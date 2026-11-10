# My Shared Claude: Product Hunt Launch Kit

Everything you need to paste into Product Hunt, plus a launch-day plan.

---

## 0. Fix these before you submit

Visitors who click through from Product Hunt land on the repo, so these matter.

| # | Fix | Why |
|---|-----|-----|
| 1 | **Add a LICENSE file** (MIT is the usual choice) | The repo has no license. Without one, "open source" isn't technically true and people can't legally reuse the code. |
| 2 | **Add a repo description and topics** on GitHub (`claude-code`, `claude-desktop`, `developer-tools`, `productivity`, `python`) | The repo currently has neither. This is the first thing people see. |
| 3 | **Put the hero image at the top of the README** (`gallery/01-hero.png`) | People from Product Hunt skim. Show the before-and-after before the setup table. |
| 4 | **Add a "not affiliated with Anthropic" line** near the top of the README | Product Hunt reviewers and commenters will ask. Being upfront about it builds trust. |
| 5 | **Create a GitHub Release** (v1.0.0) with a ready-made ZIP | A "Download" button on a release page converts better than "Code → Download ZIP". |
| 6 | **Verify one Windows and one Linux run** with a real Desktop conversation | The README says this isn't verified yet. Expect someone on launch day to ask "does it work on Windows?" |

---

## 1. Listing fields

**Name**
```
My Shared Claude
```

**Tagline** (60 char max)
```
One Claude Code history across all your accounts
```
Alternatives:
- `Switch Claude accounts without losing Code sessions` (51)
- `Keep your Claude Code sessions when you switch accounts` (55)

**Description** (260 char max, exactly 260)
```
Personal and work Claude accounts? Every switch hides your local Claude Code sessions. My Shared Claude links them into one session list: double-click setup, a preview before anything changes, and one-step undo. Free and open source for Mac, Windows and Linux.
```

**Links**
- Website: `https://github.com/gtarun/My-Shared-Claude`
- Additional link (direct download): `https://github.com/gtarun/My-Shared-Claude/releases/latest/download/My-Shared-Claude-v1.0.zip`

**Topics** (pick 3)
`Developer Tools` · `Open Source` · `Artificial Intelligence` (alternatives: `Productivity`, `GitHub`)

**Pricing**
`Free`

**Is this open source?** Yes, after you add the LICENSE file.

**Thumbnail:** `thumbnail-240.png` (240×240)

**Gallery** (1270×760, upload in this order)
1. `gallery/01-hero.png`: One session list, every account
2. `gallery/02-before-after.png`: The problem and the fix
3. `gallery/03-how-it-works.png`: Four-step setup
4. `gallery/04-preview.png`: Preview-first terminal flow
5. `gallery/05-safe-by-design.png`: Safety guarantees
6. `gallery/06-whats-shared.png`: What's shared and what isn't

**Optional video (strongly recommended):** a 30–45 second screen recording. Show the Code sidebar on account A, switch to account B and show an empty sidebar, quit, double-click the launcher, type SHARE, reopen, switch accounts, and show the full sidebar. Upload it to YouTube (unlisted is fine) and add it as the first gallery item.

---

## 2. Maker's first comment

Post this the minute the launch goes live.

```
Hey Product Hunt 👋

I use Claude Code with two accounts on one laptop: a personal one and a work one. It drove me nuts that every time I switched, my local Code sidebar was a different list. The session I'd been working on an hour ago was just… gone, until I switched back.

So I built My Shared Claude. It's a tiny, open-source helper that links your accounts' local Code session folders into one shared store. Switch accounts, and your sessions are still there.

What I cared about while building it:
• Non-developers on my team had to be able to run it, so setup is a double-click launcher. No Git, no pip install, no admin rights.
• It shows you a preview first. Nothing changes until you type SHARE.
• Everything is reversible. Original folders go to timestamped backups, and choosing Undo restores them.
• It's ~300 lines of dependency-free Python you can read before running, with CI tests on macOS, Windows and Linux.

What it deliberately does NOT do: merge logins, billing, cloud chats, connectors or org policies. Each account stays its own account. Only the local Code workspace is shared. (Please only share histories that every included account is allowed to see. That matters if one of them is a work org.)

Honest caveats: it's an independent project, not affiliated with Anthropic, and it relies on Claude Desktop's local storage layout, so a future update could change things. macOS is verified end to end. Windows and Linux pass automated tests, and I'd love reports from real machines.

I'd really appreciate feedback, especially:
1. Does it work on your Windows / Linux setup?
2. Would you want to pick which accounts get linked, instead of all of them?

Thanks for checking it out 🙏
```

---

## 3. Ready answers for likely questions

