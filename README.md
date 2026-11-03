# Android-Debloat

## TODO

- Make everything a single script
- Option to view what being purged

## Init tools on ubuntu

```shell
sudo apt install adb fastboot
adb start-server
```

## Fetch all the packages from Android

```shell
adb shell "(pm list packages -u)" | cut -s -f 2 -d ":" > phone.txt
```

## Download the UAD lists

```shell
uv run --with requests download_uad.py
```

## Search against the new lists

```shell
uv run search.py -p phone.txt -u uad.json
```

## Debloat using generated list

```shell
uv run debloat.py -l <list>
```

## Clean up

```shell
rm Advanced.txt Recommended.txt Unsafe.txt Expert.txt
```
