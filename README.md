# Hermes Device Sync - One Hermes on all your devices

**Author:** Francisco Moniz ([@franzmoniz](https://github.com/franzmoniz))
**License:** MIT  -  **Version:** 0.1.0

## What it does

Hermes Device Sync links all your devices (laptop, desktop, home server and, if it runs Hermes, your
phone) so they work as **one Hermes**:

1. **Shared memory**: what you teach Hermes on one device, every device knows.
2. **Your conversation follows you**: close Hermes on the laptop, open it on the desktop, and the same
   conversation continues there, with a short recap of where you stopped (the recap is optional).
3. **Same AI setup everywhere**: it checks that every device has the same AI accounts, main model and
   fallback models, and tells you exactly what is missing. You set the fallback models once and every
   device applies them.
4. **Leave work for another device**: ask for something on a device that is off or far away. It runs as
   soon as that device is on, and the result comes back to you.
5. **Optional remote control**: run things on your home PC from your laptop, at home or anywhere
   through Tailscale.

It works with 2 or more devices and syncs through a private GitHub repository of yours. The sync uses no
AI tokens.

This folder works two ways:
- a **guide for you** (this README), and
- a **skill for your Hermes agent** (`SKILL.md` plus the `scripts/`). Your Hermes installs and sets
  everything up and asks you only for the things it can't do itself.

---

## Why this exists

Each device normally runs its own Hermes. They don't know about each other. If you start something on
the laptop, the desktop has no idea. Memories you teach one device never reach the others. One device
can quietly be on a different (or worse) AI model because a login is missing, and you won't notice.

With this installed:

| Without it | With it |
|---|---|
| Every device has its own memory | Memory is merged across all devices (nothing is lost) |
| A conversation stays on the device where it started | Type `hermes` on any device and the newest conversation from ANY device continues there, with a 3-line recap of where you stopped (the recap is optional) |
| You don't notice a device missing an AI account or using another model | Every sync compares the devices and tells you exactly what is missing ("Desktop is missing AI accounts that Laptop has: copilot") |
| You set the fallback models on every device by hand | Change the fallback chain once and every device applies it |
| A device that is off can't do anything for you | Leave it a request. It runs as soon as that device is switched on, and the result comes back to you |
| No way to reach your home PC from outside | Optional: control one device from another, at home or anywhere through Tailscale |

The sync itself uses **no AI tokens**. It is plain git. Only the things you ask for (queued requests,
and the optional recap) use a model, and you choose which one.

## What you need

- Hermes installed on every device you want to link.
- A free GitHub account. Your Hermes helps you create one if you don't have it. The data lives in a
  **private** repository that only you can see.
- About 10 minutes for the first device and 5 for each extra one.
- Optional, to control a device from outside your home: a free Tailscale account.

You do NOT need git, the GitHub CLI or any other tools installed beforehand. Your Hermes installs them.

## How to install

### First device

1. Open Hermes on the device and send this message:

   > Download https://github.com/franzmoniz/hermes-device-sync (download the ZIP from GitHub if git is
   > not installed yet), install it as a skill and follow its README/SKILL.md to link this device with
   > my other devices. Assume I have nothing set up yet. Ask me whatever you need.

   If you received the folder from someone (or a ZIP), unzip it anywhere and send instead:

   > Install the skill in the folder `<path to hermes-device-sync>` and follow its SKILL.md to link this
   > device with my other devices. Assume I have nothing set up yet. Ask me whatever you need.

2. Your Hermes then walks you through these steps. These are the only things **you** have to do:
   - say which devices you want to link and give each one a short name (e.g. Laptop, Desktop, Phone);
   - say how you pay for AI (subscriptions, free plans, API keys). Hermes never adds anything paid
     without asking you;
   - create a GitHub account if you don't have one, and approve the GitHub login in your browser
     (Hermes shows you a code to type);
   - choose a name for your private sync repository (default `hermes-sync`);
   - on Windows, say yes if Hermes asks to allow PowerShell profile scripts (needed for the `hermes`
     shortcut);
   - choose your fallback models (what to use when your main model fails or runs out) and whether you
     want the conversation recap.

### Adding another device (any number of them)

On the new device, open Hermes and send:

> Link this device to my Hermes devices. The setup is in my private GitHub repo `<repo name>`, in the
> folder `hermes-sync` (follow `hermes-sync/SKILL.md` there). This device is called "<name>". Assume I
> have nothing set up yet. Ask me whatever you need.

You don't need to copy the folder again, because the first device already put the tool in your repo.
On this device you will:
- log in to GitHub with the **same** account;
- log in to the same AI providers as your other devices. Hermes tells you exactly which ones are
  missing. Each device logs in by itself, because passwords and tokens are never copied between
  devices.

### Optional: control a device from another one

Ask your Hermes: *"I want to control my <Desktop> from my <Laptop>, also when I'm not home."*
It will help you install Tailscale on both devices (with the same Tailscale account), enable a
locked-down SSH server on the device you want to control (it only accepts your own devices), and test
it. Windows asks for administrator permission once.

## Daily use

- Type `hermes` (no arguments) to open Hermes. It syncs, continues your newest conversation from any
  device, and syncs again when you exit. Use `hermes-new` for a fresh, plain Hermes.
- Talk to Hermes normally. Useful requests:
  - "Leave this for the Desktop: update all my projects and tell me what changed." It runs when the
    Desktop is on. If remote control is set up and the Desktop is on, it starts right away.
  - "Do my devices have the same setup?"
  - "Sync now."
- Everything also syncs by itself every 15 minutes while the device is on and you are logged in. You
  don't need to keep the Hermes window open.

## What your Hermes does and needs (summary of SKILL.md)

Your Hermes follows `SKILL.md` step by step. In short:

1. **Explains** what you get and asks for your devices, their names and how you pay for AI.
2. **Installs the skill** in its skills folder so it remembers how this works in future sessions.
3. **Installs tools** if missing: `git` and the GitHub CLI `gh` (winget on Windows, brew on macOS, apt
   on Linux, pkg on Termux).
4. **GitHub**: helps you create an account if needed, then runs `gh auth login` (you approve it in the
   browser) and `gh auth setup-git`.
5. **Creates your private repo** (`gh repo create <name> --private`) and clones it.
6. **Runs `scripts/setup.py`**, which on this device:
   - copies the tool into `<repo>/hermes-sync/` (first device only);
   - saves this device's name and paths in `$HERMES_HOME/hermes-sync.json`;
   - writes a tiny bootstrap `$HERMES_HOME/scripts/hermes-sync.sh` and a Hermes cron job `hermes-sync`
     (every 15 min, no agent, zero tokens);
   - adds the `hermes` shortcut to your PowerShell profile or `~/.bashrc`/`~/.zshrc`, with a backup
     of the old file;
   - runs the first sync.
7. **Makes sure the Hermes gateway runs**, because the cron job needs it (`hermes gateway install`).
8. **Sets shared settings** in `<repo>/hermes-sync/config.json` with you: fallback chain, recap
   (provider and language), rules for unattended requests.
9. **On each extra device** it repeats the tools, GitHub login, clone and setup steps, then helps you
   log in to every AI provider the other devices have, until the sync shows no differences.
10. **Optional remote control:** Tailscale, an SSH server restricted to your devices, and an SSH key
    per device (`scripts/remote.py`).

Rules your Hermes follows (from SKILL.md): it never puts passwords, keys or tokens in the repo; it
never types your passwords (you log in yourself); it never adds anything paid without asking; it backs
up files before changing them; it asks before system changes; and it never touches machines in a shared
network (for example a work Tailscale) that are not yours.

## Complete step-by-step instructions (for you and your Hermes)

This is the full procedure your Hermes follows (the same text as SKILL.md), so you can read exactly what
will happen, or do it yourself. "You" below means the Hermes agent; "the user" means you.

### Hard rules
1. Never put secrets in the repo (API keys, tokens, passwords, auth.json, .env). The repo holds names only.
   Each device logs in to its AI providers itself (`hermes auth add <provider>`).
2. Never type or store passwords yourself; the user completes logins in the browser (device codes).
3. Never add a paid model/API or enable anything that can bill the user without asking. Ask how they pay
   for AI (subscriptions, free tiers, pay-per-token) before proposing a fallback chain or the recap.
4. Back up any file you change outside the repo (`<file>.bak-YYYYMMDDHHMM`); setup.py already does this.
5. Ask before system-level changes (PowerShell execution policy, SSH server, firewall, Tailscale).
6. If a device is in someone else's network (e.g. a work/team Tailscale), never touch other people's
   machines; only talk between the user's own devices.
7. Re-read files / re-run checks before saying something is done. If a Hermes session starts with
   "No <provider> credentials found", it is silently running on a fallback model: tell the user.

### Files in this folder
- `scripts/setup.py` installer for one device (idempotent). `scripts/sync.py` one sync round.
- `scripts/memory_sync.py`, `device_check.py`, `jobs.py` (queue), `handoff.py` (conversation + recap),
  `remote.py` (SSH), `common.py`. All stdlib Python; run them with the Python that runs Hermes.
- `templates/` shell wrappers, `config.example.json`, `windows-ssh-server.ps1`, `gitignore`.
- `README.md` the human guide (show the user the relevant parts when they ask "what is this?").

### Procedure: first device

Step 0 - Explain and plan. Tell the user in 3-4 lines what they get (see README "What you get"). Ask:
(a) which devices and their OS, (b) a short unique name per device ("Laptop", "Desktop", "Phone"),
(c) how they pay for AI. Done when you have the device list and names.

Step 1 - Install the skill. If you only have the GitHub link, download
`https://github.com/franzmoniz/hermes-device-sync/archive/refs/heads/main.zip` (works without git:
`curl -L -o hds.zip <url>` or PowerShell `Invoke-WebRequest <url> -OutFile hds.zip`) and unzip it.
Copy this folder to `$HERMES_HOME/skills/hermes-device-sync/` (Windows:
`%LOCALAPPDATA%\hermes\skills\hermes-device-sync\`) if it is not there. Done when SKILL.md exists there.

Step 2 - Tools. Check with `terminal`: `git --version`, `gh --version`. Install what is missing:
- Windows: `winget install --id Git.Git -e` and `winget install --id GitHub.cli -e` (then open a new terminal)
- macOS: `brew install git gh`   - Debian/Ubuntu: `sudo apt install git gh`   - Termux: `pkg install git gh python openssh`
Done when both commands print a version.

Step 3 - GitHub account. Ask if they have one. If not: they create it at https://github.com/signup (free).
Then `gh auth login --hostname github.com --git-protocol https --web` and tell them to open the link and
type the code shown. Then `gh auth setup-git` (git then uses gh's token, which also works over SSH and
from cron without prompts). Done when `gh auth status` shows them logged in.

Step 4 - Private repo. Ask for a name (default `hermes-sync`). `gh repo create <name> --private`, then
`gh repo clone <name> <home>/<name>`. If they already have a private repo they want to reuse (e.g. notes),
that works too: the tool lives in a subfolder. Done when the clone exists. NEVER make it public.

Step 5 - Run setup. `python <this folder>/scripts/setup.py --repo <clone> --device "<name>"` using the
Python that runs Hermes (`python` usually works; on Windows the Hermes venv Python is fine).
It copies the tool into `<clone>/hermes-sync/`, writes the device config, the cron bootstrap, the
`hermes` shell wrapper and the cron job, and does the first sync. Read every `setup:` and
`hermes-sync:` line. If it warns about the PowerShell execution policy, ask the user, then run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Done when it ends with "first sync OK".

Step 6 - Make sure cron runs. The 15-minute job only runs while the Hermes gateway runs. Check
`hermes cron status` and `hermes gateway status`; if not installed: `hermes gateway install` (must be run in the user's own
desktop session, not over SSH) and start it. Done when `hermes cron list` shows `hermes-sync` and,
after its next run, "Last run: ... ok".

Step 7 - Shared settings (`<clone>/hermes-sync/config.json`, applies to ALL devices):
- `fallback_providers`: list of `{"provider","model"}` to use when the primary model fails or runs out.
  Build it only from providers the user has (`hermes auth list`) and is happy to use (rule 3). Leave
  `null` to not manage it. When set, every device applies it on its next sync (with a config backup).
- `summary`: 3-line recap shown above a resumed conversation. Costs a small model call each time the
  user exits Hermes, so enable it only with a provider the user accepts (a free one if they want zero
  cost). Set `language` to the user's language.
- `queue.rules`: extra rules for unattended requests (e.g. "never delete files outside ~/projects").
Save, then `python <clone>/hermes-sync/scripts/sync.py`. Done when the sync prints no errors.

Step 8 - Tell the user what is left: install on the other devices (next procedure). Give them the
exact prompt from README "Adding another device".

### Procedure: every other device
1. Hermes must already be installed there. Steps 2 and 3 above (tools + `gh auth login` with the SAME
   GitHub account + `gh auth setup-git`).
2. `gh repo clone <name> <home>/<name>` - the tool is already inside it (`<clone>/hermes-sync/`), so this
   device does not need the original folder: copy `<clone>/hermes-sync/` to the skills dir (Step 1).
3. `python <clone>/hermes-sync/scripts/setup.py --repo <clone> --device "<unique name>"`, then Step 6.
4. AI accounts: the sync prints `... is missing AI accounts that <device> has: x, y`. For each, guide
   the user through `hermes auth add <provider>` (or `hermes model` / the provider's login). Plugins:
   some providers need a plugin first (e.g. GitHub Copilot: `hermes plugins install github-copilot`).
   Primary model: `hermes config set model.default <model>` / `model.provider` like the other device.
5. Run `sync.py` again until it prints no "missing" / "different" lines. Done = no warnings.

### Optional: control one device from another (SSH)
Only if the user wants it (e.g. "from the laptop at school, do X on my desktop at home").
1. Same network only (home): no extra account. Anywhere: Tailscale (free personal plan). Each device:
   install (Windows `winget install --id Tailscale.Tailscale -e`, macOS/Linux see tailscale.com/download),
   then `tailscale up` and log in with the SAME account on all devices. A device can be in only ONE
   tailnet at a time: if one is already in a work/team tailnet, explain the choice (move it, or join
   the user's devices to that tailnet, or ask the tailnet owner to share a machine) and let them decide.
   If the tailnet has machines of other people: `tailscale set --accept-routes=false` and rule 6.
2. Target device needs an SSH server. Windows: elevated PowerShell
   `templates/windows-ssh-server.ps1 -AllowFrom <controller tailscale IP>` (firewall allows only the
   home LAN + those IPs). Linux: `sudo apt install openssh-server`. macOS: System Settings > Sharing >
   Remote Login. Phones: usually not a target.
3. Controller: `python scripts/remote.py keygen`, sync. Target: sync, then
   `python scripts/remote.py authorize "<controller>"` (on Windows admin accounts it tells you to rerun
   the .ps1 with `-AuthorizeKey`). Sync again so addresses are fresh.
4. Test from the controller: `remote.py check "<target>"` -> "online via ..."; then
   `echo 'hostname' | python scripts/remote.py run "<target>"`. Done when it prints the target's name.

### Day-to-day commands (run with `terminal`, paths relative to `<clone>/hermes-sync/`)
- Sync now: `python scripts/sync.py` (the user can type `Sync-Hermes` in PowerShell / `sync-hermes` in bash).
- Leave work for another device: `python scripts/jobs.py add "<device>" "<self-contained task>"`, then
  sync. If `remote.py check "<device>"` is online, also `remote.py sync "<device>"` to start it now.
  The task must be self-contained (the other Hermes has no access to this chat). Results:
  `queue/<id>.result.md`; `jobs.py list` for status. Read results to the user when sync reports them.
- Same setup everywhere? Read `devices/*.json` and run a sync; report every warning line.
- The user opens Hermes by typing `hermes` with no arguments: it syncs, resumes the newest conversation
  from any device, and syncs again on exit. `hermes-new` = a fresh Hermes without that.

### Pitfalls
- A device that lacks the primary provider runs on the fallback chain WITHOUT saying so in answers; the
  banner "No <provider> credentials found" is the only sign. Check `devices/*.json` after setup.
- Conversation hand-off uses Hermes internals (`state.db`, `hermes sessions export --format trace`,
  `hermes sessions import --from claude`). If a Hermes update changes them, sync prints
  "conversation export failed" and everything else keeps working. Hermes Desktop app chats are not handed off.
- Queue requests run with `--yolo` (no confirmations, nobody is there). Keep tasks specific; put limits
  in `queue.rules`. Do not pass `--source` to `hermes chat` (fails with invalid_params on some versions).
- Windows: the cron bootstrap is a tiny `.sh` (run by Hermes' bash); the real code lives in the repo, so
  updating the repo updates every device. Do not edit `$HERMES_HOME/scripts/hermes-sync.sh` by hand;
  rerun setup.py. PowerShell profile path may be under OneDrive (setup.py asks Windows for it).
- Windows OpenSSH ignores `~/.ssh/authorized_keys` for administrator accounts (use the .ps1). Commands
  that wait for input (git credential prompts, winget, hermes) hang over SSH: use `gh auth setup-git`
  and non-interactive flags.
- Sync conflicts inside the sync folder are auto-resolved (remote wins; memory is re-merged from the
  device's own copy). Conflicts in other files of a reused repo are reported, never auto-resolved.
- Copying `auth.json`/`.env` between devices is NOT supported: OAuth refresh tokens can rotate and
  break both devices. Log in on each device.
- Phone: works if Hermes runs on it as a normal install (e.g. Termux on Android: `pkg install python git gh`,
  run setup with the bash wrapper; the gateway must be running for cron). A phone app that cannot run
  scripts cannot join; reach the other devices through its messaging gateway instead.

### Verification
- `python scripts/sync.py` prints nothing (or only expected lines) on every device.
- `devices/` has one JSON per device with the same `providers`, `model` and `fallback`.
- `hermes cron list` shows `hermes-sync` with a recent "ok" run on every device.
- Hand-off: write one message in `hermes` on device A, exit, open `hermes` on device B: the same
  conversation resumes there.
- Queue: `jobs.py add "<B>" "Run hostname and tell me the result"` on A, sync A, sync B, wait ~1 min,
  sync B, sync A: A prints "request to B done" and the result file has B's hostname.

## What is stored where

In your private repo (`<repo>/hermes-sync/`):

- `scripts/`, `templates/`: the tool. Every device runs this copy, so an update reaches all devices.
- `config.json`: shared settings.
- `memory/`: your merged Hermes memory (`MEMORY.md`, `USER.md`).
- `devices/<name>.json`: per device, the names of the AI providers, the models, OS and network
  addresses. **No secrets.**
- `queue/`: requests between devices and their results.
- branch `hermes-sessions`: the latest conversation of each device (one file per device, overwritten
  every time, no history).

Your memory and conversations are in that repo, so keep it **private**.

On each device: `$HERMES_HOME/hermes-sync.json` (device name and paths), the bootstrap script, the cron
job, and the shortcut in your shell profile.

## Costs

- Sync, memory merge, device check and conversation hand-off: **zero tokens**.
- Queued requests: run with your normal Hermes model chain, like any message you send.
- Recap: one small model call each time you exit Hermes, and **only if you enable it**. Use a free
  model if you want zero cost.

## Troubleshooting

- Lines starting with `hermes-sync:` are the only output. Nothing printed means all is fine.
- "missing AI accounts" or "different fallback chain": log in on that device, or let the shared
  `fallback_providers` setting align them.
- "conversation export failed": a Hermes update probably changed its internal session format. Sync
  keeps working; only the conversation hand-off pauses until the tool is updated.
- Nothing syncs by itself: check that the Hermes gateway is running and that `hermes cron list` shows
  `hermes-sync`.
- Windows, `hermes` shortcut not working: the PowerShell execution policy blocks profiles
  (`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).

## Uninstall (per device)

`hermes cron list` (note the id of `hermes-sync`) and `hermes cron remove <id>`; delete the block between `# >>> hermes-device-sync >>>`
and `# <<< hermes-device-sync <<<` in your shell profile; delete `$HERMES_HOME/hermes-sync.json` and
`$HERMES_HOME/scripts/hermes-sync.sh`. Your repo and your Hermes data are not touched.

---

Made by **Francisco Moniz**. If it helps you, a star or a mention is appreciated. Issues and
improvements are welcome.
