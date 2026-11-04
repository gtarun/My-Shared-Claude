#!/bin/zsh -f
# Local macOS launcher. No downloads, administrator access, or network requests.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
package_dir="${0:A:h}"
helper="$package_dir/claude-session-sharing.py"

print "Claude Desktop — Local Code Session Sharing"
print ""
print "1. Set up / add accounts (default)"
print "2. Check status"
print "3. Undo sharing"
print "4. Exit"
print ""
read "choice?Choose 1–4, then press Enter: "
choice="${choice:-1}"
if [[ "$choice" == 4 ]]; then
  exit 0
fi
python_bin="$(command -v python3)"
if [[ -z "$python_bin" ]]; then
  print "Python 3.9 or newer is required. Install it from https://www.python.org/downloads/macos/ and try again."
  read "reply?Press Enter to close."
  exit 1
fi
if ! "$python_bin" -c 'import sys; raise SystemExit(sys.version_info < (3, 9))'; then
  print "Python 3.9 or newer is required. See https://www.python.org/downloads/macos/"
  read "reply?Press Enter to close."
  exit 1
fi
if [[ ! -f "$helper" ]]; then
  print "The Python helper is missing. Extract the whole ZIP and keep its files together."
  read "reply?Press Enter to close."
  exit 1
fi
result=0
case "$choice" in
  1)
    print ""
    if "$python_bin" "$helper" plan; then
      print ""
      print "Quit Claude completely with Cmd+Q before continuing."
      print "This combines local Code session lists across accounts and organizations on your Mac."
      read "reply?Type SHARE to apply, or press Enter to cancel: "
      if [[ "$reply" == SHARE ]]; then
        "$python_bin" "$helper" setup
        result=$?
        if [[ $result -eq 0 ]]; then
          print ""
          print "Ready. Reopen Claude and check the Code tab."
          print "For project folders: Group and sort > Group by > Folder (set once per organization)."
        fi
      else
        print "Cancelled. No setup changes made."
      fi
    else
      result=1
    fi
    ;;
  2)
    "$python_bin" "$helper" status
    result=$?
    ;;
  3)
    print "Quit Claude completely with Cmd+Q first."
    print "Undo restores original account folders. New shared sessions remain saved in the shared store."
    read "reply?Type UNDO to restore, or press Enter to cancel: "
    if [[ "$reply" == UNDO ]]; then
      "$python_bin" "$helper" undo
      result=$?
    else
      print "Cancelled."
    fi
    ;;
  *)
    print "Unknown option. Run the launcher again and choose 1–4."
    result=1
    ;;
esac
print ""
read "reply?Press Enter to close."
exit $result
