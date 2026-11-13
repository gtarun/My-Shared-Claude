#!/usr/bin/env python3
"""Synchronize local Claude Desktop Code records while the app is closed; never link account folders."""
import argparse
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


def inspect_records(sources):
    chosen = {}
    for folder in sources:
        for p in sorted(folder.glob('local_*.json')):
            if is_link(p) or not p.is_file():
                raise SystemExit('A session record is a link or special file. No changes made.')
            record = json.loads(p.read_text(encoding='utf-8'))
            if not isinstance(record, dict) or record.get('sessionId') != p.stem:
                raise SystemExit('Unexpected session record. No changes made.')
            uuid.UUID(p.stem.removeprefix('local_'))
            candidate = (p.stat().st_mtime_ns, record, p)
            if p.name not in chosen or candidate[0] > chosen[p.name][0]:
                chosen[p.name] = candidate
    return chosen


def preflight():
    found = sorted(folders())
    if not found:
        raise SystemExit('Sign in to each account in Claude Desktop and open Code once, then quit Claude and try again.')
    if is_link(SHARED):
        raise SystemExit('The shared archive is itself a link. No changes made.')
    if any(is_link(p) and p.resolve() != SHARED.resolve() for p in found):
        raise SystemExit('An account folder points to an unknown link target. No changes made.')
    state = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {}
    if state.get('mode') == 'offline-copy-v2' and state.get('phase') not in ('complete', 'undone'):
        raise SystemExit('An earlier sync was interrupted. Keep Claude closed and run Undo first.')
    # Prefer native account records on equal timestamps; the archive is a fallback.
    sources = found + ([SHARED] if SHARED.is_dir() else [])
    return found, inspect_records(sources)


def plan():
    found, chosen = preflight()
    print('Claude data folder: ' + str(BASE))
    print(f'Found {len(found)} account/organization folders and {len(chosen)} distinct session records.')
    print(f'Legacy linked folders to repair: {sum(is_link(p) for p in found)}')
    print('Sync copies records into NORMAL account folders. No links are created.')
    print('Run sync with Claude fully closed before switching accounts; this is not automatic live sharing.')
    print('Each run backs up the account folders and archive. Logins and cloud data stay separate.')
    print('Preview only: no files changed.')


def relative_folder(path):
    relative = path.relative_to(ROOT)
    if len(relative.parts) != 2:
        raise ValueError('Unexpected account folder')
    for part in relative.parts:
        uuid.UUID(part)
    return relative.as_posix()


def make_backup(found):
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = BASE / 'codex-session-sharing-backups' / ('offline-' + stamp)
    backup.mkdir(parents=True, mode=0o700)
    entries = []
    for folder in found:
        relative = relative_folder(folder)
        destination = backup / 'accounts' / relative
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # copytree materializes the source root even when that root is a legacy
        # link. Never recreate a linked account folder, including during undo.
        shutil.copytree(folder, destination, symlinks=True)
        destination.chmod(0o700)
        entries.append(relative)
    had_shared = SHARED.exists()
    if had_shared:
        shutil.copytree(SHARED, backup / 'shared-before', symlinks=True)
    if STATE.exists():
        shutil.copy2(STATE, backup / 'state-before.json')
    save(backup / 'manifest.json', {'folders': entries, 'had_shared': had_shared})
    return backup, entries


def replace_folder(folder, stage, retired):
    if is_link(folder):
        remove_directory_link(folder)
    elif folder.exists():
        retired.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        folder.rename(retired)
    stage.rename(folder)


def portable_equal(first, second):
    return clean(first) == clean(second)


