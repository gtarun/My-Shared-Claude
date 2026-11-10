# My Shared Claude

**Keep the same local Claude Code session list when switching between your Claude accounts on one computer.**

## Start here — quick setup

**Choose your platform below. All launchers require Python 3.9+.**

| Your computer | Launcher | How to open it |
| --- | --- | --- |
| macOS | `Claude Session Sharing.command` | Double-click in Finder. |
| Windows | `Claude Session Sharing.cmd` | Extract the ZIP first, then double-click the `.cmd` file. |
| Linux | `Claude Session Sharing.sh` | Open a terminal in the extracted folder and run `bash "./Claude Session Sharing.sh"`. |

Windows and Linux support is new. The automated checks exercise their native folder-linking and undo operations; testing a real Claude Desktop conversation is still required on your own machine. macOS Desktop history loading was verified on version 4.4212.0.

1. **Download:** [Download the ZIP](https://github.com/gtarun/My-Shared-Claude/releases/latest/download/My-Shared-Claude-v1.0.zip), then extract it: double-click on Mac, **Extract All** on Windows, or **Extract** on Linux. Keep the extracted files together.
2. **Open your accounts:** In Claude Desktop, sign into each account/organization you want included and open the **Code** tab once in each.
3. **Quit Claude:** Finish running tasks, then use **Quit/Exit** in Claude. On Mac, press **Command + Q**. On Windows, also exit Claude from its system-tray icon if it is still running.
4. **Run setup:** Open the launcher for your platform from the table above. Press **Enter**, review the preview, type **SHARE**, and press Enter again.
5. **Check:** Reopen Claude → **Code**. Open an older conversation, then switch accounts to check it there too.
6. **Show folders:** In each account, choose **Group and sort → Group by → Folder** if you prefer project folders instead of Recents.

**Done.** Switch normally between linked accounts. For a new account later, repeat steps 2–4. To undo, quit Claude, open the launcher, and choose **3**.

This combines all detected local Code account folders on your computer. Ordinary chats, cloud sessions, and connector logins remain separate. If Python is missing, [install it from python.org](https://www.python.org/downloads/) or ask IT, then retry. For other issues, see [Troubleshooting](#troubleshooting).

## More detail

For example, you can start a local Code conversation while signed into your personal account, switch to your work account, and still find that conversation in the Code sidebar.

You do not need to understand programming, Git, or Python to use the launcher. Follow the setup steps below. Python does need to be installed so the launcher can run its helper.

> This is an independent local workaround for the **Code tab in Claude Desktop**. It does not merge ordinary Claude chats or cloud accounts. Each teammate runs it on their own computer; conversations are not synchronized between teammates or computers.

## Before you start

You need:

- **macOS, Windows, or Linux** with a native Claude Desktop installation. For Linux, follow the [official Linux Desktop installation guide](https://code.claude.com/docs/en/desktop-linux); Linux Desktop is currently beta. Run the Windows launcher in Windows, not inside WSL.
- At least two Claude accounts or organizations that you want to share local Code conversations between.
- **Python 3.9 or newer**. If you are unsure whether you have it, try the launcher: it checks before making changes.
- A few minutes to finish your current Claude tasks and close the app.

The macOS setup was verified with **Claude Desktop 4.4212.0**. Claude updates can change how sessions are stored, so compatibility with every future version is not guaranteed.

Only combine conversation histories that you intend to make available under all the included accounts and organizations. If you continue a shared conversation under a different account, its existing context may be processed using that account's service and organization settings.

## What is shared?

| Item | What to expect |
| --- | --- |
| Local Code session list | Combined across the account/organization folders already present on this computer. |
| Existing local Code conversation history | Can be reopened when its original transcript is still available. A session entry alone cannot recreate a missing transcript. |
| New local Code sessions | Saved in the shared session store for the linked accounts. |
| Local Code settings, skills, agents, plugins, and project memory | Continue using their existing local files. The script does not copy account-hosted customization into them or rewrite your settings. |
| Authentication and subscriptions | Remain separate. You still sign into the account you want to use. |
| Ordinary Claude Chat, Cowork, and cloud sessions | Not merged. |
| Connectors and connector authentication | Remain account-specific and may need reconnecting. |
| Saved environments and sidebar layout | Remain account-specific. See the folder-view instructions below. |
| Organization policies and available models | Still depend on the active account and organization. |

The goal is to share your **local Code workspace**, not to make separate Claude accounts identical.

## Setup: step by step

### 1. Download and extract the files

If a teammate gave you `Claude-Session-Sharing.zip`, extract it using Finder on Mac, **Extract All** on Windows, or your Linux archive manager. Do not run files from inside an unextracted ZIP.

Alternatively, download the source from this GitHub repository using **Code → Download ZIP**, then extract the downloaded ZIP.

Open the extracted folder. These files must stay together:

```text
Claude Session Sharing.command  # Mac
Claude Session Sharing.cmd      # Windows
Claude Session Sharing.sh       # Linux
claude-session-sharing.py
READ ME FIRST.txt
```

The source download also includes this README and the tests. Keep the extracted folder somewhere convenient, because you will use the same launcher to check status, add accounts, or undo setup later.

### 2. Open each account in Claude once

The launcher can only connect account folders that Claude has already created on this computer.

1. Open **Claude Desktop**.
2. Sign into your first account and open the **Code** tab.
3. Use the account menu to switch accounts or organizations. Sign out and back in if necessary.
4. Open the **Code** tab in each account or organization you want included.

You do not need to send a test message. Opening Code allows Claude to create its local session folder.

### 3. Quit Claude completely

Finish any running work first, then use Claude’s **Quit/Exit** menu. On Mac, **Command + Q** or **Claude → Quit Claude** closes the app. On Windows, check the system tray near the clock and exit Claude there too if it remains running. On Linux, quit the native Desktop app.

Closing a window may leave the app running. The launcher checks for Claude processes and stops if they are still running. Its conservative check can also detect an open Claude CLI process; close that process before retrying.

### 4. Open the launcher

Choose the matching option:

- **Mac:** double-click **Claude Session Sharing.command** in Finder.
- **Windows:** double-click **Claude Session Sharing.cmd** in the extracted folder. A command window opens. Do not choose **Run as administrator**; use your normal Windows account.
- **Linux:** open the extracted folder, right-click an empty area and choose **Open in Terminal** if available. Paste the line below and press Enter. You do not need `sudo` or `chmod` for this method.

```bash
bash "./Claude Session Sharing.sh"
```

A terminal/command window displays the instructions. You should see:

```text
Claude Desktop — Local Code Session Sharing

1. Set up / add accounts (default)
2. Check status
3. Undo sharing
4. Exit
```

On Mac, if the `.command` file opens in a text editor, close the editor and use **Open With → Terminal** from its Finder menu. On Linux, a `.sh` file may open in an editor; use the terminal command above instead.

If your operating system or company's device controls block the launcher, ask your IT administrator for the approved way to run a local script. Do not turn off system security protections.

### 5. Review and apply setup

1. Press **Enter** to choose setup, or type **1** and press Enter.
2. Read the preview. It reports how many account/organization folders it found and how many need linking.
3. If these are the local Code histories you want to combine, type **SHARE** in capital letters and press Enter.
4. Wait for the success message showing the number of shared session records and the backup location.
5. Press Enter when asked to close the launcher.

The preview makes no changes. Pressing Enter without typing `SHARE` cancels setup.

Setup includes **all detected local Code account/organization folders** on this computer. There is currently no menu for choosing only some of them. A single account can have several organization folders, so the reported folder count can be higher than your number of email logins.

### 6. Reopen Claude and check your conversations

1. Open Claude Desktop again.
2. Go to the **Code** tab.
3. Check that older local Code sessions appear in the sidebar.
4. Open a familiar conversation to confirm its history is available.
5. Switch to another included account or organization and check the Code tab there too.

You do not need to send a message just to check that the history loads. An inactive subscription can prevent continuing a conversation even when its local history is available.

## Show project folders instead of one long list

The same conversations can look different under different accounts because sidebar preferences are separate.

If you see **Recents** instead of project folder headings:

1. In the Code sidebar, open **Group and sort** beside the session-list heading.
2. Choose **Group by**.
3. Choose **Folder**.

Repeat once for each account or organization where you want folder grouping. The launcher shares session records; it does not automatically synchronize sidebar preferences, pinned sections, or collapsed groups.

## Everyday use after setup

Use Claude normally and switch accounts when needed. Linked account folders point to the same local Code session store, so new sessions and updates are available to those linked accounts.

You do **not** need to run setup every time you switch between accounts that are already connected. If the sidebar has not refreshed after switching, quit and reopen Claude.

Use one active Desktop login at a time. This package is not designed for running multiple Desktop account windows simultaneously.

## Add another account or organization later

1. Sign into the new account or organization in Claude Desktop.
2. Open Code once so Claude creates its local session folder.
3. Finish your tasks and quit Claude completely using **Quit/Exit** (**Command + Q** on Mac).
4. Open the launcher again and choose **1. Set up / add accounts**.
5. Review the preview and type **SHARE**.
6. Reopen Claude.

Running setup again adds new folders without replacing existing shared conversations. If a new folder contains a session ID that is already shared, the existing shared copy takes priority. On initial setup, duplicate IDs are resolved using the most recently modified source file.

## Check whether sharing is working

Open the launcher, type **2**, and press Enter.

It reports:

- How many session records are in the shared store.
- How many account/organization folders are linked, out of the total detected.

For example, **5 / 6** means five folders share sessions and one detected folder still needs setup. It does not mean a conversation has been deleted.

## Undo the setup

1. Finish any running Claude tasks.
2. Quit Claude completely using **Quit/Exit** (**Command + Q** on Mac).
3. Open the launcher.
4. Type **3** and press Enter.
5. Read the explanation, type **UNDO** in capital letters, and press Enter.
6. Reopen Claude.

Undo restores each original account folder from its backup. **Sessions created or updated after sharing was installed remain saved in the shared store**, but those later changes are not automatically copied into the restored per-account folders. If you need them moved back into a particular account, ask the person maintaining this tool to help before deleting any folders.

Undo does not delete the shared store. Simply deleting the downloaded launcher does not undo setup either; use the Undo option first if you want to stop sharing.

## Troubleshooting

### “Quit Claude completely…”

Claude is still running. Finish your tasks and use **Quit/Exit**, then retry. On Mac, press Command + Q. On Windows, also check the system-tray icon. Close open Claude CLI processes if the check continues to block setup.

### “Sign in to each account… and open Code once”

The expected local session folders were not found. Open Claude, sign into the intended accounts/organizations, and open Code in each. Quit Claude and retry.

### Python is missing or too old

The helper requires Python 3.9 or newer. On Mac or Windows, download a current stable installer from [the official Python website](https://www.python.org/downloads/), or ask IT to install Python using your company's usual process. On Windows, the launcher tries `py -3` first, then `python`. On Linux, ask IT to install your distribution’s `python3` package (3.9 or newer). After installation, close the launcher window and open it again. You do not need to install any extra Python packages.

If macOS offers to install Apple developer tools when launching Python, cancel if you do not want those tools and ask IT to help install Python directly instead.

### The Python helper is missing

You may have moved only the launcher (`.command`, `.cmd`, or `.sh`). Extract the whole ZIP again and keep the launcher and `claude-session-sharing.py` in the same folder.

### Sessions appear, but project folders do not

Choose **Group and sort → Group by → Folder**. This preference is separate for each account/organization.

### A session is listed, but its conversation does not open

The list entry and the actual transcript are separate files. If a transcript was already missing, cleaned up, or stored somewhere this setup cannot reach, this tool cannot recreate it. Keep the backups and ask the maintainer to investigate. The number of session records is not a guarantee that every historical conversation can be recovered.

### Connectors need to reconnect

That is expected when switching accounts. Newly imported copies have old account-bound Remote Control/bridge references and remote MCP connector definitions removed. Reconnect services under the account you intend to use. The tool does not move login credentials between accounts.

### Claude says the subscription is inactive or a model is unavailable

Session sharing does not change billing, organization policies, or model entitlements. Select an account/organization with the required access or contact your administrator.

### Setup was interrupted or reports a file error

Keep Claude closed. Run the launcher and use **Undo** before trying setup again. Original account folders are preserved in timestamped backups. If Undo also reports an error, stop and send the error text to the maintainer rather than manually deleting session folders.

### A Claude update changes the behavior

This tool relies on Claude Desktop's local storage layout. Check whether the maintainer has verified the new version before re-running setup. Preserve the shared store and backups while investigating.

## What the script changes on disk

This section is for the teammate helping with setup; you can use the launcher without understanding these paths.

The helper discovers the native Desktop data directory for the current user. There are no hardcoded usernames or account IDs in the package.

| Platform | Automatically checked locations |
| --- | --- |
| macOS | `~/Library/Application Support/Claude` |
| Windows | `%APPDATA%\Claude`, Claude package folders under `%LOCALAPPDATA%\Packages\...\LocalCache\Roaming\Claude`, and existing `%LOCALAPPDATA%\Claude-Data\claude_*` folders. |
| Linux | `$XDG_CONFIG_HOME/Claude` (defaults to `~/.config/Claude`), plus existing `claude-desktop` and `claude` directories under the same configuration root. |

Discovery uses only locations that contain `claude-code-sessions`. Linux naming variants and Windows package paths are compatibility candidates, not a guarantee about every installer. If more than one distinct store exists, the helper stops rather than guessing. A maintainer can choose the correct store explicitly:

```bash
python3 claude-session-sharing.py plan --data-dir "/path/to/Claude"
```

Replace the path with the actual **Claude data directory**, not its `claude-code-sessions` child. Use the same `--data-dir` for setup, status, and undo. On Windows, use `py -3` in place of `python3` and supply your Windows path. This setup does not merge multiple independent Desktop installations.

| Location | Purpose |
| --- | --- |
| `<Claude data directory>/claude-code-sessions/<account>/<organization>/` | Existing per-account local Code session records. |
| `<Claude data directory>/shared-code-sessions/` | Combined session records used by linked accounts. |
| `<Claude data directory>/codex-session-sharing-backups/` | Timestamped original account folders and shared-store snapshots when adding accounts. |
| `<Claude data directory>/codex-session-sharing.json` | Setup journal used by status and rollback operations. |

Setup moves the original account folders into the backup location and replaces those folders with links to the shared store. It leaves existing transcript locations, project files, local configuration files, and login storage in place. macOS and Linux use symbolic links and owner-only permission modes for newly created shared records and journal files. Windows uses directory junctions, so Developer Mode and administrator symlink privileges are not required; access inherits the protections of your existing user-data directory. Use a local filesystem that supports directory junctions, typically NTFS.

The helper does not download software, send test prompts, contact GitHub, install background services, or require administrator access. Opening Claude and continuing a conversation still uses Claude's normal network behavior.

Backups and transcripts can contain private conversation data. **Do not upload your Claude storage, backups, login files, or setup journal into this repository.** The repository contains the tool, documentation, and tests only.

## Terminal commands for maintainers

From the repository folder (on Windows, substitute `py -3` for `python3`):

```bash
# Read-only preview; no files changed.
python3 claude-session-sharing.py plan

# Install sharing or enroll newly discovered account folders; Claude must be closed.
python3 claude-session-sharing.py setup

# Read-only status.
python3 claude-session-sharing.py status

# Restore original account folders; Claude must be closed.
python3 claude-session-sharing.py undo
```

The command-line `setup` command applies changes directly. The double-click launcher adds the human-readable preview and `SHARE` confirmation.

To clone this repository with Git:

```bash
git clone git@github.com:gtarun/My-Shared-Claude.git
cd My-Shared-Claude
```

To run the tests:

```bash
python3 -m unittest discover -s tests -v

# Optional launcher syntax checks where these shells are installed:
bash -n "Claude Session Sharing.sh"
zsh -n "Claude Session Sharing.command"
```

GitHub Actions runs the suite on native macOS, Windows, and Ubuntu runners with Python 3.9 and 3.12. It tests filesystem behavior and launcher startup, not the actual Claude Desktop app. The tests use temporary folders, not your real Claude account data. They cover the read-only preview, missing storage, session-file validation, merging, shared writes, adding accounts, undo, and recovery after interrupted linking, platform discovery, Windows junctions/native Unix links, and launcher startup.

Before contributing a change, run the tests and describe any compatibility assumptions. Do not broaden claims about cloud synchronization or account-hosted features: those are outside this tool's scope.

For Claude Desktop's own features and settings, see the [official Code tab documentation](https://code.claude.com/docs/en/desktop).
