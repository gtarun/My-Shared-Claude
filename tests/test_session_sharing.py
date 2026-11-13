import contextlib
import os
import base64
import importlib.util
import io
import json
import tempfile
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'claude-session-sharing.py'


def create_legacy_link(path, target):
    if sys.platform == 'win32':
        quote = lambda p: "'" + str(p).replace("'", "''") + "'"
        code = "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path " + quote(path) + ' -Value ' + quote(target) + ' | Out-Null'
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', base64.b64encode(code.encode('utf-16-le')).decode()], check=True, capture_output=True)
    else:
        path.symlink_to(target, target_is_directory=True)

class SharingTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('sharing', SCRIPT)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.m.BASE = Path(self.temp.name) / 'Claude'
        self.m.ROOT = self.m.BASE / 'claude-code-sessions'
        self.m.SHARED = self.m.BASE / 'shared-code-sessions'
        self.m.STATE = self.m.BASE / 'codex-session-sharing.json'
        self.m.require_closed = lambda: None
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def folder(self):
        p = self.m.ROOT / str(uuid.uuid4()) / str(uuid.uuid4())
        p.mkdir(parents=True)
        return p

    def record(self, folder, **extra):
        d = {'sessionId': 'local_' + str(uuid.uuid4()), 'title': 'Example'}
        d.update(extra)
        p = folder / (d['sessionId'] + '.json')
        p.write_text(json.dumps(d))
        return p

    def test_plan_is_read_only_and_reports_folders(self):
        a, b = self.folder(), self.folder()
        self.record(a)
        self.record(b)
        self.assertTrue(callable(getattr(self.m, 'plan', None)), 'Read-only preview is missing')
        self.m.plan()
        self.assertFalse(self.m.SHARED.exists())
        self.assertFalse(self.m.STATE.exists())
        self.assertFalse(self.m.is_link(a))
        self.assertIn('2', self.output.getvalue())

    def test_missing_install_has_helpful_message(self):
        try:
            self.m.status()
        except FileNotFoundError:
            self.fail('Status crashes when Claude has not created session storage')
        self.assertIn('Sign in', self.output.getvalue())

    def test_record_symlinks_are_rejected_before_changes(self):
        a = self.folder()
        original = self.record(a)
        outside = self.m.BASE / 'outside.json'
        original.rename(outside)
        try:
            original.symlink_to(outside)
        except OSError as error:
            if __import__('sys').platform == 'win32':
                self.skipTest('File symlinks unavailable without Windows symlink privileges: ' + str(error))
            raise
        with self.assertRaises(SystemExit):
            self.m.setup()
        self.assertFalse(self.m.SHARED.exists())
        self.assertTrue(a.is_dir())
        self.assertFalse(self.m.is_link(a))

    def test_sync_keeps_native_directories_and_copies_only_when_run(self):
        a, b = self.folder(), self.folder()
        original = self.record(a, bridgeSessionIds=['old-account'])
        self.record(b)
        self.m.setup()
        self.assertFalse(self.m.is_link(a))
        self.assertFalse(self.m.is_link(b))
        self.assertNotEqual(a.resolve(), b.resolve())
        if hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY'):
            for folder in [a, b]:
                fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                os.close(fd)
        self.assertNotIn('bridgeSessionIds', json.loads((b / original.name).read_text()))
        new = self.record(a)
        self.assertFalse((b / new.name).exists())
        self.m.setup()
        self.assertTrue((b / new.name).exists())
        self.assertEqual(len(list(b.glob('local_*.json'))), 3)

    def test_sync_picks_newest_native_edit_and_preserves_source_credentials(self):
        a, b = self.folder(), self.folder()
        source = self.record(a, remoteMcpServersConfig=['keep-on-origin'])
        self.m.setup()
        data = json.loads(source.read_text())
        data['title'] = 'Updated in Claude'
        replacement = source.with_suffix('.new')
        replacement.write_text(json.dumps(data))
        os.replace(replacement, source)
        os.utime(source, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns + 1000000000))
        self.m.setup()
        self.assertEqual(json.loads((b / source.name).read_text())['title'], 'Updated in Claude')
        self.assertEqual(json.loads(source.read_text())['remoteMcpServersConfig'], ['keep-on-origin'])

    def test_legacy_link_is_materialized_and_undo_never_recreates_it(self):
        a, b = self.folder(), self.folder()
        self.m.SHARED.mkdir()
        saved = self.record(self.m.SHARED)
        a.rmdir()
        create_legacy_link(a, self.m.SHARED)
        self.m.setup()
        self.assertFalse(self.m.is_link(a))
        self.assertTrue((a / saved.name).exists())
        self.assertTrue((b / saved.name).exists())
        self.m.undo()
        self.assertFalse(self.m.is_link(a))
        self.assertTrue((a / saved.name).exists())
        self.assertTrue(saved.exists())

    def test_failed_sync_is_recoverable_without_losing_user_records(self):
        a, b = self.folder(), self.folder()
        source = self.record(a)
        self.record(b)
        with patch.object(self.m, 'replace_folder', side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError):
                self.m.setup()
        self.m.undo()
        self.assertTrue(source.exists())
        self.assertFalse(self.m.is_link(a))

    def test_undo_preserves_changes_made_after_sync_in_backup(self):
        a, b = self.folder(), self.folder()
        self.record(a)
        self.m.setup()
        new = self.record(a)
        self.m.undo()
        self.assertFalse(self.m.is_link(a))
        self.assertTrue(any(p.name == new.name for p in (self.m.BASE / 'codex-session-sharing-backups').rglob(new.name)))

    def test_recovery_reads_transcript_metadata_without_modifying_messages(self):
        a = self.folder()
        self.record(a)
        transcript = Path(self.temp.name) / (str(uuid.uuid4()) + '.jsonl')
        content = '\n'.join(json.dumps(d) for d in [
            {'type': 'user', 'cwd': str(Path(self.temp.name)), 'timestamp': '2026-11-12T08:00:00Z', 'message': {'content': 'private'}},
            {'type': 'custom-title', 'customTitle': 'Recovered design'},
            {'type': 'assistant', 'timestamp': '2026-11-12T09:00:00Z', 'message': {'content': 'private response'}},
        ]) + '\n'
        transcript.write_text(content)
        self.assertTrue(callable(getattr(self.m, 'recover_transcripts', None)), 'Transcript recovery is missing')
        self.m.recover_transcripts([transcript])
        files = list(a.glob('local_*.json'))
        recovered = [json.loads(p.read_text()) for p in files if json.loads(p.read_text()).get('cliSessionId') == transcript.stem]
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0]['title'], 'Recovered design')
        self.assertEqual(transcript.read_text(), content)
        self.assertEqual(recovered[0]['permissionMode'], 'default')

class PlatformTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('platform_sharing', SCRIPT)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def test_linux_uses_xdg_config_directory(self):
        self.assertTrue(callable(getattr(self.m, 'candidate_bases', None)), 'Platform discovery is missing')
        candidates = self.m.candidate_bases('linux', self.home, {'XDG_CONFIG_HOME': str(self.home / 'custom')})
        self.assertIn(self.home / 'custom' / 'Claude', candidates)

    def test_windows_discovers_packaged_store(self):
        self.assertTrue(callable(getattr(self.m, 'candidate_bases', None)), 'Platform discovery is missing')
        local = self.home / 'Local'
        packaged = local / 'Packages' / 'Claude_example' / 'LocalCache/Roaming/Claude'
        (packaged / 'claude-code-sessions').mkdir(parents=True)
        candidates = self.m.candidate_bases('win32', self.home, {'LOCALAPPDATA': str(local), 'APPDATA': str(self.home / 'Roaming')})
        self.assertIn(packaged, candidates)

    def test_ambiguous_stores_require_explicit_selection(self):
        self.assertTrue(callable(getattr(self.m, 'select_base', None)), 'Store selection is missing')
        first, second = self.home / 'first', self.home / 'second'
        for p in [first, second]:
            (p / 'claude-code-sessions').mkdir(parents=True)
        with patch.object(self.m, 'candidate_bases', return_value=[first, second]):
            with self.assertRaisesRegex(SystemExit, 'data-dir'):
                self.m.select_base()
        self.assertEqual(self.m.select_base(first), first.resolve())

    def test_windows_running_app_blocks_changes(self):
        with patch.object(self.m.sys, 'platform', 'win32'), patch.object(self.m.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '"Claude.exe","123","Console","1","10,000 K"\n', '')):
            with self.assertRaises(SystemExit):
                self.m.require_closed()

    def test_failed_process_check_blocks_changes(self):
        with patch.object(self.m.sys, 'platform', 'linux'), patch.object(self.m.os, 'getuid', return_value=123, create=True), patch.object(self.m.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2, '', 'cannot enumerate processes')):
            with self.assertRaises(SystemExit):
                self.m.require_closed()

class LauncherTests(unittest.TestCase):
    def test_native_launcher_can_exit_without_installing(self):
        repo = SCRIPT.parent
        if sys.platform == 'win32':
            command = ['cmd.exe', '/d', '/c', str(repo / 'Claude Session Sharing.cmd')]
        elif sys.platform.startswith('linux'):
            command = ['bash', str(repo / 'Claude Session Sharing.sh')]
        else:
            command = ['zsh', str(repo / 'Claude Session Sharing.command')]
        result = subprocess.run(command, input='4\n', capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Sync / repair old setup', result.stdout)

if __name__ == '__main__':
    unittest.main()
