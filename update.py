#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from tqdm import tqdm

OS_NAME = "PixelExperience"

CHUNK_SIZE = 1024 * 1024 * 4  # 4MB

DEVICE_DATA = {
    "error": False,
    "version": "twelve",
    "maintainers": [
        {
            "main_maintainer": True,
            "github_username": "buzunser",
            "name": "buzunser",
        },
        {
            "main_maintainer": True,
            "github_username": "buzunser",
            "name": "buzunser",
        },
    ],
    "donate_url": "",
    "website_url": "https://github.com/buzunser/",
    "news_url": "",
    "datetime": None,  # To be filled in
    "filename": None,  # To be filled in
    "id": None,  # To be filled in
    "size": None,  # To be filled in
    "url": None,  # To be filled in
    "filehash": None,  # To be filled in
}


def parse_filename(zip_url: str) -> str:
    url = urlparse(zip_url)
    file_name = os.path.basename(url.path)

    return file_name


def generate_datetime(date: str, time: str) -> int:
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:])
    hour = int(time[:2])
    minute = int(time[2:])

    dt = datetime(
        year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=timezone.utc
    )
    timestamp = int(dt.timestamp())

    return timestamp


def get_file_data(file_url: str, file_path: str | None) -> bytes:
    if file_path is None:
        res = requests.get(file_url, allow_redirects=True, stream=True)
        total_size = int(res.headers.get("content-length", 0))
        content = bytearray()
        progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True)

        for data in res.iter_content(CHUNK_SIZE):
            progress_bar.update(len(data))
            content.extend(data)

        return bytes(content)
    else:
        with open(file_path, "rb") as file:
            return file.read()


def write_data(device: str, pre: bool) -> None:
    filename = f"{device}.json" if not pre else f"{device}_pre.json"

    with open(filename, "w") as file:
        json.dump(DEVICE_DATA, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the OTA data for a device.")
    parser.add_argument("zip_url", nargs="?", help="static link to the flashable zip")
    parser.add_argument(
        "--local-file",
        type=str,
        nargs="?",
        required=False,
        help="path to local version of flashable zip (else will be downloaded)",
    )
    parser.add_argument("--pre", action="store_true", help="this is a pre-release")

    args = parser.parse_args()

    print("Parsing filename...")

    filename = parse_filename(args.zip_url)

    print("Validating extension...")

    if filename[-4:] != ".zip":
        raise ValueError("Provided URL does not end in .zip")

    parts = filename[:-4].split("-")

    print("Validating file name...")

    if len(parts) != 5:
        raise ValueError("Filename does not contain exactly 5 parts")

    name, version, date, time, build_type = parts
    os_name, device_name = name.split("_")

    print("Validating OS name...")

    if os_name != OS_NAME:
        raise ValueError(f"File is for {os_name}, not {OS_NAME}")

    print("Generating UNIX timestamp...")

    dt = generate_datetime(date, time)

    print("Downloading or opening ZIP...")

    file_content = get_file_data(args.zip_url, args.local_file)
    size = len(file_content)

    print("Generating MD5 hash...")

    md5 = hashlib.md5(file_content).hexdigest()
    id = hashlib.md5(filename.encode("utf-8")).hexdigest()

    DEVICE_DATA["url"] = args.zip_url
    DEVICE_DATA["filename"] = filename
    DEVICE_DATA["id"] = id
    DEVICE_DATA["datetime"] = dt
    DEVICE_DATA["size"] = size
    DEVICE_DATA["filehash"] = md5

    print("Writing JSON...")

    write_data(device_name, args.pre)

    print(f"Please now update {device_name}_changelog.txt!")