**"Is this against Anthropic's terms?"**
> It only rearranges files on your own computer. It doesn't touch logins, bypass limits or share anything between people. Each account still signs in separately and uses its own subscription. That said, if one account belongs to an employer, check that you're allowed to bring work history into a personal account (and the other way around).

**"Why not just use one account?"**
> Lots of us have a work org plus a personal plan, or several client orgs. Different billing, different policies. You still want to find yesterday's session.

**"Does it sync between computers / teammates?"**
> No, and on purpose. It's local to one machine and one user. Nothing leaves your computer.

**"What if Claude updates and it breaks?"**
> Run Undo from the launcher to restore your original folders from the backups. I'll post compatibility notes in the README for each Desktop version I verify.

**"Why Python?"**
> It ships with or is easy to get on every OS, needs no extra packages, and one readable file is easy to audit.

---

## 4. Launch-day plan

**When:** Launch at **12:01 AM Pacific** (1:31 PM IST). A Tuesday, Wednesday or Thursday gets the most traffic. Avoid weeks with big AI launches.

**1 week before**
- [ ] Finish the six fixes in section 0
- [ ] Record the 30–45 second demo video
- [ ] Create a Product Hunt "Coming soon" / upcoming page and share it, so followers get notified
- [ ] Make a list of 30–50 people who actually use Claude Code with more than one account, and message them personally (not a mass DM)
- [ ] Pre-write the posts in section 5

**Launch day**
- [ ] 12:01 AM PT: submit or schedule the launch, then post the maker comment immediately
- [ ] Post on X / LinkedIn, linking to the **Product Hunt page** (not the repo)
- [ ] Send personal messages. Ask people to "check it out and share honest feedback," **not** "upvote me." Product Hunt penalizes vote solicitation and vote rings.
- [ ] Reply to every comment within ~30 minutes for the first 6 hours
- [ ] Mid-day: post a progress update or a reply to an interesting question on X
- [ ] Don't open the PH link for people in a way that sends lots of new accounts from the same IP or link (PH's fraud detection discounts those votes)

**Day after**
- [ ] Thank commenters, and add a "Featured on Product Hunt" badge to the README
- [ ] Post on Show HN and Reddit (section 5). Spacing them out keeps each one from drawing attention away from the others.
- [ ] Turn launch feedback (e.g. picking which accounts to link) into GitHub issues

---

## 5. Social posts

**X / Twitter (launch post)**
```
I use Claude Code with a personal account and a work account.

Every time I switched, my local Code sessions disappeared from the sidebar.

So I built My Shared Claude: one session list across all your accounts.
• double-click setup
• preview before any change
• one-step undo
• free + open source

Live on Product Hunt today 👇
[PH link]
```

**LinkedIn**
```
Launching something small but useful today on Product Hunt 🚀

If you use Claude Code with more than one account (personal + work, or several client orgs), you've probably noticed that switching accounts swaps your entire local session list. The conversation you were just in is gone until you switch back.

My Shared Claude fixes that. It links your accounts' local Code session folders into one shared list on your machine, while keeping logins, billing, connectors and org policies separate.

I built it so non-developers on my team could run it: double-click a launcher, check a preview, type SHARE. Undo is one step too. It's free, open source, ~300 lines of Python, and tested on macOS, Windows and Linux.

Would love your feedback 👉 [PH link]

(Independent project, not affiliated with Anthropic.)
```

**Show HN (post the day after)**
```
Title: Show HN: Keep one Claude Code session list across multiple Claude accounts

Body:
Claude Desktop stores local Code sessions per account/org, so switching accounts swaps your whole sidebar. This is a ~300-line dependency-free Python helper that moves each account's session folder to a backup and replaces it with a link (symlink on macOS/Linux, junction on Windows) to one shared store. Dry-run preview, journaled setup, one-step undo. CI runs on all three OSes against Python 3.9 and 3.12.

It deliberately doesn't touch auth, cloud chats or connectors. Known limits: it depends on Desktop's on-disk layout, and Windows/Linux haven't been verified end to end with real Desktop history yet.

https://github.com/gtarun/My-Shared-Claude
```

**Reddit** (r/ClaudeAI; read the sub's self-promo rules first)
```
Title: I made a free tool so switching Claude accounts doesn't hide your Code sessions

If you use Claude Desktop's Code tab with a personal + work account, you know the sidebar shows a completely different list after switching. I wrote a small open-source helper that links them into one shared session list on your computer. Preview before changes, one-step undo, no admin rights. Logins/connectors stay separate.

Repo: https://github.com/gtarun/My-Shared-Claude
Happy to answer questions. Mac is verified, Windows/Linux testers welcome.
```
