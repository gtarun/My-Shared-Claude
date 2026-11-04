import contextlib
import importlib.util
import io
import json
import tempfile
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
        self.assertFalse(a.is_symlink())
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
        original.symlink_to(outside)
        with self.assertRaises(SystemExit):
            self.m.setup()
        self.assertFalse(self.m.SHARED.exists())
        self.assertTrue(a.is_dir())
        self.assertFalse(a.is_symlink())

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
        self.assertFalse(a.is_symlink())
        self.assertEqual(len(list(a.glob('local_*.json'))), 1)
        self.assertTrue((self.m.SHARED / new.name).exists())
        self.assertFalse(self.m.STATE.exists())

    def test_interrupted_link_creation_can_be_undone(self):
        a = self.folder()
        source = self.record(a)
        with patch.object(Path, 'symlink_to', side_effect=OSError('simulated interruption')):
            with self.assertRaises(OSError):
                self.m.setup()
        self.m.undo()
        self.assertTrue(source.exists())
        self.assertFalse(a.is_symlink())

if __name__ == '__main__':
    unittest.main()
