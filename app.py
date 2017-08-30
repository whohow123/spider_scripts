# coding:utf-8
import asyncio
import datetime
import sys

from scripts.youtube_spider import YoutubeSpider

loop = asyncio.get_event_loop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        op_type = sys.argv[1]
        tasks = [
            YoutubeSpider().run(
                sys.argv[1],
                loop,
                datetime.date(2017, 8, i),
                datetime.date(2017, 8, i + 1)) for i in range(1, 31)]
        loop.run_until_complete(asyncio.gather(*tasks))
    else:
        print('Error input, op_type is empty !')
