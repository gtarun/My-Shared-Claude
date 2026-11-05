#!/usr/bin/env python3
"""Share local Claude Desktop Code session records; never touch login storage."""
import argparse
import base64
import csv
import datetime
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid

BASE = Path.home() / 'Library/Application Support/Claude'
ROOT = BASE / 'claude-code-sessions'
SHARED = BASE / 'shared-code-sessions'
STATE = BASE / 'codex-session-sharing.json'


def candidate_bases(platform=None, home=None, env=None):
    platform = platform or sys.platform
    home = Path.home() if home is None else home
    env = os.environ if env is None else env
    if platform == 'darwin':
        return [home / 'Library/Application Support/Claude']
    if platform == 'win32':
        roaming = Path(env.get('APPDATA', str(home / 'AppData/Roaming')))
        local = Path(env.get('LOCALAPPDATA', str(home / 'AppData/Local')))
        result = [roaming / 'Claude']
        packages = local / 'Packages'
        if packages.is_dir():
            for package in sorted(packages.iterdir()):
                if 'claude' in package.name.lower() and package.is_dir():
                    result.append(package / 'LocalCache/Roaming/Claude')
        moved = local / 'Claude-Data'
        if moved.is_dir():
            result.extend(p for p in sorted(moved.glob('claude_*')) if p.is_dir())
        return result
    if platform.startswith('linux'):
        config = Path(env.get('XDG_CONFIG_HOME', str(home / '.config')))
        return [config / 'Claude', config / 'claude-desktop', config / 'claude']
    raise SystemExit('Supported platforms: macOS, Windows, and Linux.')


def select_base(explicit=None):
    if explicit is not None:
        base = Path(explicit).expanduser().resolve()
        if not (base / 'claude-code-sessions').is_dir():
            raise SystemExit('--data-dir must name the Claude data folder containing claude-code-sessions.')
        return base
    candidates = candidate_bases()
    existing = {}
    for p in candidates:
        if (p / 'claude-code-sessions').is_dir():
            existing[os.path.normcase(str(p.resolve()))] = p
    if len(existing) > 1:
        locations = '\n'.join(str(p) for p in existing.values())
        raise SystemExit('Multiple Claude stores found. Ask your maintainer to choose one with --data-dir PATH:\n' + locations)
    return next(iter(existing.values()), candidates[0])


def is_link(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def create_directory_link(path, target):
    if sys.platform == 'win32':
        # Junctions work without Developer Mode or symlink privileges. Encode the
        # command and quote literals so paths containing shell characters stay data.
        literal = lambda p: "'" + str(p.resolve()).replace("'", "''") + "'"
        script = "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path " + literal(path) + ' -Value ' + literal(target) + ' | Out-Null'
        encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], capture_output=True, text=True)
        if result.returncode != 0:
            raise OSError('Windows could not create a directory junction. Keep Claude closed and use Undo. ' + result.stderr.strip())
    else:
        path.symlink_to(target, target_is_directory=True)
    if not is_link(path) or path.resolve() != target.resolve():
        raise OSError('The session-folder link could not be verified. Keep Claude closed and use Undo.')


def remove_directory_link(path):
    if not is_link(path):
        raise OSError('Refusing to remove an ordinary directory: ' + str(path))
    if sys.platform == 'win32' and not path.is_symlink():
        # rmdir removes the junction, not the directory it points to.
        path.rmdir()
    else:
        path.unlink()


def folders():
    if not ROOT.exists():
        return
    for account in ROOT.iterdir():
        if not account.is_dir() or is_link(account):
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
    with tmp.open('w', encoding='utf-8') as f:
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
    if sys.platform == 'win32':
        result = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq Claude.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit('Could not check whether Claude is running. No changes made.')
        running = any(row and row[0].casefold() == 'claude.exe' for row in csv.reader(result.stdout.splitlines()))
    else:
        # Include the official Linux launcher name; conservatively include the CLI.
        result = subprocess.run(['pgrep', '-u', str(os.getuid()), '-ix', 'Claude|claude-desktop'], capture_output=True, text=True)
        if result.returncode not in (0, 1):
            raise SystemExit('Could not check whether Claude is running. No changes made.')
        running = result.returncode == 0
    if running:
        raise SystemExit('Quit Claude completely using its Quit/Exit menu (Cmd+Q on Mac), then try again. On Windows, also quit the tray icon. Close Claude CLI processes too if this check still blocks setup.')


