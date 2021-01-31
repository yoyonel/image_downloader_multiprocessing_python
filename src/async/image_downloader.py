# -*- coding: utf-8 -*-
import asyncio

import aiofiles
import argparse
import logging
import random
import tqdm
from aiohttp import ClientSession
from aiologger import Logger
from aiologger.formatters.base import Formatter
from pathlib import Path

from tools.aiohttp_ignore_ssl_error import ignore_aiohttp_ssl_error

aio_logger = Logger.with_default_handlers(
    name='aio_image_downloader',
    # formatter=Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter=Formatter(fmt='%(message)s'),
    level=logging.INFO,
)

glob_configs = {"export_dir": Path("cats")}


def build_img_export_name(img_url) -> Path:
    try:
        image_name = str(img_url[(img_url.rfind('/')) + 1:])
        if '?' in image_name:
            image_name = image_name[:image_name.find('?')]
    except:
        image_name = str(random.randint(11111, 99999)) + '.jpg'
    return glob_configs["export_dir"] / image_name


async def load_and_export_img(img_url, response) -> bool:
    export_img = build_img_export_name(img_url)
    async with aiofiles.open(export_img, mode='wb') as f:
        await f.write(await response.read())
    await aio_logger.debug(f'Download complete: {img_url}')
    return True


async def fetch(img_url, session) -> bool:
    await aio_logger.debug(f'Downloading: {img_url}')
    async with session.get(img_url) as response:
        if response.status != 200:
            await aio_logger.warning(f"Can't fetch img at: {img_url} - status: {response.status} (!= 200)")
            return False
        if 'image' not in response.headers.get("content-type", ''):
            await aio_logger.warning(f"content at {img_url} not image type (content-type={response.headers.get('content-type', '')})")
            return False
        return await load_and_export_img(img_url, response)


async def run(img_urls):
    await aio_logger.info(f"Nb url images: {len(img_urls)}")
    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        tasks = [asyncio.ensure_future(fetch(img_url, session)) for img_url in img_urls]
        # https://stackoverflow.com/questions/37901292/asyncio-aiohttp-progress-bar-with-tqdm
        nb_img_downloaded = sum([await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks))])
    aio_logger.info(f"Nb img downloaded: {nb_img_downloaded}/{len(img_urls)}")


def build_parser():
    """

    Returns:

    """
    parser = argparse.ArgumentParser(description='AIO Image downloader')

    # Required
    parser.add_argument("url_input",
                        type=argparse.FileType(mode='r'),
                        help="txt file (example: cats.txt)")

    #
    parser.add_argument("--export_dir",
                        type=str,
                        default="cats",
                        help="Export directory (default: %(default)s)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    glob_configs["export_dir"] = Path(args.export_dir)

    with args.url_input as io_urls_img:
        urls_img = io_urls_img.read().splitlines()

    loop = asyncio.get_event_loop()
    ignore_aiohttp_ssl_error(loop)
    future = asyncio.ensure_future(run(urls_img))
    loop.run_until_complete(future)


if __name__ == '__main__':
    main()
