# encoding: utf-8
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ffmpy
from configure import config
import json
import subprocess
from os.path import join as pathjoin
from html import unescape
import requests
from bs4 import BeautifulSoup
import io
import logging
from src import LogFormat
from concurrent import futures

LogFormat().main()
logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')


class YoutubeSpider(object):
    """download youtube video info"""
    async def run(self, loop, begin, end):
        search_info = {
            'words': 'child',
            'lan': 'en',
            'region_code': 'US',
            'relevance_language': 'en'
        }
        search_url = config.YOUTUBE_SEARCH_URL % \
                     (search_info['words'], config.GOOGLEAPIS_KEY, search_info['region_code'],
                      search_info['relevance_language'], begin, end)

        video_list = await self.get_youtube_search_results(search_url)
        try:
            for video_id in video_list:
                video_url, title = await self.get_best_download_url(video_id)
                if video_url != "" and title != "":
                    # down youtube video caption
                    res = await self.get_video_caption(video_id, search_info, title)
                    if res is True:
                        # down youtube video as mp3 format
                        await self.multi_process_handle_mp3(loop, video_url, title)
        except Exception as e:
            logger.info("Video_id: %s error_msg: %s", video_id, e, exc_info=True)

        return

    async def multi_process_handle_mp3(self, loop, video_url, title):
        """multi process to handle computation-intensive tasks"""
        executor = futures.ProcessPoolExecutor(max_workers=5)
        await loop.run_in_executor(executor, self.get_youtube_video_as_mp3, video_url, title)

        return

    async def get_youtube_search_results(self, search_url):
        try:
            list_url = ''
            video_list = []

            while True:
                requesturl = list_url if list_url.strip() else search_url
                listpagedata = await self.get_data(requesturl)
                if listpagedata:
                    if listpagedata['items']:
                        for item in listpagedata['items']:
                            video_list.append(item['id']['videoId'])

                    if listpagedata['pageInfo']['totalResults'] > 50:
                        if listpagedata['items'] and listpagedata['nextPageToken'].strip():
                            list_url = search_url + '&pageToken=' + listpagedata['nextPageToken']
                        else:
                            break
                    else:
                        break
                else:
                    break
        except Exception as e:
            logger.info("Search_url: %s error_msg: %s", search_url, e, exc_info=True)

        return video_list

    async def get_data(self, search_url):
        r = requests.get(search_url, verify=False)
        data_list = r.content.decode('utf-8', 'ignore')
        json_data_list = json.loads(data_list)

        return json_data_list

    async def get_best_download_url(self, video_id):
        # you-get
        title = ''
        download_url = ''
        cmd = 'you-get --json '+config.DETAIL_YOUTUBE+video_id
        result = json.loads(await self.run_cmd(cmd))
        if result['streams']:
            for key, val in result['streams'].items():
                if val['container'] == 'mp4':
                    download_url = val['url']
                    break

            title = result['title']

        return download_url, title

    def get_youtube_video_as_mp3(self, *args):
        video_url = args[0]
        title = args[1]

        file_name = pathjoin(config.DOWN_DIR, title+'.mp3')

        url_path = video_url
        mp3_path = file_name

        try:
            ff = ffmpy.FFmpeg(
                inputs={url_path: None},
                outputs={mp3_path: ' -acodec libmp3lame -vn '}
            )
            ff.run()

            logger.info(title + ' === Success !')
            return True
        except ffmpy.FFRuntimeError:
            logger.info("MP4 to MP3 failed")

    async def get_video_caption(self, *args):
        # script get youtube video caption
        video_id = args[0]
        search_info = args[1]
        title = args[2]
        
        title = title.replace(':', ' -').replace('|', '-')

        # 设置要保存.srt字幕的路径
        des = config.DOWN_DIR + title + '.srt'

        # 获取自带字幕
        caption_url = config.YOUTUBE_CAPTION_URL % (search_info['lan'], video_id)

        r_caps_en_xml = requests.get(caption_url, verify=False)
        xml_content = r_caps_en_xml.content.decode('utf-8', 'ignore')
        if xml_content:
            soup_caps_en_xml = BeautifulSoup(xml_content, "lxml")
            list_data = soup_caps_en_xml.find_all('text')

            # 将XML信息转换成.srt字幕信息并打印保存成srt文件
            with open(des, 'w', encoding='utf-8') as f:
                num = 1
                for i in list_data:
                    start_time = float(i['start'])
                    end_time = float(i['start']) + float(i['dur'])
                    start_time = self.sec_to_srt_format(start_time)
                    end_time = self.sec_to_srt_format(end_time)
                    text_line = unescape(i.text).replace('\n', ' ')
                    mystr = """{var1} 
                    {var2} --> {var3} 
                    {var4}\n """.format(var1=num, var2=start_time, var3=end_time, var4=text_line)
                    f.writelines(mystr)
                    num += 1
            return True
        else:
            logger.info(video_id + ' caption xml is empty!')
            return False

    @staticmethod
    async def run_cmd(cmd):
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result_f, error_f = process.stdout, process.stderr

        errors = error_f.read()
        if errors:
            return errors
        result_str = result_f.read().strip()

        if result_f:
            result_f.close()
        if error_f:
            error_f.close()

        return result_str

    @staticmethod
    def sec_to_srt_format(t):
        tm = t * 1000
        hao = tm % 1000
        tm = tm / 1000
        miao = tm % 60
        tm = tm / 60
        fen = tm % 60
        tm = tm / 60
        shi = tm

        return "%02d:%02d:%02d,%03d" % (shi, fen, miao, hao)
