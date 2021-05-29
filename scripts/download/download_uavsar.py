import requests
import os
from os.path import join, isdir, isfile, basename
import progressbar


def stream_download(url, output_f):
    """

    Args:
        url: url to download
        output_f: path to save the data to

    """
    print(f"\n\nDownloading {url}\nSaving to {output_f}")
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        with open(output_f, 'wb') as f:
            for i, chunk in enumerate(r):
                f.write(chunk)
                bar.update(i)
    else:
        print(f"HTTP CODE {r.status_code}. Skipping download!")
