#!/bin/zsh -f
# Native macOS launcher. No downloads or administrator access.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
package_dir="${0:A:h}"
python_bin="$(command -v python3)"
if [[ -z "$python_bin" ]]; then
  print 'Python 3.9 or newer is required. Install it from python.org or ask IT.'
  read "reply?Press Enter to close."
  exit 1
fi
if [[ ! -f "$package_dir/claude-session-sharing.py" ]]; then
  print 'The Python helper is missing. Extract the whole ZIP and keep its files together.'
  read "reply?Press Enter to close."
  exit 1
fi
"$python_bin" "$package_dir/claude-session-sharing.py" menu
result=$?
if [[ $result -ne 0 ]]; then
  print 'The command did not finish. Read the message above before trying again.'
  read "reply?Press Enter to close."
fi
exit $result
