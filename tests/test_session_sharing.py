import contextlib
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

    def test_merge_live_writes_enroll_and_rollback(self):
        a, b = self.folder(), self.folder()
        original = self.record(a, bridgeSessionIds=['account-bound'], remoteMcpServersConfig=['account-bound'])
        self.record(b)
        self.m.setup()
        self.assertEqual(len(list(self.m.SHARED.glob('local_*.json'))), 2)
        d = json.loads((a / original.name).read_text())
        self.assertNotIn('bridgeSessionIds', d)
        self.assertNotIn('remoteMcpServersConfig', d)
        self.assertEqual(a.resolve(), b.resolve())
        new = self.record(a)
        self.assertTrue((b / new.name).exists())
        c = self.folder()
        self.record(c)
        self.m.setup()
        self.assertEqual(c.resolve(), a.resolve())
        self.assertEqual(len(list(self.m.SHARED.glob('local_*.json'))), 4)
        self.m.setup()  # idempotent
        self.m.undo()
        self.assertFalse(self.m.is_link(a))
        self.assertEqual(len(list(a.glob('local_*.json'))), 1)
        self.assertTrue((self.m.SHARED / new.name).exists())
        self.assertFalse(self.m.STATE.exists())

    def test_interrupted_link_creation_can_be_undone(self):
        a = self.folder()
        source = self.record(a)
        with patch.object(self.m, 'create_directory_link', side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError):
                self.m.setup()
        self.m.undo()
        self.assertTrue(source.exists())
        self.assertFalse(self.m.is_link(a))

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

    def test_directory_link_writes_and_removal_preserve_target(self):
        self.assertTrue(callable(getattr(self.m, 'create_directory_link', None)), 'Portable linking is missing')
        target, link = self.home / 'target', self.home / 'link'
        target.mkdir()
        self.m.create_directory_link(link, target)
        self.assertTrue(self.m.is_link(link))
        (link / 'retained.txt').write_text('keep')
        self.m.remove_directory_link(link)
        self.assertFalse(link.exists())
        self.assertEqual((target / 'retained.txt').read_text(), 'keep')

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
        self.assertIn('Set up / add accounts', result.stdout)

if __name__ == '__main__':
    unittest.main()
