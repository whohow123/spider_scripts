# coding:utf-8
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.youtube_spider import YoutubeSpider

loop = asyncio.get_event_loop()


def spider_youtube():
    """下载youtube视频的相关信息"""
    loop.run_until_complete(YoutubeSpider().run())


if __name__ == "__main__":
    spider_youtube()
