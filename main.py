import asyncio
from time import time

import aiohttp

from civitai.network.cookies import cookies
from civitai.network.downloader import File, get_image_html
from civitai.network.infinite import InfiniteLoader, Input
from civitai.network.parser import extract_mantine_class


def catch_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            # You can add more handling here if needed

    return wrapper


@catch_errors
async def download_file(
    session: aiohttp.ClientSession, id: int, out_dir: str, sem: asyncio.Semaphore
):
    async with sem:
        image_html = await get_image_html(session, id)
        url = extract_mantine_class(image_html)[0]
        start = time()
        saved_path, downloaded = await File.download(session, url, out_dir, f"{id}")
        duration = time() - start
        msg = "Save" if downloaded else "Skip"
        print(f"[{id}] {msg} '{saved_path}' in {duration:.2f}s")


async def download_n_files(
    n: int, out_dir: str, tags: list[int] | None = None, max_workers: int = 5
):
    async with aiohttp.ClientSession(cookies=cookies) as session:
        infinite_loader = InfiniteLoader(session)

        input = Input.new(tags=tags)
        while n > 0:
            page = await infinite_loader.load_page(input)
            input = input.next(page.nextCursor)  # update input immediatly
            print(f"Loaded {len(page.ids)} ids. {n} files left to download.")

            batch = []
            sem = asyncio.Semaphore(max_workers)  # limit number of concurrent downloads
            while len(page.ids) > 0 and n > 0:
                id = page.ids.pop(0)
                batch.append(download_file(session, id, out_dir, sem=sem))
                n -= 1
            await asyncio.gather(*batch)


if __name__ == "__main__":
    asyncio.run(download_n_files(500, "output", tags=[113935]))
