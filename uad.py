#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

URL = "https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json"
TIERS = ("Recommended", "Advanced", "Expert", "Unsafe")

log = logging.getLogger("uad")


class UAD:
    def __init__(
        self, serial: str | None = None, cache_dir: Path | None = None
    ) -> None:
        self.serial = serial
        base = (
            cache_dir
            or Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "uad"
        )
        self.cache = base / "uad_lists.json"

    def adb(self, *args: str) -> tuple[bool, str]:
        cmd = ["adb", *(["-s", self.serial] if self.serial else []), *args]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return res.returncode == 0, (res.stdout or res.stderr).strip()

    def rules(self, update: bool = False) -> dict[str, dict]:
        if update or not self.cache.exists():
            log.info("Downloading UAD rules from GitHub...")
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            raw = urllib.request.urlopen(URL, timeout=30).read()
            data = json.loads(raw)
            tmp = self.cache.with_suffix(".tmp")
            tmp.write_bytes(raw)
            tmp.replace(self.cache)
            log.info("Saved %d rules to %s", len(data), self.cache)
            return data

        data = json.loads(self.cache.read_text(encoding="utf-8"))
        log.info("Loaded %d cached rules from %s", len(data), self.cache)
        return data

    def installed(self) -> set[str]:
        target = f"device {self.serial}" if self.serial else "default ADB device"
        log.info("Querying installed packages on %s...", target)
        ok, out = self.adb("shell", "pm", "list", "packages", "--user", "0")
        if not ok:
            raise RuntimeError(out or "ADB error")
        pkgs = {
            line.removeprefix("package:").strip()
            for line in out.splitlines()
            if line.startswith("package:")
        }
        log.info("Found %d installed packages", len(pkgs))
        return pkgs

    def scan(
        self, tiers: set[str] | None = None, update: bool = False
    ) -> list[tuple[str, dict]]:
        allowed = tiers if tiers is not None else {"Recommended"}
        active = [t for t in TIERS if t in allowed]
        data = self.rules(update=update)
        pkgs = self.installed()
        log.info("Filtering packages for tiers: %s", ", ".join(active))
        matches = sorted(
            (pkg, data[pkg])
            for pkg in pkgs
            if pkg in data and data[pkg].get("removal") in allowed
        )
        log.info("Matched %d packages", len(matches))
        return matches

    def debloat(self, pkg: str) -> dict[str, tuple[bool, str]]:
        log.info("Debloating %s", pkg)
        steps = {
            "clear": ("shell", "pm", "clear", pkg),
            "bg1": (
                "shell",
                "cmd",
                "appops",
                "set",
                pkg,
                "RUN_IN_BACKGROUND",
                "ignore",
            ),
            "bg2": (
                "shell",
                "cmd",
                "appops",
                "set",
                pkg,
                "RUN_ANY_IN_BACKGROUND",
                "ignore",
            ),
            "hide": ("shell", "pm", "hide", pkg),
            "uninstall": ("shell", "pm", "uninstall", "--user", "0", pkg),
        }
        results: dict[str, tuple[bool, str]] = {}
        for name, cmd in steps.items():
            ok, out = self.adb(*cmd)
            results[name] = (ok, out)
            status = "OK" if ok else "FAIL"
            log.info("  [%s] %s: %s", status, name, out or "done")
        return results


def parse_selection(raw: str, total: int) -> list[int]:
    token = raw.strip().lower()
    if not token:
        return []
    if token == "all":
        return list(range(total))
    indices: list[int] = []
    seen: set[int] = set()
    for part in token.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if start < 1 or end > total or start > end:
                raise ValueError(f"Range out of bounds: {part}")
            items = range(start - 1, end)
        else:
            idx = int(part)
            if idx < 1 or idx > total:
                raise ValueError(f"Index out of bounds: {part}")
            items = (idx - 1,)
        for i in items:
            if i not in seen:
                seen.add(i)
                indices.append(i)
    return indices


def run_cli(uad: UAD, targets: list[tuple[str, dict]]) -> None:
    print()
    for i, (pkg, meta) in enumerate(targets, start=1):
        tier = meta.get("removal", "")
        desc = " ".join(meta.get("description", "").split())
        print(f"[{i}] {pkg} [{tier}]")
        if desc:
            print(f"    {desc}")

    try:
        raw = input(
            "\nSelect packages to debloat (e.g. 1,3-5 | all | Enter to cancel): "
        )
        selected_idx = parse_selection(raw, len(targets))
    except (KeyboardInterrupt, EOFError):
        print()
        log.info("Cancelled by user")
        return
    except ValueError as exc:
        log.error("Invalid selection: %s", exc)
        return

    if not selected_idx:
        log.info("No packages selected")
        return

    total = len(selected_idx)
    for pos, i in enumerate(selected_idx, start=1):
        pkg = targets[i][0]
        log.info("[%d/%d] Processing %s", pos, total, pkg)
        uad.debloat(pkg)
    log.info("Completed %d package(s)", total)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stdout
    )

    p = argparse.ArgumentParser(prog="uad.py")
    p.add_argument("-s", "--serial", help="ADB device serial")
    p.add_argument("--update", action="store_true", help="Refresh cached UAD list")
    p.add_argument(
        "--tier",
        nargs="+",
        choices=TIERS,
        default=["Recommended"],
        help="Removal tiers (default: Recommended)",
    )
    args = p.parse_args()

    uad = UAD(serial=args.serial)
    try:
        targets = uad.scan(set(args.tier), update=args.update)
    except (RuntimeError, urllib.error.URLError, json.JSONDecodeError) as exc:
        log.error("%s", exc)
        return 1

    if not targets:
        log.info("No matching packages found")
        return 0

    run_cli(uad, targets)
    return 0


if __name__ == "__main__":
    sys.exit(main())
