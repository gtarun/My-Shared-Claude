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

class AutoSyncTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('sharing_auto', SCRIPT)
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

    def watcher(self):
        self.assertTrue(callable(getattr(self.m, 'ExitWatcher', None)), 'Exit watcher is missing')
        return self.m.ExitWatcher(settle_seconds=5, retry_seconds=30)

    def test_no_sync_while_running_or_before_quiet_period(self):
        watcher = self.watcher()
        self.assertEqual(watcher.observe(True, 0), 'running')
        self.assertEqual(watcher.observe(False, 10), 'settling')
        self.assertEqual(watcher.observe(False, 14), 'settling')
        self.assertEqual(watcher.observe(False, 15), 'sync')

    def test_reopening_defers_sync_until_next_quit(self):
        watcher = self.watcher()
        watcher.observe(True, 0)
        watcher.observe(False, 10)
        self.assertEqual(watcher.observe(True, 12), 'running')
        self.assertEqual(watcher.observe(True, 100), 'running')
        self.assertEqual(watcher.observe(False, 101), 'settling')
        self.assertEqual(watcher.observe(False, 106), 'sync')

    def test_success_runs_once_until_app_runs_again(self):
        watcher = self.watcher()
        watcher.observe(False, 0)
        self.assertEqual(watcher.observe(False, 5), 'sync')
        watcher.complete(True, 5)
        self.assertEqual(watcher.observe(False, 100), 'idle')
        watcher.observe(True, 101)
        watcher.observe(False, 102)
        self.assertEqual(watcher.observe(False, 107), 'sync')

    def test_failure_is_retried_after_backoff(self):
        watcher = self.watcher()
        watcher.observe(False, 0)
        watcher.observe(False, 5)
        watcher.complete(False, 5)
        self.assertEqual(watcher.observe(False, 20), 'retry')
        self.assertEqual(watcher.observe(False, 35), 'sync')

    def test_operation_lock_blocks_a_second_writer_and_releases_after_error(self):
        self.assertTrue(callable(getattr(self.m, 'operation_lock', None)), 'Operation lock is missing')
        self.m.BASE.mkdir()
        with self.m.operation_lock():
            with self.assertRaises(self.m.SyncBusyError):
                with self.m.operation_lock():
                    self.fail('Two writers acquired the lock')
        try:
            with self.m.operation_lock():
                raise ValueError('interrupted')
        except ValueError:
            pass
        with self.m.operation_lock():
            pass

    def test_unchanged_records_do_not_generate_another_backup(self):
        self.assertTrue(callable(getattr(self.m, 'sync_if_needed', None)), 'Change detection is missing')
        a = self.folder()
        self.record(a)
        self.m.setup()
        before = list((self.m.BASE / 'codex-session-sharing-backups').iterdir())
        self.assertFalse(self.m.sync_if_needed())
        self.assertEqual(list((self.m.BASE / 'codex-session-sharing-backups').iterdir()), before)

    def folder(self):
        path = self.m.ROOT / str(uuid.uuid4()) / str(uuid.uuid4())
        path.mkdir(parents=True)
        return path

    def record(self, folder):
        record = {'sessionId': 'local_' + str(uuid.uuid4()), 'title': 'New work'}
        path = folder / (record['sessionId'] + '.json')
        path.write_text(json.dumps(record))
        return path

    def test_exit_trigger_copies_real_records_to_other_normal_folders(self):
        watcher = self.watcher()
        a, b = self.folder(), self.folder()
        self.record(a)
        self.m.setup()
        new = self.record(a)
        watcher.observe(True, 0)
        watcher.observe(False, 10)
        self.assertFalse((b / new.name).exists())
        self.assertEqual(watcher.observe(False, 15), 'sync')
        self.assertTrue(self.m.sync_if_needed())
        watcher.complete(True, 15)
        self.assertTrue((b / new.name).exists())
        self.assertFalse(self.m.is_link(a))
        self.assertFalse(self.m.is_link(b))

    def test_reopening_before_commit_leaves_original_folders_and_no_pending_journal(self):
        a, b = self.folder(), self.folder()
        source = self.record(a)
        with patch.object(self.m, 'require_closed', side_effect=[None, SystemExit('Claude reopened')]):
            with self.assertRaises(SystemExit):
                self.m.setup()
        self.assertTrue(source.exists())
        self.assertFalse((b / source.name).exists())
        self.assertFalse(self.m.STATE.exists())
        self.assertFalse(list(self.m.ROOT.glob('*/.session-sync-*')))

    def test_auto_install_refuses_non_mac_without_touching_runtime(self):
        self.assertTrue(callable(getattr(self.m, 'install_autosync', None)), 'Auto-install command is missing')
        with patch.object(self.m.sys, 'platform', 'win32'):
            with self.assertRaises(SystemExit):
                self.m.install_autosync()
        self.assertFalse(self.m.BASE.exists())

if __name__ == '__main__':
    unittest.main()
