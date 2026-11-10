# Reddit replies: paste one or two a day, not all at once

Your account has 1 karma. Several near-identical comments with the same link in one day is exactly what Reddit's spam filter catches. Space these out over 3–4 days, and stay to answer follow-ups.

Each reply answers the person's question first and says you made the tool.

---

## 1. "claude desktop lost all my chats after switching accounts?" (r/ClaudeCode, Nov 3)
https://www.reddit.com/r/ClaudeCode/comments/1xmu3mq/claude_desktop_lost_all_my_chats_after_switching/

```
They're not gone. Claude Desktop keeps everything per account, so when you log back into the original account they'll all be there.

Regular chats are stored in your account in the cloud, so they always follow the account. Local Code sessions are stored on your computer in a separate folder per account/org (claude-code-sessions/<account>/<org>/), which is why the Code sidebar looks empty after switching.

If you specifically want the same Code session list in both accounts, I ran into the same thing and made a small free tool that links those folders together on your machine: https://github.com/gtarun/My-Shared-Claude (disclosure: I made it). It has a preview and an undo. It doesn't merge regular chats, though; those stay with each account.

It's on Product Hunt today too, if you'd like to leave feedback: https://www.producthunt.com/products/my-shared-claude
```

---

## 2. "Is it possible to swap between Claude Code accounts for different projects?" (r/ClaudeCode, Nov 5)
https://www.reddit.com/r/ClaudeCode/comments/1xonhrl/is_it_possible_to_swap_between_claude_code/

```
In the desktop app it's one signed-in account at a time, as far as I know. There's no per-project account setting.

What made switching bearable for me: the annoying part wasn't logging in and out, it was that each account has its own local Code session list, so my in-progress sessions vanished every time I switched. I wrote a small open-source helper that gives both accounts one shared local session list, so switching to the team account still shows the personal-project sessions and vice versa: https://github.com/gtarun/My-Shared-Claude (I made it, free).

It won't let you run both at once. It just makes switching lose nothing. Only do it if you're fine with those sessions being visible under both accounts, since one of them is your team's.

Launched it on Product Hunt today; feedback there or here is welcome: https://www.producthunt.com/products/my-shared-claude
```

---

## 3. "Multiple Anthropic Claude Account" (r/ClaudeAI, Nov 6)
https://www.reddit.com/r/ClaudeAI/comments/1xpbdk1/multiple_anthropic_claude_account/

```
Welcome! On a laptop, the Claude Desktop app is signed into one account at a time, and you switch from the account menu. Each account keeps its own chats, projects and settings, and on the phone it's the same idea: switch accounts in the app.

One thing that tripped me up if you use the Code tab: local Code sessions are kept separately per account, so after switching it looks like your work disappeared (it didn't; switch back and it's there). If you'd like both accounts to see the same Code sessions on your laptop, I made a free tool for that: https://github.com/gtarun/My-Shared-Claude (disclosure: it's mine). There's a double-click launcher, so no terminal needed.

(It's also on Product Hunt today if you have thoughts on it: https://www.producthunt.com/products/my-shared-claude)
```

---

## 4. "2 accounts simultaneously on Windows Claude desktop app?" (r/ClaudeAI, Nov 1)
https://www.reddit.com/r/ClaudeAI/comments/1xli7z4/2_accounts_simultaneously_on_windows_claude/

```
I haven't found a supported way to run two Desktop instances at once on the same Windows user. Switching is the reliable route.

The part I could fix was the cost of switching: local Code sessions live in a separate folder per account, so switching from Max to Teams hid all my sessions. I built a small tool that links those folders on Windows using directory junctions (no admin rights needed), so both accounts share one local Code session list: https://github.com/gtarun/My-Shared-Claude (I'm the author, free/MIT).

Windows support is new. The automated tests pass on Windows, but if you try it, I'd really appreciate hearing whether your Desktop history shows up in both accounts. Also think about whether you want work sessions visible under your personal account first.

I launched it on Product Hunt today, and Windows feedback there would be gold: https://www.producthunt.com/products/my-shared-claude
```

---

## 5. "Running two Claude Desktop accounts (personal + work) on one Windows user?" (r/ClaudeAI, Oct 16)
https://www.reddit.com/r/ClaudeAI/comments/1x7o9zy/running_two_claude_desktop_accounts_personal_work/

```
Late to this, but in case it helps anyone landing here: I couldn't get two simultaneous Desktop sessions working cleanly either, so I went the other way and made switching painless.

The thing that hurt most was the Code sidebar resetting on every switch (sessions are stored per account/org on disk). I wrote a small open-source helper that links those per-account folders to one shared store, so personal and Team both show the same local Code sessions. It uses junctions on Windows, so it works without admin or Developer Mode, and it has a dry-run preview plus undo: https://github.com/gtarun/My-Shared-Claude (disclosure: I made it).

Logins, connectors and the Team org's policies stay separate. It only shares the local session list.

It's on Product Hunt today as well, for anyone who wants to comment: https://www.producthunt.com/products/my-shared-claude
```

---

## Skipped on purpose
- Threads about rotating accounts or adding a second subscription to stretch usage limits (1xjex7p, 1xhyz18, 1x3e6ju, 1xcf3kw, 1xf97pu). Promoting the tool there frames it as a limit-evasion tool and could get it reported.
- "I built a 2-second account switcher" (1wcjeh6): someone else's launch thread. Don't drop your link in it.
- Terms-of-service-only questions (1x117ik, 1xf1uxw).
