import asyncio
from time import time

import aiohttp

from civitai.cmd.args import args
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


# If n is 0 or None, download infinite files
async def download_n_files(
    n: int | None, out_dir: str, tags: list[int] | None = None, max_workers: int = 5
):
    def have_iterations(n: int | None) -> bool:
        return n is None or n > 0

    def remained_str(n: int | None) -> str:
        return "'inf'" if n is None else n

    if n == 0:
        n = None

    print(
        f"Starting download {remained_str(n)} files to '{out_dir}' directory with tags: {tags} concurrently with {max_workers} workers..."
    )

    async with aiohttp.ClientSession(cookies=cookies) as session:
        infinite_loader = InfiniteLoader(session)

        input = Input.new(tags=tags)
        while have_iterations(n):
            page = await infinite_loader.load_page(input)
            input = input.next(page.nextCursor)  # update input immediatly

            print(
                f"Loaded next batch with {len(page.ids)} ids. {remained_str(n)} files left to download."
            )

            batch = []
            sem = asyncio.Semaphore(max_workers)  # limit number of concurrent downloads
            while len(page.ids) > 0 and have_iterations(n):
                id = page.ids.pop(0)
                batch.append(download_file(session, id, out_dir, sem=sem))
                if n is not None:
                    n -= 1
            await asyncio.gather(*batch)


if __name__ == "__main__":
    asyncio.run(
        download_n_files(
            n=args.num_files,
            out_dir=args.out_dir,
            tags=args.tags,
            max_workers=args.max_workers,
        )
    )
