# My Shared Claude: Promotion Plan

Where to post, in what order, and what to post. Every post is written for its place: same product, different angle.

**Ground rules (these keep you from getting banned):**
- Always say you made it ("I built…"). Undisclosed self-promotion is the main reason accounts get banned on Reddit and HN.
- Never ask for upvotes. Ask for feedback. Product Hunt, HN and Reddit all penalize vote requests.
- Don't paste the same text in many places on the same day. Reddit's spam filter catches cross-posts, so space them 1–2 days apart and rewrite each one.
- Read each subreddit's sidebar rules right before posting. Many only allow self-promotion on certain days or with a specific flair. I couldn't read them automatically because Reddit blocked the request.
- Stick around for 2–3 hours after each post and reply to every comment. Early replies are what make a post rise.
- Post from an account with some history. A brand-new Reddit account posting a link usually gets auto-removed.

**Biggest boost before you start:** a 20–30 second GIF/video. Show the sidebar on account A, switch to B (empty), run the launcher, switch again (full). Put it at the top of the README and attach it to Reddit, X and LinkedIn posts. Posts with a visual of the problem do much better than text.

---

## Timeline

| When | Where |
|------|-------|
| Day 0 (PH launch day) | Product Hunt · X · LinkedIn · Claude Developers Discord |
| Day 1 | Show HN |
| Day 2 | r/ClaudeAI |
| Day 3 | r/ClaudeCode |
| Next Monday | Peerlist Launchpad (Mondays, 00:00–23:59 UTC) |
| Week 1 | DevHunt · Uneed (free queue, 30+ day wait, so submit early) · Fazier |
| Week 1–2 | dev.to / Hashnode technical write-up, then share that on r/programming-adjacent subs |
| Week 2 | r/SideProject · r/opensource · r/coolgithubprojects |
| **On or after Nov 18, 2026** | awesome-claude-code. It requires 14 days since your first commit (Nov 4) or 100 stars. |
| Ongoing | Answer existing questions about multiple Claude accounts on Reddit, the Discord or GitHub issues, and link the tool where it genuinely solves the problem |

---

## 1. Show HN

Rules: it must be something people can try and that you made yourself. No marketing language, and don't ask friends to vote. ([guidelines](https://news.ycombinator.com/showhn.html))
Best time: weekday, 8–10 AM US Eastern. Submit the GitHub URL.

**Title**
```
Show HN: My Shared Claude – one Claude Code session list across multiple accounts
```

**First comment (post right after submitting)**
```
I have a personal and a work Claude account on one laptop. Claude Desktop keeps local Code sessions in a per-account/per-org folder, so switching accounts swaps the whole Code sidebar. The session I was in an hour ago disappears until I switch back.

This is a ~300-line, dependency-free Python script (with double-click launchers for macOS/Windows/Linux) that:
- finds every <data dir>/claude-code-sessions/<account>/<org>/ folder
- merges their session records into one shared store (newest file wins on ID conflicts)
- moves each original folder to a timestamped backup and replaces it with a link: symlink on macOS/Linux, directory junction on Windows (so no admin/Developer Mode needed)
- writes a journal so `status` and `undo` know exactly what it did

It shows a dry-run preview first and requires typing SHARE to apply. Undo restores the original folders. It doesn't touch auth, cloud chats, connectors or org policies, and it strips account-bound Remote Control / remote MCP references from imported copies.

Caveats: it depends on Desktop's on-disk layout, which could change in any update. macOS is verified end to end. Windows/Linux pass CI (3.9 and 3.12 on all three OSes) but I haven't confirmed real Desktop history loading there yet. Not affiliated with Anthropic.

Feedback I'm after: is linking folders the right approach vs. syncing copies, and would you want per-account selection?
```

---

## 2. Reddit

