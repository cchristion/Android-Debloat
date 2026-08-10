# Android-Debloat

### Init tools on ubuntu
```bash
sudo apt install adb fastboot
adb start-server
```


### Fetch all the packages from Android
```bash
adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt
```

### Download the UAD lists
```bash
python download_uad.py
```

### Search against the new lists
```bash
python search.py -p phone.txt -u uad.json
```

### Debloat using generated list
```bash
python debloat.py -l <list>
```

### Clean up
```bash
rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
```