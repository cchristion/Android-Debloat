import argparse
import subprocess
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", type=Path, required=True)
    args = parser.parse_args()
    return args


args = cli()

with open(args.list) as file:
    for line in file:
        line = line.strip()
        print(f"{line}:")
        cmds = [
            ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", line],
            ["adb", "shell", "pm", "clear", line],
            [
                "adb",
                "shell",
                "cmd",
                "appops",
                "set",
                line,
                "RUN_IN_BACKGROUND",
                "ignore",
            ],
            ["adb", "shell", "pm", "hide", line],
            ["adb", "shell", "pm", "suspend", line],
        ]
        for c in cmds:
            subprocess.run(c, text=True, check=False)