**Rules checked on Nov 10, 2026, while logged in as u/gtarun24 (1 karma):**
- **r/ClaudeAI:** feed posts need **more than 100 karma**. Showcase posts must be built with or for Claude by you, explain *how Claude helped*, say it's free, keep promotional language minimal, and use a flair (`Built with Claude` or `Productivity`). **You can't post here yet.**
- **r/ClaudeCode:** simple project shares go in the **Weekly Showcase Thread**. Standalone posts need the `Built with Claude Code` flair and a real write-up: how it works, how Claude Code was used, and what you learned. **The showcase thread is open to you now.**
- **r/opensource:** requires an OSI license (you have MIT ✓) and the `Promotional` flair. It removes drive-by posts and karma-farming accounts, so stay and answer comments.
- **Building karma honestly:** spend 1–2 weeks answering Claude Code questions in r/ClaudeCode and r/ClaudeAI. Real help, no links. That gets you past 100 karma.

### r/ClaudeCode Weekly Showcase Thread (available now)
Answer the thread's prompts: what you built, how you used Claude Code, a link, and what you learned.

### r/ClaudeAI (largest audience; needs 100+ karma)
Use flair `Built with Claude`. The rules require explaining how Claude helped build it, so add a paragraph on that to the body below.

**Title**
```
Switching between personal and work Claude accounts hides your Code sessions. I made a free fix
```
**Body**
```
If you use the Code tab in Claude Desktop with more than one account or org, you've probably seen this: switch accounts and the whole local session list changes. The thing you were working on is gone until you switch back.

I got tired of it and wrote a small open-source helper that links each account's local Code session folder to one shared store on your machine. After setup, every account sees the same local session list.

- Double-click launcher for Mac / Windows / Linux (needs Python 3.9+, no packages, no admin)
- Shows a preview first; nothing changes until you type SHARE
- Original folders are backed up; Undo restores them
- Logins, billing, cloud chats, connectors and org policies stay separate

One honest warning: only do this if you're OK with all included accounts seeing those histories. Think about it before mixing a work org into a personal account.

Repo: https://github.com/gtarun/My-Shared-Claude

Not affiliated with Anthropic. Mac is verified; I'd love to hear from Windows/Linux users whether it works on a real install.
```

### r/ClaudeCode (smaller, more technical)
**Title**
```
Built a tiny tool to keep one Claude Code session list across multiple Desktop accounts (symlinks/junctions, with undo)
```
**Body**
```
Claude Desktop stores local Code sessions under claude-code-sessions/<account>/<org>/, so every account switch swaps your sidebar.

My Shared Claude merges those into one store and replaces each per-account folder with a link (symlink on macOS/Linux, junction on Windows). It's ~300 lines of stdlib Python, journaled, with dry-run preview and one-step undo. CI runs on macOS/Windows/Ubuntu × Python 3.9/3.12.

What it doesn't do: share auth, cloud sessions, connectors, sidebar prefs.

https://github.com/gtarun/My-Shared-Claude

Curious whether anyone has hit edge cases with multiple orgs under one login. The folder count there surprised me.
```

### r/SideProject
**Title**
```
I built a free tool so switching Claude accounts doesn't hide my coding sessions
```
**Body:** use the r/ClaudeAI body, but open with one line about why you built it ("I juggle a work and personal account…") and end with "What would you add?"

### r/opensource
**Title**
```
My Shared Claude: MIT-licensed helper to share Claude Code's local session list across accounts
```
**Body:** use the short technical body from r/ClaudeCode. Mention the MIT license and that the code is one readable file.

### r/coolgithubprojects
Post the repo link with a one-line description:
```
My Shared Claude: keep one local Claude Code session list when switching between Claude accounts (Mac/Windows/Linux, preview + undo)
```

