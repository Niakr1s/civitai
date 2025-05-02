import asyncio
import json
from abc import abstractmethod
from copy import deepcopy

import aiohttp

INFINITE_REQUEST_URL = "https://civitai.com/api/trpc/image.getInfinite"


class Input:
    _meta = {"values": {"cursor": ["undefined"]}}

    def __init__(self, input: dict):
        self.input = input

    @abstractmethod
    def new(tags: list | None = None, cursor: str | None = None) -> "Input":
        if tags is None:
            tags = []

        input = {
            "json": {
                "period": "Week",
                "sort": "Most Reactions",
                "types": ["video"],
                "tags": tags,
                "useIndex": True,
                "browsingLevel": 31,
                "include": ["cosmetics"],
                "excludedTagIds": [306619, 5351, 154326, 161829, 163032, 5188],
                "disablePoi": True,
                "disableMinor": True,
                "cursor": cursor,
                "authed": True,
            },
        }
        if cursor is None:
            input["meta"] = Input._meta

        return Input(input=input)

    def next(self, cursor: str) -> "Input":
        input = deepcopy(self.input)
        input["json"]["cursor"] = cursor
        if "meta" in input:
            del input["meta"]
        return Input(input=input)

    def to_str(self) -> str:
        return json.dumps(self.input, separators=(",", ":"), ensure_ascii=True)


class Page:
    def __init__(self, nextCursor: str, ids: list[int]):
        self.nextCursor = nextCursor
        self.ids = ids


class InfiniteLoader:
    headers = {
        "Accept": "/",
        "Accept-Encoding": "gzip, deflate, zstd",
        "Content-Type": "application/json",
        "Origin": "https://civitai.com",
        "Referer": "https://civitai.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    }

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def load_page(self, input: Input) -> Page:
        async with self.session.get(
            INFINITE_REQUEST_URL,
            params={"input": input.to_str()},
            headers=InfiniteLoader.headers,
        ) as resp:
            data = await resp.json()
            nextCursor = data["result"]["data"]["json"]["nextCursor"]
            ids = [item["id"] for item in data["result"]["data"]["json"]["items"]]
            return Page(nextCursor, ids)


async def main():
    input = Input.new()
    async with aiohttp.ClientSession() as session:
        for i in range(3):
            page = await InfiniteLoader(session).load_page(input)
            print(page.nextCursor, page.ids, len(page.ids))
            input = input.next(page.nextCursor)


if __name__ == "__main__":
    asyncio.run(main())