def sync_records(extra=None, transcripts=None):
    require_closed()
    found, chosen = preflight()
    for record, modified in extra or []:
        chosen[record['sessionId'] + '.json'] = (modified, record, None)
    backup, entries = make_backup(found)
    for source in transcripts or []:
        destination = backup / 'transcripts' / source.name
        destination.parent.mkdir(exist_ok=True, mode=0o700)
        shutil.copy2(source, destination)
        destination.chmod(0o600)
    state = {'mode': 'offline-copy-v2', 'phase': 'pending', 'last_backup': backup.name}
    save(STATE, state)
    stages = []
    for folder in found:
        stage = folder.parent / ('.session-sync-' + uuid.uuid4().hex)
        shutil.copytree(folder, stage, symlinks=True)
        stage.chmod(0o700)
        for name, (modified, record, _) in chosen.items():
            destination = stage / name
            current = json.loads(destination.read_text(encoding='utf-8')) if destination.exists() else None
            if current is not None and portable_equal(current, record):
                continue  # Keep this account's own connector settings intact.
            save(destination, clean(record))
            os.utime(destination, ns=(modified, modified))
        stages.append((folder, stage))
    require_closed()
    for folder, stage in stages:
        replace_folder(folder, stage, backup / 'replaced' / relative_folder(folder))
    SHARED.mkdir(mode=0o700, exist_ok=True)
    for name, (modified, record, _) in chosen.items():
        destination = SHARED / name
        save(destination, clean(record))
        os.utime(destination, ns=(modified, modified))
    state.update(phase='complete', folders=entries, synced_at=datetime.datetime.now().isoformat())
    save(STATE, state)
    print(f'Synced {len(chosen)} records into {len(found)} normal account/organization folders.')
    print('Backup: ' + str(backup))
    print('Reopen Claude. Quit and run Sync again before the next account switch.')


def setup():
    # Backward-compatible command name; all old folder-linking behavior is gone.
    sync_records()


def status():
    found = list(folders())
    if not found:
        print('Sign in to each account in Claude Desktop and open Code once to create local session storage.')
        return
    linked = sum(is_link(p) for p in found)
    print(f'Account/organization folders: {len(found)}; normal: {len(found) - linked}; legacy linked: {linked}')
    print(f'Archive records: {len(list(SHARED.glob("local_*.json")))}')
    print('Legacy links can prevent Claude from saving. Run Sync/repair while Claude is closed.' if linked else 'Offline copy sync: run Sync while Claude is closed before switching accounts.')
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding='utf-8'))
        if state.get('mode') == 'offline-copy-v2':
            print('Last operation: ' + state.get('phase', 'unknown'))
            print('Last sync: ' + state.get('synced_at', 'not completed'))
    print('Authentication storage and account-hosted data are not synchronized.')


def undo():
    require_closed()
    if not STATE.exists():
        raise SystemExit('No sync journal found.')
    state = json.loads(STATE.read_text(encoding='utf-8'))
    if state.get('mode') != 'offline-copy-v2':
        raise SystemExit('Legacy linked setup detected. Choose Sync/repair first; old links must not be restored.')
    name = state.get('last_backup')
    if not name or Path(name).name != name or not name.startswith('offline-'):
        raise SystemExit('No valid last-sync backup to restore.')
    backup = BASE / 'codex-session-sharing-backups' / name
    manifest = json.loads((backup / 'manifest.json').read_text(encoding='utf-8'))
    targets = []
    for relative in manifest['folders']:
        folder = ROOT / relative
        if relative_folder(folder) != relative:
            raise ValueError('Invalid backup folder')
        snapshot = backup / 'accounts' / relative
        if not snapshot.is_dir() or is_link(snapshot):
            raise SystemExit('Backup account snapshot is missing or linked. Nothing restored.')
        if is_link(folder) and folder.resolve() != SHARED.resolve():
            raise SystemExit('Unknown account-folder link. Nothing restored.')
        targets.append((folder, snapshot))
    preserved, _ = make_backup([p for p, _ in targets if p.exists()])
    stages = []
    for folder, snapshot in targets:
        stage = folder.parent / ('.session-sync-' + uuid.uuid4().hex)
        shutil.copytree(snapshot, stage, symlinks=True)
        stage.chmod(0o700)
        stages.append((folder, stage))
    for folder, stage in stages:
        replace_folder(folder, stage, preserved / 'replaced' / relative_folder(folder))
    if SHARED.exists():
        SHARED.rename(preserved / 'archive-at-undo')
    if manifest['had_shared']:
        shutil.copytree(backup / 'shared-before', SHARED, symlinks=True)
    save(STATE, {'mode': 'offline-copy-v2', 'phase': 'undone', 'last_backup': None, 'preserved_at_undo': preserved.name})
    print('Restored the account folders to their pre-sync snapshots. All folders remain normal directories.')
    print('Changes made after that sync remain preserved in: ' + str(preserved))
    print('Original transcripts were not changed. Undo does not reintroduce links.')


