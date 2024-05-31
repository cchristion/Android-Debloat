import argparse
from pathlib import Path


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uad-list", type=Path, required=True)
    parser.add_argument("-p", "--phone-list", type=Path, required=True)
    args = parser.parse_args()
    return args


recommendations = ["Recommended", "Advanced", "Expert", "Unsafe"]
args = cli()

with open(args.uad_list) as file:
    content = file.read()
content = eval(content)

with open(args.phone_list) as file:
    phone_packages = [line.strip() for line in file]

lists_path = Path("lists")
lists_path.mkdir(parents=True, exist_ok=True)

for rec in recommendations:
    print(f"Writing: {rec}")
    with open(lists_path / f"{rec}.txt", "w") as file:
        for entry in content:
            if entry["removal"] == rec and entry["id"] in phone_packages:
                file.write(f"{entry['id']}\n")
