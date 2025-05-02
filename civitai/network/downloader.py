import asyncio
from abc import abstractmethod
from pathlib import Path

import aiohttp

URL = ""


class File:
    @abstractmethod
    def suggested_extension(content_type: str) -> str:
        return content_type.split("/")[-1] if "/" in content_type else ""

    @abstractmethod
    async def download(
        session: aiohttp.ClientSession,
        url: str,
        save_dir: str,
        filename: str,
        skip_if_exists: bool = True,
    ) -> tuple[Path, bool]:
        async with session.get(url) as resp:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)

            filename = Path(filename)

            content_type = resp.content_type
            ext = File.suggested_extension(content_type)
            save_path = save_dir / f"{filename}.{ext}"
            if skip_if_exists and save_path.exists():
                return (save_path, False)

            data = await resp.read()
            with open(save_path, "wb") as f:
                f.write(data)
            return (save_path, True)


async def get_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as resp:
        return await resp.text()


IMAGE_HTML_URL = "https://civitai.com/images/"


async def get_image_html(session: aiohttp.ClientSession, id: int) -> str:
    async with session.get(IMAGE_HTML_URL + str(id)) as resp:
        return await resp.text()


async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/7a5b840d-8b03-499f-9510-507963f870c8/transcode=true,original=true,quality=90/Professional_Mode__transparent_submarine_with_a_gl.mp4"
        file = await File.download(session, url)
        file.save_to(Path("."), "submarine")


if __name__ == "__main__":
    asyncio.run(main())
