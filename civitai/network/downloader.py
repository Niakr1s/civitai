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

    def save_to(self, dir: Path, filename: str, extension: str | None = None):
        if extension is None:
            extension = self.suggested_extension()
        with open(dir / f"{filename}.{extension}", "wb") as f:
            f.write(self.data)

    @abstractmethod
    async def download(session: aiohttp.ClientSession, url: str) -> "File":
        async with session.get(url) as resp:
            content_type = resp.content_type
            data = await resp.read()
            return File(data, content_type)


async def main():
    async with aiohttp.ClientSession() as session:
        url = "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/7a5b840d-8b03-499f-9510-507963f870c8/transcode=true,original=true,quality=90/Professional_Mode__transparent_submarine_with_a_gl.mp4"
        file = await File.download(session, url)
        file.save_to(Path("."), "submarine")


if __name__ == "__main__":
    asyncio.run(main())
