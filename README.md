# Android-Debloat

## Fetch all the packages from Android
adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt

## Download the uad lists
wget -O uad_lists.old.json https://raw.githubusercontent.com/0x192/universal-android-debloater/main/resources/assets/uad_lists.json
wget -O uad_lists.new.json  https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json

## search against the new lists
python search.py -p phone.txt -u uad_lists.json

## Debloat using generated list
python debloat.py -l <list>

## Clean up
rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