def inspect_records(new):
    chosen = {}
    for folder in new:
        for p in folder.glob('local_*.json'):
            if is_link(p) or not p.is_file():
                raise SystemExit('A session record is a symlink or special file. No changes made.')
            record = json.loads(p.read_text(encoding='utf-8'))
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
    if is_link(SHARED):
        raise SystemExit('The shared store is itself a symlink. No changes made.')
    if any(is_link(p) and p.resolve() != SHARED.resolve() for p in found):
        raise SystemExit('Unexpected existing session-directory symlink; no changes made.')
    new = [p for p in found if not is_link(p)]
    return found, new, inspect_records(new)


def plan():
    found, new, chosen = preflight()
    print(f'Found {len(found)} account/organization folders; {len(new)} need linking.')
    print(f'Found {len(chosen)} distinct session records in those folders.')
    print('Claude data folder: ' + str(BASE))
    print('Setup shares local Code session records across these accounts on this computer.')
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
    state = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'links': [], 'backups': []}
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
        create_directory_link(folder, SHARED)
    print(f'Sharing {len(list(SHARED.glob("local_*.json")))} records across {len(state["links"])} account/organization folders.')
    print(f'Original folders preserved in: {backup}')


def status():
    links = list(folders())
    if not links:
        print('Sign in to each account in Claude Desktop and open Code once to create local session storage.')
        return
    print(f'Shared local session records: {len(list(SHARED.glob("local_*.json")))}')
    print(f'Linked account/organization folders: {sum(is_link(p) and p.resolve() == SHARED.resolve() for p in links)} / {len(links)}')
    print('Authentication storage and account-hosted data are not linked.')


def undo():
    require_closed()
    if not STATE.exists():
        raise SystemExit('No installed sharing state found.')
    state = json.loads(STATE.read_text(encoding='utf-8'))
    for item in reversed(state['links']):
        path, original = Path(item['path']), Path(item['original'])
        if is_link(path) and path.resolve() == SHARED.resolve():
            remove_directory_link(path)
        if not path.exists() and original.exists():
            original.rename(path)
        elif original.exists():
            raise SystemExit(f'Refusing to overwrite an unexpected folder: {path}')
    STATE.rename(STATE.with_name('codex-session-sharing-undone-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.json'))
    print('Original account folders restored. The shared store remains intact, including any new sessions.')


def menu():
    print('Claude Desktop - Local Code Session Sharing\n')
    print('1. Set up / add accounts (default)\n2. Check status\n3. Undo sharing\n4. Exit\n')
    choice = input('Choose 1-4, then press Enter: ').strip() or '1'
    if choice == '4':
        return
    try:
        if choice == '1':
            plan()
            print('\nFinish running tasks and quit Claude completely first.')
            if input('Type SHARE to apply, or press Enter to cancel: ').strip() == 'SHARE':
                setup()
                print('Ready. Reopen Claude > Code. For folders: Group and sort > Group by > Folder.')
            else:
                print('Cancelled. No setup changes made.')
        elif choice == '2':
            status()
        elif choice == '3':
            print('Quit Claude first. Undo restores original folders; new shared sessions remain in the shared store.')
            if input('Type UNDO to restore, or press Enter to cancel: ').strip() == 'UNDO':
                undo()
            else:
                print('Cancelled.')
        else:
            print('Unknown option. Choose 1-4 next time.')
    finally:
        input('\nPress Enter to close.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'setup', 'status', 'undo', 'menu'])
    parser.add_argument('--data-dir', help='Claude data directory containing claude-code-sessions; useful for custom installs or multiple stores')
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        raise SystemExit('Python 3.9 or newer is required.')
    try:
        BASE = select_base(args.data_dir)
        ROOT = BASE / 'claude-code-sessions'
        SHARED = BASE / 'shared-code-sessions'
        STATE = BASE / 'codex-session-sharing.json'
        {'plan': plan, 'setup': setup, 'status': status, 'undo': undo, 'menu': menu}[args.command]()
    except (OSError, ValueError) as error:
        print(f'Could not complete {args.command}: {error}', file=sys.stderr)
        print('Original session folders are retained. If setup was interrupted, keep Claude closed and choose Undo in the launcher.', file=sys.stderr)
        sys.exit(1)
