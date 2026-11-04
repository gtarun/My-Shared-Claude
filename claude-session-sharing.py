#!/usr/bin/env python3
"""Share local Claude Desktop Code session records; never touch login storage."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

BASE = Path.home() / 'Library/Application Support/Claude'
ROOT = BASE / 'claude-code-sessions'
SHARED = BASE / 'shared-code-sessions'
STATE = BASE / 'codex-session-sharing.json'


def folders():
    if not ROOT.exists():
        return
    for account in ROOT.iterdir():
        if not account.is_dir() or account.is_symlink():
            continue
        try:
            uuid.UUID(account.name)
        except ValueError:
            continue
        for org in account.iterdir():
            try:
                uuid.UUID(org.name)
            except ValueError:
                continue
            if org.is_dir():
                yield org


def save(path, data):
    tmp = path.with_name(path.name + '.sharing-tmp')
    with tmp.open('w') as f:
        os.chmod(tmp, 0o600)
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def clean(record):
    # Remote session IDs and credentials belong to their original account.
    result = dict(record)
    for key in list(result):
        if key.startswith(('remoteControl', 'bridge', 'steeredByRemote')) or key in {
            'remoteMcpServersConfig', 'interruptedAwaitingPerson',
            'interruptedByQuitAt', 'remoteControlLiveAtUpdateQuit',
        }:
            result.pop(key, None)
    result['remoteControlAutoEligible'] = False
    return result


def require_closed():
    if subprocess.run(['pgrep', '-x', 'Claude'], capture_output=True).returncode == 0:
        raise SystemExit('Quit Claude completely with Cmd+Q, then run this command again.')


def inspect_records(new):
    chosen = {}
    for folder in new:
        for p in folder.glob('local_*.json'):
            if p.is_symlink() or not p.is_file():
                raise SystemExit('A session record is a symlink or special file. No changes made.')
            record = json.loads(p.read_text())
            if not isinstance(record, dict) or record.get('sessionId') != p.stem:
                raise SystemExit('Unexpected session record; stopped before linking folders.')
            try:
                uuid.UUID(p.stem.removeprefix('local_'))
            except ValueError:
                raise SystemExit('Unexpected session ID. No changes made.')
            if p.name not in chosen or p.stat().st_mtime_ns > chosen[p.name][0]:
                chosen[p.name] = (p.stat().st_mtime_ns, record)
    return chosen


def preflight():
    found = list(folders())
    if not found:
        raise SystemExit('Sign in to each account in Claude Desktop and open Code once, then quit Claude and try again.')
    if SHARED.is_symlink():
        raise SystemExit('The shared store is itself a symlink. No changes made.')
    if any(p.is_symlink() and p.resolve() != SHARED.resolve() for p in found):
        raise SystemExit('Unexpected existing session-directory symlink; no changes made.')
    new = [p for p in found if not p.is_symlink()]
    return found, new, inspect_records(new)


def plan():
    found, new, chosen = preflight()
    print(f'Found {len(found)} account/organization folders; {len(new)} need linking.')
    print(f'Found {len(chosen)} distinct session records in those folders.')
    print('Setup shares local Code session records across these accounts on this Mac.')
    print('Original folders are backed up. Account-bound Remote Control and remote MCP references are removed from newly imported copies.')
    print('Logins, cloud chats, Cowork, saved environments, sidebar preferences and connector authentication are not shared.')
    print('Shared local Code configuration continues using its existing files.')
    print('Preview only: no files changed.')


def setup():
    require_closed()
    found, new, chosen = preflight()
    if not new:
        print('All existing account/organization folders already share sessions.')
        return
    state = json.loads(STATE.read_text()) if STATE.exists() else {'links': [], 'backups': []}
    SHARED.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = BASE / 'codex-session-sharing-backups' / stamp
    backup.mkdir(parents=True, mode=0o700)
    if any(SHARED.iterdir()):
        shutil.copytree(SHARED, backup / 'shared-before', symlinks=True)
    for name, (_, record) in chosen.items():
        # On subsequent setup runs the live shared record is authoritative.
        if not (SHARED / name).exists():
            save(SHARED / name, clean(record))
    state['backups'].append(str(backup))
    save(STATE, state)
    for folder in new:
        original = backup / folder.parent.name / folder.name
        original.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        entry = {'path': str(folder), 'original': str(original)}
        # Journal before moving; undo handles an interrupted setup as well.
        state['links'].append(entry)
        save(STATE, state)
        folder.rename(original)
        folder.symlink_to(SHARED, target_is_directory=True)
    print(f'Sharing {len(list(SHARED.glob("local_*.json")))} records across {len(state["links"])} account/organization folders.')
    print(f'Original folders preserved in: {backup}')


def status():
    links = list(folders())
    if not links:
        print('Sign in to each account in Claude Desktop and open Code once to create local session storage.')
        return
    print(f'Shared local session records: {len(list(SHARED.glob("local_*.json")))}')
    print(f'Linked account/organization folders: {sum(p.is_symlink() and p.resolve() == SHARED.resolve() for p in links)} / {len(links)}')
    print('Authentication storage and account-hosted data are not linked.')


def undo():
    require_closed()
    if not STATE.exists():
        raise SystemExit('No installed sharing state found.')
    state = json.loads(STATE.read_text())
    for item in reversed(state['links']):
        path, original = Path(item['path']), Path(item['original'])
        if path.is_symlink() and path.resolve() == SHARED.resolve():
            path.unlink()
        if not path.exists() and original.exists():
            original.rename(path)
        elif original.exists():
            raise SystemExit(f'Refusing to overwrite an unexpected folder: {path}')
    STATE.rename(STATE.with_name('codex-session-sharing-undone-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'))
    print('Original account folders restored. The shared store remains intact, including any new sessions.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'setup', 'status', 'undo'])
    args = parser.parse_args()
    if sys.platform != 'darwin':
        raise SystemExit('This package supports macOS only.')
    if sys.version_info < (3, 9):
        raise SystemExit('Python 3.9 or newer is required.')
    try:
        {'plan': plan, 'setup': setup, 'status': status, 'undo': undo}[args.command]()
    except (OSError, ValueError) as error:
        print(f'Could not complete {args.command}: {error}', file=sys.stderr)
        print('Original session folders are retained. If setup was interrupted, keep Claude closed and choose Undo in the launcher.', file=sys.stderr)
        sys.exit(1)
