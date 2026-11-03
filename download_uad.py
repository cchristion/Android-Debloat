import json
import requests

url_new = "https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json"
url_old = "https://raw.githubusercontent.com/0x192/universal-android-debloater/main/resources/assets/uad_lists.json"

data_new = requests.get(url_new).json()
data_old = requests.get(url_old).json()

for i in data_old:
    if i["id"] in data_new:
        continue
    else:
        data_new[i["id"]] = i

with open("uad.json", "w", encoding="utf-8") as file:
    json.dump(data_new, file, indent=4)

print("Downloaded, merged and saved to uad.json")
