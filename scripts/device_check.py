"""Checks that all devices have the same AI setup, and applies the shared fallback chain.

Every device writes <data dir>/devices/<device>.json with NAMES ONLY (never keys or tokens):
providers with credentials, primary model, fallback chain, OS, and how to reach it over SSH.
Then it compares itself with every other device and prints a warning for each difference.

If config.json has "fallback_providers" (a list), it is applied to this device with
`hermes config set` (a backup of config.yaml is made first). So changing the chain once in
the repo changes it on every device, even devices you are away from.
"""
import getpass, json, os, platform, re, shutil, socket, subprocess, time
from pathlib import Path
from common import HH, data_dir, device, shared_cfg, hermes, read_json, write_json, out, strip_ansi

CACHE = HH / "cache" / "hermes-sync-device.json"


def _signature():
    sig = []
    for f in ("config.yaml", "auth.json", ".env"):
        try:
            sig.append(os.path.getmtime(HH / f))
        except OSError:
            sig.append(0)
    return sig


def _collect_ai():
    """providers / model / fallback, using the Hermes CLI (cached until config/auth files change)."""
    cache = read_json(CACHE, {})
    if cache.get("sig") == _signature() and cache.get("ai"):
        return cache["ai"]
    rc, txt = hermes("auth", "list")
    providers = sorted(set(re.findall(r"^(\S+) \(\d+ credentials?\):", strip_ansi(txt), re.M)))
    _, model = hermes("config", "get", "model.default")
    _, mprov = hermes("config", "get", "model.provider")
    _, fb = hermes("config", "get", "fallback_providers", "--json")
    try:
        fallback = [f"{x['provider']}/{x['model']}" for x in (json.loads(strip_ansi(fb).strip().splitlines()[-1]) or [])]
    except (ValueError, IndexError, KeyError, TypeError):
        fallback = []
    last = lambda s: (strip_ansi(s).strip().splitlines() or [""])[-1].strip()
    ai = {"providers": providers, "model": last(model), "model_provider": last(mprov), "fallback": fallback}
    if rc == 0:
        write_json(CACHE, {"sig": _signature(), "ai": ai})
    return ai


def _apply_fallback(want, have):
    names = [f"{w['provider']}/{w['model']}" for w in want]
    if names == have:
        return False
    cfg = HH / "config.yaml"
    if cfg.exists():
        shutil.copy2(cfg, cfg.with_name("config.yaml.bak-" + time.strftime("%Y%m%d%H%M")))
    rc, txt = hermes("config", "set", "fallback_providers",
                     json.dumps([{"provider": w["provider"], "model": w["model"]} for w in want]))
    if rc:
        out("could not apply the shared fallback chain: " + strip_ansi(txt)[-200:])
        return False
    out(f"fallback chain of {device()} updated from config.json: " + " -> ".join(names))
    return True


def _lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip if not ip.startswith(("127.", "100.")) else None
    except OSError:
        return None


def _tailscale_ip():
    exe = shutil.which("tailscale")
    if not exe and os.name == "nt" and os.path.exists(r"C:\Program Files\Tailscale\tailscale.exe"):
        exe = r"C:\Program Files\Tailscale\tailscale.exe"
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "ip", "-4"], capture_output=True, text=True, timeout=10)
        ip = r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else None
        return ip
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return None


def _ssh_server():
    try:
        with socket.create_connection(("127.0.0.1", 22), timeout=1):
            return True
    except OSError:
        return False


def _reach():
    pub = Path.home() / ".ssh" / "hermes_sync.pub"
    bash = None
    if os.name == "nt":
        git_exe = shutil.which("git")
        cands = [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe",
                 *sorted((HH / "tools").glob("git-*/usr/bin/bash.exe"))]
        if git_exe:  # <git>/cmd/git.exe -> <git>/bin/bash.exe or <git>/usr/bin/bash.exe
            root = Path(git_exe).resolve().parent.parent
            cands += [root / "bin" / "bash.exe", root / "usr" / "bin" / "bash.exe"]
        for c in cands:
            if c.exists():
                bash = str(c)
                break
    return {
        "os": "windows" if os.name == "nt" else platform.system().lower(),
        "user": getpass.getuser(),
        "lan_ip": _lan_ip(),
        "tailscale_ip": _tailscale_ip(),
        "ssh_server": _ssh_server(),
        "ssh_pubkey": pub.read_text(encoding="utf-8").strip() if pub.exists() else None,
        "bash": bash,
        "sync_script": str(HH / "scripts" / "hermes-sync.sh"),
    }


def run():
    me = device()
    cfg = shared_cfg()
    ai = _collect_ai()
    want = cfg.get("fallback_providers")
    if isinstance(want, list) and want and _apply_fallback(want, ai["fallback"]):
        CACHE.unlink(missing_ok=True)
        ai = _collect_ai()
    info = {"device": me, **ai, **_reach(), "last_seen": time.strftime("%Y-%m-%d")}
    ddir = data_dir() / "devices"
    write_json(ddir / f"{me}.json", info)

    for f in sorted(ddir.glob("*.json")):
        o = read_json(f, {})
        name = o.get("device") or f.stem
        if name == me:
            continue
        missing = sorted(set(o.get("providers", [])) - set(ai["providers"]))
        if missing:
            out(f"{me} is missing AI accounts that {name} has: {', '.join(missing)} "
                f"(log in here with: hermes auth add <provider>)")
        if o.get("model") and o.get("model") != ai["model"]:
            out(f"different primary model: {me}={ai['model'] or '?'} vs {name}={o['model']}")
        if o.get("fallback") != ai["fallback"]:
            out(f"different fallback chain between {me} and {name} "
                f"({' -> '.join(ai['fallback']) or 'none'} vs {' -> '.join(o.get('fallback') or []) or 'none'})")


if __name__ == "__main__":
    run()