def transcript_record(path):
    uuid.UUID(path.stem)
    if path.suffix != '.jsonl' or is_link(path) or not path.is_file():
        raise SystemExit('Recovery requires an ordinary .jsonl transcript file.')
    metadata = {}; stamps = []; turns = 0
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            try:
                value = json.loads(line)
            except ValueError:
                continue  # A trailing partial record need not hide earlier history.
            if not isinstance(value, dict):
                continue
            for key in ('cwd', 'customTitle'):
                if value.get(key):
                    metadata[key] = value[key]
            if value.get('timestamp'):
                try:
                    stamps.append(int(datetime.datetime.fromisoformat(value['timestamp'].replace('Z', '+00:00')).timestamp() * 1000))
                except (ValueError, TypeError):
                    pass
            if value.get('type') == 'user':
                turns += 1
    cwd = metadata.get('cwd')
    if not cwd or not stamps or not turns:
        raise SystemExit('Transcript has insufficient session metadata; nothing recovered.')
    record = {'sessionId': 'local_' + path.stem, 'cliSessionId': path.stem,
              'cwd': cwd, 'originCwd': cwd, 'title': metadata.get('customTitle', 'Recovered ' + path.stem[:8]),
              'createdAt': min(stamps), 'lastActivityAt': max(stamps), 'lastFocusedAt': max(stamps),
              'isArchived': False, 'completedTurns': turns, 'permissionMode': 'default',
              'enabledMcpTools': [], 'alwaysAllowedReasons': [], 'sessionPermissionUpdates': [],
              'remoteControlAutoEligible': False}
    parts = Path(cwd).parts
    for index in range(len(parts) - 1):
        if parts[index:index + 2] == ('.claude', 'worktrees'):
            record['originCwd'] = str(Path(*parts[:index]))
            record['worktreePath'] = cwd
            break
    return record


def recover_transcripts(paths):
    require_closed()
    _, chosen = preflight()
    known = {record.get('cliSessionId') for _, record, _ in chosen.values()}
    recovered = []
    sources = []
    for value in paths:
        path = Path(value).expanduser()
        if path.stem in known:
            print('Already indexed: ' + path.stem)
            continue
        record = transcript_record(path)
        recovered.append((record, path.stat().st_mtime_ns))
        sources.append(path)
        known.add(path.stem)
    if recovered:
        sync_records(recovered, sources)
        print(f'Rebuilt {len(recovered)} missing sidebar entries from existing transcripts; no messages were changed.')
    else:
        print('No missing session entries to recover.')


def menu():
    print('Claude Desktop - Offline Code Session Sync\n')
    print('1. Sync / repair old setup (default)\n2. Check status\n3. Undo last sync\n4. Exit\n')
    choice = input('Choose 1-4, then press Enter: ').strip() or '1'
    if choice == '4':
        return
    try:
        if choice == '1':
            plan()
            print('\nFinish tasks and quit Claude completely. Sync is required again before future account switches.')
            if input('Type SYNC to apply, or press Enter to cancel: ').strip() == 'SYNC':
                setup()
            else:
                print('Cancelled. No changes made.')
        elif choice == '2':
            status()
        elif choice == '3':
            print('Quit Claude first. Undo preserves current data in another backup; it never restores folder links.')
            if input('Type UNDO to restore the last pre-sync snapshot: ').strip() == 'UNDO':
                undo()
        else:
            print('Unknown option. Choose 1-4 next time.')
    finally:
        input('\nPress Enter to close.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'sync', 'setup', 'status', 'undo', 'menu', 'recover'])
    parser.add_argument('--data-dir', help='Claude data directory containing claude-code-sessions; useful for custom installs or multiple stores')
    parser.add_argument('--transcript', action='append', default=[], help='Explicit .jsonl file to recover; repeat for multiple files')
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        raise SystemExit('Python 3.9 or newer is required.')
    try:
        BASE = select_base(args.data_dir)
        ROOT = BASE / 'claude-code-sessions'
        SHARED = BASE / 'shared-code-sessions'
        STATE = BASE / 'codex-session-sharing.json'
        {'plan': plan, 'sync': setup, 'setup': setup, 'status': status, 'undo': undo, 'menu': menu, 'recover': lambda: recover_transcripts(args.transcript)}[args.command]()
    except (OSError, ValueError) as error:
        print(f'Could not complete {args.command}: {error}', file=sys.stderr)
        print('Original session folders are retained. If setup was interrupted, keep Claude closed and choose Undo in the launcher.', file=sys.stderr)
        sys.exit(1)
