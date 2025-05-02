import asyncio
from abc import abstractmethod
from pathlib import Path

import aiohttp

URL = ""


class File:
    def __init__(self, data: bytes, content_type: str):
        self.data = data
        self.content_type = content_type

    def suggested_extension(self) -> str:
        return self.content_type.split("/")[-1] if "/" in self.content_type else ""

    def save_to(self, dir: Path, filename: str, extension: str | None = None) -> Path:
        if extension is None:
            extension = self.suggested_extension()

        dir = Path(dir)
        dir.mkdir(parents=True, exist_ok=True)

        save_path = dir / f"{filename}.{extension}"
        with open(save_path, "wb") as f:
            f.write(self.data)
        return save_path

    @abstractmethod
    async def download(session: aiohttp.ClientSession, url: str) -> "File":
        async with session.get(url) as resp:
            content_type = resp.content_type
            data = await resp.read()
            return File(data, content_type)


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
