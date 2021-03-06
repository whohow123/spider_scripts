# coding:utf-8
import asyncio
import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.youtube_spider import YoutubeSpider

loop = asyncio.get_event_loop()

if __name__ == "__main__":
    tasks = [
        YoutubeSpider().run(
            loop,
            datetime.date(2017, 8, i),
            datetime.date(2017, 8, i + 1)) for i in range(1, 31)]
    loop.run_until_complete(asyncio.gather(*tasks))
