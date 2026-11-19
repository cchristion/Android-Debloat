#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import parse_qs
import urllib.request
import webbrowser

URL = "https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json"
TIERS = ("Recommended", "Advanced", "Expert", "Unsafe")


class UAD:
    def __init__(self, serial: str | None = None, cache_dir: Path | None = None, mock: bool = False) -> None:
        self.serial = serial
        self.mock = mock
        base = cache_dir or Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "uad"
        self.cache = base / "uad_lists.json"

    def adb(self, *args: str) -> tuple[bool, str]:
        if self.mock:
            return True, "Success [MOCK]"
        cmd = ["adb", *(["-s", self.serial] if self.serial else []), *args]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.returncode == 0, (res.stdout or res.stderr).strip()

    def rules(self, update: bool = False) -> dict[str, dict]:
        if update or not self.cache.exists():
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            raw = urllib.request.urlopen(URL, timeout=30).read()
            json.loads(raw)
            tmp = self.cache.with_suffix(".tmp")
            tmp.write_bytes(raw)
            tmp.replace(self.cache)
        return json.loads(self.cache.read_text(encoding="utf-8"))

    def installed(self, data: dict[str, dict] | None = None) -> set[str]:
        if self.mock:
            return set(list((data or self.rules()).keys())[:50])
        ok, out = self.adb("shell", "pm", "list", "packages", "--user", "0")
        if not ok:
            raise RuntimeError(out or "ADB error")
        return {line.removeprefix("package:").strip() for line in out.splitlines() if line.startswith("package:")}

    def scan(self, tiers: set[str] | None = None, update: bool = False) -> list[tuple[str, dict]]:
        allowed = tiers or {"Recommended"}
        data = self.rules(update=update)
        return sorted((pkg, data[pkg]) for pkg in self.installed(data) if pkg in data and data[pkg].get("removal") in allowed)

    def debloat(self, pkg: str) -> dict[str, str]:
        steps = {
            "clear": ("shell", "pm", "clear", pkg),
            "bg1": ("shell", "cmd", "appops", "set", pkg, "RUN_IN_BACKGROUND", "ignore"),
            "bg2": ("shell", "cmd", "appops", "set", pkg, "RUN_ANY_IN_BACKGROUND", "ignore"),
            "hide": ("shell", "pm", "hide", pkg),
            "uninstall": ("shell", "pm", "uninstall", "--user", "0", pkg),
        }
        return {k: self.adb(*cmd)[1] for k, cmd in steps.items()}


def run_checklist(uad: UAD, targets: list[tuple[str, dict]]) -> None:
    rows = "\n".join(
        f'<div style="border-bottom:1px solid #ddd;padding:10px 0">'
        f'<label><input type="checkbox" name="pkg" value="{html.escape(pkg)}"> '
        f'<b>{html.escape(pkg)}</b> [{html.escape(meta.get("removal", ""))}]</label> '
        f'<a href="https://play.google.com/store/apps/details?id={html.escape(pkg)}" target="_blank">Play Store</a>'
        f'<p style="margin:4px 0 0 22px;color:#444">{html.escape(meta.get("description", ""))}</p></div>'
        for pkg, meta in targets
    )
    page = (
        f"<!doctype html><html><body style='font-family:sans-serif;max-width:860px;margin:20px auto'>"
        f"<form method='POST'><button type='submit' style='padding:10px 16px;font-size:16px'>Uninstall Selected</button>"
        f"{rows}</form></body></html>"
    )

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", 0))
            selected = parse_qs(self.rfile.read(length).decode("utf-8")).get("pkg", [])
            results = "\n".join(f"{pkg}: {uad.debloat(pkg)}" for pkg in selected) or "No packages selected."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(results.encode("utf-8"))
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, *args: object) -> None:
            pass

    srv = HTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{srv.server_port}"
    print(f"Checklist open: {url} (Ctrl+C to cancel)")
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def main() -> int:
    p = argparse.ArgumentParser(prog="uad.py")
    p.add_argument("-s", "--serial")
    p.add_argument("--update", action="store_true")
    p.add_argument("--tier", action="append", choices=TIERS)
    p.add_argument("--mock", action="store_true", help="Test UI without an ADB device")
    args = p.parse_args()

    uad = UAD(serial=args.serial, mock=args.mock)
    targets = uad.scan(set(args.tier or ["Recommended"]), update=args.update)
    if not targets:
        print("No matching packages.")
        return 0
    run_checklist(uad, targets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
