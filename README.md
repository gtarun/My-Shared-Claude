# My Shared Claude

**Copy local Claude Code session lists between your own accounts on one computer, while Claude Desktop is closed.**

> **Important repair for earlier versions:** the original folder-linking approach allowed history to open but could prevent Claude Desktop from saving new session records. Do not keep using that version. Download the current files, fully quit Claude, and choose **Sync / repair old setup**. The repair replaces recognized old links with normal folders and preserves backups. Missing sidebar entries may need separate transcript recovery; instructions are below.

## Start here — quick setup

**Requires Python 3.9+. Use the launcher for your computer:**

| Computer | Launcher | Open it this way |
| --- | --- | --- |
| Mac | `Claude Session Sharing.command` | Double-click in Finder. |
| Windows | `Claude Session Sharing.cmd` | Extract the ZIP, then double-click the `.cmd` file. |
| Linux | `Claude Session Sharing.sh` | Open a terminal in the extracted folder and run `bash "./Claude Session Sharing.sh"`. |

1. **Download:** [Download the latest ZIP](https://github.com/gtarun/My-Shared-Claude/releases/latest/download/My-Shared-Claude.zip). Extract it and keep the launcher and Python helper together. Replace any older downloaded copies.
2. **Open your accounts once:** in Claude Desktop, sign into each account/organization you want included and open **Code** once in each. This creates its local folder; you do not need to send a message.
3. **Quit Claude completely:** finish running tasks, then use **Quit/Exit**. On Mac, press **Command + Q**. On Windows, also exit Claude’s system-tray icon if it is still running.
4. **Run the matching launcher:** press **Enter** for **Sync / repair old setup**. Read the preview, type **SYNC**, and press Enter.
5. **Reopen Claude → Code:** older local sessions should be listed. Open a familiar one to check its history.
6. **For project folders:** choose **Group and sort → Group by → Folder** once in each account/organization.

**Before every later account switch: finish work → quit Claude → run Sync → reopen Claude → switch accounts.** This version copies files; it does not keep accounts synchronized while Claude is running.

The tool combines all detected local Code account folders in one native Desktop data directory on this computer. It does not copy conversations to teammates’ computers or merge cloud accounts. If Python is missing, install it from [python.org](https://www.python.org/downloads/) or ask IT. See [Troubleshooting](#troubleshooting) for help.

## What changed, and why?

The original version pointed several account folders at one shared directory using symbolic links or Windows junctions. An operating-system link test passed, and existing conversations could be read, but Claude Desktop’s private-directory safeguards could reject writes through those links. This left some newer conversations with transcripts on disk but no saved sidebar entry.

The current version creates **no account-folder links**. Each account has a normal, independent directory that Claude can write to. The tool copies session records between those directories only when Claude is fully closed. It does not patch Claude, disable its safeguards, or install a background service.

On first use after the old version, Sync also repairs recognized linked folders. Undo never restores the faulty links.

## Before starting

You need a native Claude Desktop installation on macOS, Windows, or Linux, plus Python 3.9 or newer. Run the Windows launcher in Windows, not in WSL. For Linux, use the [official Desktop installation instructions](https://code.claude.com/docs/en/desktop-linux).

Only combine conversation histories that you intend to make available under all included accounts and organizations. Continuing an imported conversation uses the active account’s service, subscription, models, and organization settings.

Compatibility depends on Claude’s storage layout. Automated checks cover native Windows, macOS, and Ubuntu 24.04 filesystem operations, migration, copying, recovery, and undo, with Python 3.9 and 3.12. Those tests do not substitute for checking actual Claude Desktop loading and saving after app updates. The reported failure was investigated against macOS Desktop **5.1231.2**; the old 4.4212.0 read-only check was insufficient to establish save compatibility.

## What is copied?

| Item | Behavior |
| --- | --- |
| Local Code sidebar records | Copied to all detected account/organization folders during each explicit sync. |
| Conversation history | Referenced through existing local transcript files. A sidebar record cannot recreate a missing transcript. |
| New or updated sessions | Stay in the account that saved them until you quit Claude and run Sync again. |
| Local Code settings, skills, agents, plugins, project memory | Continue using their existing local files. This tool does not rewrite or merge configuration files. |
| Login credentials and subscriptions | Remain separate and are never copied. |
| Ordinary Chat, Cowork, and cloud sessions | Not synchronized. |
| Saved environments, sidebar layout, account-hosted customization | Remain account-specific. |
| Remote Control and connectors | Account-bound references are removed from imported copies; reconnect them under the intended account if needed. The source account’s own settings are retained when its record is unchanged. |
| Organization policies and model access | Still depend on the active account. |

This is **manual local copying**, not automatic sharing or cloud synchronization. Use one active Desktop login at a time.

## Detailed setup without programming

### 1. Download and extract

Download the ZIP from the link at the top, or use **Code → Download ZIP** on GitHub. On Windows choose **Extract All** rather than opening the launcher inside the ZIP. On Mac double-click the ZIP; on Linux use your archive manager.

Keep these files together in a convenient folder:

```text
Claude Session Sharing.command   (Mac launcher)
Claude Session Sharing.cmd       (Windows launcher)
Claude Session Sharing.sh        (Linux launcher)
claude-session-sharing.py        (required helper for every platform)
READ ME FIRST.txt
README.md
```

Source downloads also contain tests and a workflow. No extra Python packages are required. Use your normal computer account, not administrator mode or `sudo`.

### 2. Let Claude create each account folder

Open Claude Desktop. Sign into each account/organization you want to include, and open the Code tab once. A single email account can have several organization folders, so the folder count may exceed your number of logins.

There is currently no account-selection menu: every detected account/organization folder in the chosen Desktop data directory is included.

### 3. Finish work and quit

Wait for running work to finish. Quit the app completely with its Quit/Exit menu. Closing a window may leave Claude running. On Mac, Command + Q quits. On Windows, check the tray icon near the clock. The script stops if it detects Claude processes; its conservative check can also catch an open Claude CLI process.

### 4. Open the launcher

On Mac or Windows, double-click the appropriate launcher. On Linux, open a terminal in the extracted folder and run:

```bash
bash "./Claude Session Sharing.sh"
```

If a Mac `.command` file opens in an editor, choose **Open With → Terminal** in Finder. A Linux `.sh` file may also open as text; use the terminal command above instead. If company controls block scripts, ask IT for the approved method. Do not disable security settings.

You will see:

```text
1. Sync / repair old setup (default)
2. Check status
3. Undo last sync
4. Exit
```

Press Enter for option 1. The preview changes nothing. It reports the folders, distinct records, and legacy links to repair. Type **SYNC** to apply; pressing Enter without that word cancels. Keep Claude closed until the success message appears.

Every sync saves a timestamped backup before changing account folders. Keep the printed backup path if you need help later.

### 5. Reopen and check

Reopen Claude, open Code, and find a familiar conversation. Open it without sending a prompt to check its history. New sessions need another sync before they become available under other accounts.

For folders instead of one long Recents list, choose **Group and sort → Group by → Folder**. This preference is separate for each account/organization.

## Switching accounts later

1. Finish your current work.
2. Quit Claude fully.
3. Open this launcher and choose Sync; type **SYNC**.
4. Reopen Claude and switch to the other account.
5. Open Code and check the copied session.

If you add a new account/organization, open Code in it once, quit, and run Sync again to include it. Merely switching accounts does not trigger copying. Do not run two sync operations at the same time.

Sync is additive: it does not propagate deletion. A deleted entry may be copied back from another account or the archive. Archive a conversation instead when you want it out of your active list.

When the same session ID exists in multiple places, the file with the newest modification time wins; equal timestamps prefer a native account record over the archive. Every pre-sync variant remains in that run’s backup. Copies retain source timestamps so the next sync can recognize genuinely newer account writes. This is not a semantic merge of simultaneous edits.

## Recover conversations missing after the old setup

First run Sync/repair with Claude closed. This restores normal writable directories, but it cannot recover a sidebar record that was never written.

If the original `.jsonl` transcript still exists, a maintainer can use the recovery command below. It rebuilds minimal sidebar metadata from that explicit transcript, backs up the transcript, and copies the recovered entry to all detected account folders. It **does not modify conversation messages** or send a prompt. Recovered entries start with default/manual permissions and no inherited connector approvals.

Do not guess transcript IDs or move transcript files to try to fix the sidebar. Ask the maintainer to identify the correct file and verify the recovered conversation in Desktop. Missing transcripts cannot be reconstructed by this tool. Conversation attachments, cloud artifacts, and unavailable remote resources may need separate recovery.

## Check status

Open the launcher and choose **2**. It reports normal and legacy-linked account folders, archive records, the last operation phase, and the last completed sync time. **Legacy linked folders should be zero after repair.** The archive record count is not a guarantee that all corresponding transcript files still exist.

If a previous sync was interrupted, keep Claude closed and use Undo before running another sync.

## Undo the last sync

1. Quit Claude completely.
2. Open the launcher and choose **3**.
3. Type **UNDO**.
4. Reopen Claude when it finishes.

Undo restores the account folders and archive to their snapshots immediately before the last sync. Before doing so it preserves their current state in another timestamped backup, so work saved after that sync is retained there. Those later records are not automatically reinserted into the restored folders. The original transcript files are never changed.

If the pre-sync folder was a legacy link, Undo restores its copied contents into a **normal folder**, not a link. Old link-mode journals must be migrated with Sync/repair first. Undo is one level; older backups remain available for maintainer-assisted recovery. Deleting the downloaded launcher does not restore an earlier snapshot or delete any conversations.

## Troubleshooting

### Claude is still running

Finish tasks and use Quit/Exit. On Windows, quit the tray icon too. Close any Claude CLI processes if necessary, then retry. The helper does not kill processes for you.

### Python is missing or too old

Install Python 3.9+ from [python.org](https://www.python.org/downloads/) or ask IT. Windows tries `py -3`, then `python`. Linux needs a suitable `python3` package. Close and reopen the launcher after installation. If Mac offers developer tools you do not want, cancel and ask IT to install Python directly.

### No local folders were found

Sign into each intended account/organization, open Code once, quit Claude, and retry. Ensure you are running the launcher as the same operating-system user who uses Claude.

### Multiple stores were found

Stop and ask the maintainer to select the correct Desktop data directory with `--data-dir`. The script refuses to guess. This tool does not merge multiple independent installations.

### A conversation still does not appear

Verify you ran Sync after the source account saved it. Check archived sessions and sidebar filters. If the old linked setup prevented the sidebar entry from being saved, its existing transcript may need the explicit recovery step above.

### A conversation appears but has no history

Its transcript may be missing, cleaned up, or stored elsewhere. Preserve the backups and ask for investigation. An entry alone cannot recreate messages.

### Folders look different under another organization

Choose **Group and sort → Group by → Folder** there. Layout and grouping are not synchronized.

### “Claude can’t use thinking from another organization”

This is an account/organization restriction on preserved thinking, not a missing transcript. The earlier thinking stays in the stored conversation, but the active organization may not be allowed to reuse it. Claude can reread the visible history and generate fresh thinking, which can take longer and use more tokens. To reuse the original thinking, resume under the organization that produced it. The sync tool cannot remove this restriction and does not strip or rewrite thinking blocks in your transcript. See [Anthropic’s preserved-thinking documentation](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking).

### Connectors, a model, or subscription access do not work

Imported records do not carry another account’s connector login or Remote Control identity. Reconnect under the intended account. Model entitlements, subscriptions, and organization restrictions are unaffected by syncing records.

### Sync or Undo was interrupted

Keep Claude closed. Use Undo before retrying Sync. If Undo reports an error, stop and send the error text to the maintainer. Do not delete account directories or backups. Backups can contain private data; do not publish them.

### A Desktop update changes behavior

Preserve the normal account folders and transcripts, and ask the maintainer to verify both loading **and saving**. Successful copying or reading is not sufficient to prove future writes persist.

## Data locations and privacy

The helper uses the current user’s native Desktop store. There are no hardcoded usernames or account IDs.

| Platform | Discovery candidates |
| --- | --- |
| macOS | `~/Library/Application Support/Claude` |
| Windows | `%APPDATA%\Claude`; matching Claude package data under `%LOCALAPPDATA%\Packages\...\LocalCache\Roaming\Claude`; existing `%LOCALAPPDATA%\Claude-Data\claude_*` directories. |
| Linux | `$XDG_CONFIG_HOME/Claude` (default `~/.config/Claude`), plus existing `claude-desktop` and `claude` variants under that configuration root. |

Only candidates containing `claude-code-sessions` are considered. Paths vary with installers; these candidates are not a promise about every distribution.

Inside the selected data directory:

| Path | Purpose |
| --- | --- |
| `claude-code-sessions/<account>/<organization>/` | Normal account folders that Claude reads and writes. |
| `shared-code-sessions/` | Fallback archive of records from the last sync; not a live shared folder. |
| `codex-session-sharing-backups/offline-<timestamp>/` | Pre-sync account snapshots, archive snapshot, manifest, replaced folders, and any explicitly recovered transcripts. |
| `codex-session-sharing.json` | Local operation journal, using the legacy filename for compatibility. |

The helper does not edit login files, project files, settings files, or transcript contents. It does not download software, contact GitHub, send messages, or install a background service. Existing session and backup files remain private local data. Never commit them to this repository.

## Commands for maintainers

Run from the repository folder; on Windows substitute `py -3` for `python3`.

```bash
# Read-only preview.
python3 claude-session-sharing.py plan

# Copy records and migrate recognized legacy links. Claude MUST be closed.
python3 claude-session-sharing.py sync

# The old command name is a backward-compatible alias for sync, not link setup.
python3 claude-session-sharing.py setup

# Read-only status.
python3 claude-session-sharing.py status

# Restore the last pre-sync snapshots, preserving current files first.
python3 claude-session-sharing.py undo

# Explicitly rebuild one missing sidebar entry and synchronize it.
python3 claude-session-sharing.py recover --transcript "/path/to/session-uuid.jsonl"

# Repeat --transcript to recover more than one known transcript in the same run.
python3 claude-session-sharing.py recover --transcript "/path/to/first-uuid.jsonl" --transcript "/path/to/second-uuid.jsonl"

# Custom Desktop store; supply the same directory for every command.
python3 claude-session-sharing.py sync --data-dir "/path/to/Claude"
```

Direct `sync`, `setup`, `recover`, and `undo` commands apply changes immediately. The launcher adds a preview and typed confirmation. Recovery uses explicit transcript paths; it does not scan and silently import all CLI conversations.

```bash
git clone git@github.com:gtarun/My-Shared-Claude.git
cd My-Shared-Claude
python3 -m unittest discover -s tests -v
bash -n "Claude Session Sharing.sh"
zsh -n "Claude Session Sharing.command"
```

Tests use temporary data and cover normal-directory persistence, the Unix no-follow directory check, legacy-link migration, newer native writes, account-bound metadata handling, explicit transcript recovery, interrupted sync, undo preservation, platform discovery, process guards, and native launcher startup. GitHub Actions runs them on all three platforms. Windows junction creation is used only in test fixtures to reproduce and remove the old layout; the production helper never creates links.

For Claude’s own settings and features, see the [official Desktop documentation](https://code.claude.com/docs/en/desktop).
