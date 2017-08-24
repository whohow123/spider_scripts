# encoding: utf-8
from html import unescape
import requests
from bs4 import BeautifulSoup
import io
import sys

requests.packages.urllib3.disable_warnings()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')


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


youtubeUrl = 'https://www.youtube.com/watch?v=yx9dRL1BCCQ'

# 获取视频的标题信息
r = requests.get(youtubeUrl, verify=False)
soup = BeautifulSoup(r.content.decode('utf-8', 'ignore'))
youtubeTitle = soup.find('title').text.replace(':', ' -').replace('|', '-')

# 设置要保存.srt字幕的路径
des = '/Users/whohow/videos/' + youtubeTitle + '.srt'

# 获取自带字幕
ttsUrl = 'http://video.google.com/timedtext?lang=en&v=yx9dRL1BCCQ'
r_caps_en_xml = requests.get(ttsUrl, verify=False)
soup_caps_en_xml = BeautifulSoup(r_caps_en_xml.content.decode('utf-8', 'ignore'))
list_data = soup_caps_en_xml.find_all('text')

# 将XML信息转换成.srt字幕信息并打印保存成srt文件
with open(des, 'w', encoding='utf-8') as f:
    num = 1
    for i in list_data:
        start_time = float(i['start'])
        end_time = float(i['start']) + float(i['dur'])
        start_time = sec_to_srt_format(start_time)
        end_time = sec_to_srt_format(end_time)
        text_line = unescape(i.text).replace('\n', ' ')
        mystr = """{var1} 
        {var2} --> {var3} 
        {var4}\n """.format(var1=num, var2=start_time, var3=end_time, var4=text_line)
        f.writelines(mystr)
        num += 1