**Skip:** r/programming (it bans self-promotional project posts) and r/macapps (it has strict rules and isn't the right audience). r/vibecoding and r/ChatGPTCoding are optional. Post there only if your Day 2–3 posts go well, and adapt the text.

---

## 3. awesome-claude-code (submit on or after Nov 18, 2026)

The main list ([hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)) only takes submissions through its **"Recommend a resource" issue form**, not pull requests. A repo needs **14+ days since the first commit or 100+ stars**. Submit it yourself, because the form asks you to confirm you checked everything personally.

Form answers:
- **Display Name:** `My Shared Claude`
- **Category:** `Configuration` (fallback: `Multi-Purpose`)
- **Link:** `https://github.com/gtarun/My-Shared-Claude`
- **Author Name:** `gtarun`
- **Author Link:** `https://github.com/gtarun`
- **Description** (must be descriptive, not promotional, and not address the reader):
```
Cross-platform helper that links the per-account local Code session folders of Claude Desktop into one shared store, so the same local session list appears after switching accounts or organizations. Includes a dry-run preview, timestamped backups, and one-step undo; uses symlinks on macOS/Linux and directory junctions on Windows.
```

---

## 4. Launch boards (beyond Product Hunt)

| Site | How it works | Cost | Notes |
|------|-------------|------|-------|
| **Peerlist Launchpad** | Launch on a Monday (UTC); a week of voting | Free with a verified profile | Developer audience, a very good fit |
| **DevHunt** | Dev-tools-only launch board; voters log in with GitHub | Free listing; paid weekly launch | Strong fit for open-source dev tools |
| **Uneed** | Free queue with a 30+ day wait | Free, or paid to skip the line | Submit now so the date comes after PH |
| **Fazier** | Daily launches | Free submission | Smaller audience, but it's quick |
| **Indie Hackers** | Post in the community, not as a launch | Free | Write a "what I learned" angle, not an ad |

Reuse the Product Hunt tagline, description and gallery images on all of them.

---

## 5. Technical write-up (dev.to + Hashnode + Medium, same article)

A how-it-works article reaches people searching for this problem for months afterward. Post it on dev.to first, then cross-post with a canonical link.

**Title options**
- `How Claude Desktop stores Code sessions, and how I share them across accounts`
- `Symlinks vs. junctions: making one Claude Code session list work on Mac, Windows and Linux`

**Outline**
1. The problem (screenshot of two different sidebars)
2. Where Claude Desktop keeps local Code sessions on each OS (table from README)
3. Approach: merge, then link. Why links instead of syncing copies
4. Windows: why directory junctions (no admin / Developer Mode)
5. Safety: dry-run, journal, timestamped backups, undo
6. What it intentionally doesn't share (auth, connectors, cloud)
7. Testing across 3 OSes in GitHub Actions
8. Caveats and what's next, with a link to the repo

Tags: `claude`, `ai`, `productivity`, `opensource`, `python`

---

## 6. Social

### X / Twitter (launch day)
Attach the GIF or `gallery/02-before-after.png`.
```
I use Claude Code with a personal account and a work account.

Every switch, my local Code sessions vanished from the sidebar.

So I built My Shared Claude: one session list across all your accounts.

• double-click setup
• preview before any change
• one-step undo
• free + open source

[Product Hunt link]
```
Follow-up tweet in the same thread (people like seeing how it was built):
```
How it works: Claude Desktop keeps Code sessions per account/org. The tool merges them into one store and swaps each folder for a link (symlink on Mac/Linux, junction on Windows). ~300 lines of Python, no dependencies.

Repo: https://github.com/gtarun/My-Shared-Claude
```

### LinkedIn (launch day)
Use the LinkedIn post in `LAUNCH-KIT.md`, section 5.

### Claude Developers Discord
Post in the showcase / projects channel only, never in help channels:
```
Made a small open-source helper for anyone using Claude Desktop's Code tab with multiple accounts/orgs: it keeps one local session list across account switches (links the per-account folders to a shared store). Preview + undo, Mac/Win/Linux. Feedback welcome, especially from Windows/Linux folks: https://github.com/gtarun/My-Shared-Claude
```

---

## 7. Ongoing (the highest-converting channel)

Search for people who already have this problem and answer them helpfully:
- Reddit search: `claude multiple accounts sessions`, `claude code switch account history`, `claude desktop two accounts`
- GitHub issues on `anthropics/claude-code` that mention account switching or lost sessions
- X search: `"claude code" "two accounts"` / `"switch accounts"`

Answer the actual question first, then add "I ran into this too and made a small tool for it: [link]. Disclosure: I made it."

---

## Track it

| Channel | Date | Link | Upvotes/likes | Comments | GitHub stars after |
|---------|------|------|---------------|----------|--------------------|
| Product Hunt | | | | | |
| Show HN | | | | | |
| r/ClaudeAI | | | | | |
| r/ClaudeCode | | | | | |
| Peerlist | | | | | |
| DevHunt | | | | | |
| dev.to | | | | | |
| awesome-claude-code | | | | | |
