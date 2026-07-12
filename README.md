# Android-Debloat

### Fetch all the packages from Android
```bash
adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt
```

### Download the UAD lists
```bash
wget -O uad_lists.old.json https://raw.githubusercontent.com/0x192/universal-android-debloater/main/resources/assets/uad_lists.json
wget -O uad_lists.new.json https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/refs/heads/main/resources/assets/uad_lists.json
```

### Search against the new lists
```bash
python search.py -p phone.txt -u uad_lists.json
```

### Debloat using generated list
```bash
python debloat.py -l <list>
```

### Clean up
```bash
rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
```
