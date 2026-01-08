# Bunkr Album Downloader

Simple CLI tool to download full Bunkr albums.

## Usage

### Run in CLI
Run the script directly. You will be prompted for the album URL and an optional download path.
```bash
python bunkr_downloader.py
```

### Run as Import
Import script and run main(), provide URL and (optionally) download path.
Note: if no path given, then input() called, if no input() given, then defaults tothe  current path.

```python
from bunkr_downloader import main

main(
    url="https://bunkr.example/album",
    download_path="./downloads"
)
```
