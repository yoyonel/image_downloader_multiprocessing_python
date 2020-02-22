# -*- coding: utf-8 -*-
import argparse
import collections
import io
import logging
import pathlib
import random
from functools import partial
from multiprocessing.pool import ThreadPool
from typing import List

import requests
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("image_downloader::multi_processing")


def get_download_location(url_input: str):
    name = url_input.split('.')[0]
    pathlib.Path(name).mkdir(parents=True, exist_ok=True)
    return name


def get_urls(url_input: str) -> List[str]:
    """
    Returns a list of urls by reading the txt file supplied as argument in terminal
    """
    with open(url_input, 'r') as f:
        images_url = f.read().splitlines()

    logger.info('{} Images detected'.format(len(images_url)))
    return images_url


def image_downloader(img_url: str, url_input: str) -> bool:
    """
    Input:
    param: img_url  str (Image url)
    Tries to download the image url and use name provided in headers. Else it randomly picks a name
    """
    logger.info(f'Downloading: {img_url}')
    res = requests.get(img_url, stream=True)
    # count = 1
    # while res.status_code != 200 and count <= 5:
    #     res = requests.get(img_url, stream=True)
    #     print(f'Retry: {count} {img_url}')
    #     count += 1
    # checking the type for image
    if 'image' not in res.headers.get("content-type", ''):
        logger.error("ERROR: URL doesn't appear to be an image")
        return False
    # Trying to red image name from response headers
    try:
        image_name = str(img_url[(img_url.rfind('/')) + 1:])
        if '?' in image_name:
            image_name = image_name[:image_name.find('?')]
    except:
        image_name = str(random.randint(11111, 99999)) + '.jpg'

    i = Image.open(io.BytesIO(res.content))
    download_location = get_download_location(url_input)
    i.save(download_location + '/' + image_name)

    logger.info('Download complete: %s', img_url)
    return True


def run_downloader(process: int, images_url: list, url_input: str):
    """
    Inputs:
        process: (int) number of process to run
        images_url:(list) list of images url
    """
    logger.info('MESSAGE: Running %s process', process)
    it_mp_imap = ThreadPool(process).imap_unordered(partial(image_downloader, url_input=url_input), images_url)
    # https://github.com/python/cpython/blob/v3.6.5/Modules/_collectionsmodule.c#L356
    collections.deque(it_mp_imap, maxlen=0)


def build_parser():
    """

    Returns:

    """
    parser = argparse.ArgumentParser(
        description='MultiProcess Image downloader',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required
    parser.add_argument("url_input",
                        type=str,
                        help="txt file (example: cats.txt)")

    #
    parser.add_argument("num_process",
                        nargs='?',
                        type=int,
                        default=10,
                        help="Number of process")

    parser.add_argument("--export_dir",
                        type=str,
                        default="cats",
                        help="Export directory")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    images_url = get_urls(args.url_input)
    run_downloader(args.num_process, images_url, args.url_input)


if __name__ == "__main__":
    main()
