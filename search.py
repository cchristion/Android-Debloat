import argparse
import json
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uad-list", type=Path, required=True)
    parser.add_argument("-p", "--phone-list", type=Path, required=True)
    args = parser.parse_args()
    return args


args = cli()
recommendations = ["Recommended", "Advanced", "Expert", "Unsafe"]

with Path.open(args.uad_list) as file:
    uad_dict = json.load(file)
    uad_packages = list(uad_dict.keys())

with Path.open(args.phone_list) as file:
    phone_packages = [line.strip() for line in file]

common_packages = list(set(uad_packages) & set(phone_packages))

to_file = {}

for package in common_packages:
    if uad_dict[package]["removal"] in to_file:
        to_file[uad_dict[package]["removal"]].append(package)
    else:
        to_file[uad_dict[package]["removal"]] = [package]

lists_path = Path("lists")
lists_path.mkdir(parents=True, exist_ok=True)

for key, value in to_file.items():
    with Path.open(lists_path / f"{key}.txt", "a") as file:
        file.writelines(f"{v}\n" for v in value)
        print(f"Wrote {lists_path/key}.txt")
