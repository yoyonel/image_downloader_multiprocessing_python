# -*- coding: utf-8 -*-
import asyncio

import aiofiles
import argparse
import random
from aiohttp import ClientSession
from aiologger import Logger
from aiologger.formatters.base import Formatter
from pathlib import Path

aio_logger = Logger.with_default_handlers(
    name='aio_image_downloader',
    # formatter=Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter=Formatter(fmt='%(message)s')
)

glob_configs = {
    "export_dir": Path("cats"),
    "nb_img_downloaded": 0,
}


def build_img_export_name(img_url) -> Path:
    try:
        image_name = str(img_url[(img_url.rfind('/')) + 1:])
        if '?' in image_name:
            image_name = image_name[:image_name.find('?')]
    except:
        image_name = str(random.randint(11111, 99999)) + '.jpg'

    return glob_configs["export_dir"] / image_name


async def load_and_export_img(img_url, response):
    export_img = build_img_export_name(img_url)
    async with aiofiles.open(export_img, mode='wb') as f:
        await f.write(await response.read())
    glob_configs["nb_img_downloaded"] += 1
    await aio_logger.info(f'Download complete: {img_url}')


async def fetch(img_url, session):
    await aio_logger.info(f'Downloading: {img_url}')
    async with session.get(img_url) as response:
        if response.status == 200:
            if 'image' in response.headers.get("content-type", ''):
                await load_and_export_img(img_url, response)
            else:
                await aio_logger.warning(f"content at {img_url} not image type (content-type={response.headers.get('content-type', '')})")
        else:
            await aio_logger.warning(f"Can't fetch img at: {img_url} - status: {response.status} (!= 200)")


async def run(img_urls):
    await aio_logger.info(f"Nb url images: {len(img_urls)}")

    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for img_url in img_urls:
            task = asyncio.ensure_future(fetch(img_url, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


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
    future = asyncio.ensure_future(run(urls_img))
    loop.run_until_complete(future)


if __name__ == '__main__':
    main()
