#!/usr/bin/env bash
# Native Linux launcher. No downloads or administrator access.
package_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Python 3.9 or newer is required. Ask IT to install python3, then retry.'
  read -r -p 'Press Enter to close. ' reply
  exit 1
fi
if [[ ! -f "$package_dir/claude-session-sharing.py" ]]; then
  printf '%s\n' 'The Python helper is missing. Extract the whole ZIP and keep its files together.'
  read -r -p 'Press Enter to close. ' reply
  exit 1
fi
python3 "$package_dir/claude-session-sharing.py" menu
result=$?
if [[ $result -ne 0 ]]; then
  printf '\n%s\n' 'The command did not finish. Read the message above before trying again.'
  read -r -p 'Press Enter to close. ' reply
fi
exit "$result"
