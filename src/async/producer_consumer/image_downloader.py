# -*- coding: utf-8 -*-
import asyncio

import aiofiles
import argparse
import random
import time
from aiohttp import ClientSession
from aiologger import Logger
from aiologger.formatters.base import Formatter
from pathlib import Path

from src.tools.async_producer_consumer import ASyncProducerConsumer, async_consumer

aio_logger = Logger.with_default_handlers(name='aio_image_downloader',
                                          formatter=Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

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


async def export_img(img_url, img_data):
    fn_export_img = build_img_export_name(img_url)
    aio_logger.info(f"Write img to: {fn_export_img} ...")
    async with aiofiles.open(fn_export_img, mode='wb') as f:
        await f.write(img_data)
    glob_configs["nb_img_downloaded"] += 1


async def fetch_img_data(url, session):
    img_data = None
    await aio_logger.info(f"Fetch img at: {url} ...")
    async with session.get(url) as response:
        if response.status == 200:
            if 'image' in response.headers.get("content-type", ''):
                img_data = await response.read()
            else:
                await aio_logger.warning(f"content at {url} not image type (content-type={response.headers.get('content-type', '')})")
        else:
            await aio_logger.warning(f"Can't fetch img at: {url} - status: {response.status} (!= 200)")
    return img_data, url


async def run(img_urls):
    await aio_logger.info(f"Nb url images: {len(img_urls)}")

    producers_consumers = ASyncProducerConsumer()

    queue_img_urls = asyncio.Queue()
    queue_img_data = asyncio.Queue()

    client_session = ClientSession()

    async def _consume_img_url_and_fetch_img():
        async def func_apply_on_item(img_url):
            return await fetch_img_data(img_url, client_session)

        await async_consumer(queue_img_urls, queue_img_data, func_apply_on_item)

    async def _consume_img_data_and_save_it():
        async def func_apply_on_item(img_url):
            img_data, img_url = await fetch_img_data(img_url, client_session)
            await export_img(img_url, img_data)

        await async_consumer(queue_img_urls, queue_img_data, func_apply_on_item)

    async def _produce_img_urls():
        for img_url in img_urls:
            await queue_img_urls.put(img_url)

    producers_consumers.add('fetch_img',
                            queue_img_urls, _consume_img_url_and_fetch_img)
    producers_consumers.add('export_img',
                            queue_img_data, _consume_img_data_and_save_it)

    event_loop = asyncio.get_event_loop()

    # create a future on task that ending "quickly"
    future_task = event_loop.create_task(_produce_img_urls())

    # wait until the consumer has processed all items
    await producers_consumers.join()

    while (future_task.done() is False or
           not queue_img_data.empty() or
           not queue_img_urls.empty()):
        await asyncio.wait_for(queue_img_data.get(), timeout=None)


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
    start = time.time()
    main()
    end = time.time()
    print(f'Time taken to download {glob_configs["nb_img_downloaded"]}')
    print(end - start)
