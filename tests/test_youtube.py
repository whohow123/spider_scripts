# coding:utf-8
import asyncio
import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.youtube_spider import YoutubeSpider
from multiprocessing import Pool

loop = asyncio.get_event_loop()

def spider_youtube(day_str):
    """下载youtube视频的相关信息"""
    begin = datetime.date(2017, 8, day_str)
    end = datetime.date(2017, 8, day_str+1)
    loop.run_until_complete(YoutubeSpider().run(begin, end))

if __name__ == "__main__":
    pool = Pool(processes=5)
    pool.map_async(spider_youtube, range(1, 31))
    pool.close()
    pool.join()
