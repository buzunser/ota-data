# ota-data

This repository contains the data about current pre-releases and releases of DavinciCodeOS used in the built-in updater.

## Dependencies

For using scripts here, you need a working Python 3.9 or newer with `requests` and `tqdm` installed.

## Updating

`./update.py GITHUB_RELEASES_DOWNLOAD_LINK_FOR_ZIP`

And add `--pre` if it's a pre-release.

There are more options to speed this up, see `./update.py --help`.
