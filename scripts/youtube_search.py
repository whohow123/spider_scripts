# coding=utf-8
import sys
import os
import csv
import asyncio
import codecs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.youtube_spider import YoutubeSpider
from configure import config

loop = asyncio.get_event_loop()

class YoutubeSearch(object):
    def __init__(self):
        self.youtube_spider = YoutubeSpider()

    async def run(self):
        words = config.SEARCH_WORDS
        search_info = {
            'region_code': 'US',
            'relevance_language': 'en'
        }
        begin = '2017-08-28'
        end = '2017-08-29'

        for word in words:
            search_url = config.YOUTUBE_SEARCH_URL % \
                         (word, config.GOOGLEAPIS_KEY, search_info['region_code'],
                          search_info['relevance_language'], begin, end)

            listpagedata = await self.youtube_spider.get_data(search_url)

            if listpagedata['items']:
                with codecs.open(config.LOG_DIR+word+".csv", "w", encoding="utf-8") as datacsv:

                    i = 0
                    for item in listpagedata['items']:
                        # dialect为打开csv文件的方式，默认是excel
                        csvwriter = csv.writer(datacsv, dialect=("excel"))
                        # csv文件插入一行数据，把下面列表中的每一项放入一个单元格（可以用循环插入多行）
                        if i == 0:
                            csvwriter.writerow([
                                'title',
                                'link',
                                'screen_url'
                            ])
                        else:
                            csvwriter.writerow([
                                item['snippet']['title'],
                                config.DETAIL_YOUTUBE + item['id']['videoId'],
                                item['snippet']['thumbnails']['high']['url']
                            ])

                        i += 1

if __name__ == "__main__":
    loop.run_until_complete(YoutubeSearch().run())
