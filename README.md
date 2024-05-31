# Android-Debloat

adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt

curl -O https://raw.githubusercontent.com/0x192/universal-android-debloater/main/resources/assets/uad_lists.json

python search.py -p phone.txt -u uad_lists.json

rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
