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
        cmd = ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", line]
        subprocess.run(cmd, text=True, check=False)
