# Android-Debloat

## Init tools on ubuntu

```shell
sudo apt install adb fastboot
adb start-server
```

### New Way, using AI

```shell
uv run --script uad.py --tier Recommended --tier Advanced --tier Expert
```

### Old Way

```shell
# Fetch all the packages from Android
adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt

# Download the UAD lists
uv run --with requests download_uad.py

# Search against the new lists
uv run search.py -p phone.txt -u uad.json

# Debloat using generated list
uv run debloat.py -l <list>

# Clean up
rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
```
