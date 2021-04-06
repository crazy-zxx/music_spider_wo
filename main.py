#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""酷我音乐搜索下载"""

__author__ = 'xylx'

import align_print
import requests
import json
import time
import urllib.parse
import re

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Cookie': 'kw_token=SHA96IGVU9K',
    'Accept-Language': 'zh-cn',
    'Host': 'www.kuwo.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'csrf': 'SHA96IGVU9K'
}


# 按歌曲名称搜索，并返回搜索结果的list
def music_search():
    key = input('请输入搜索的歌名（无输入将退出）：')
    if key is None or key.strip() == '':
        exit(0)
    key = key.strip()

    url = ' https://www.kuwo.cn/api/www/search/searchMusicBykeyWord?'
    headers['Referer'] = 'https://www.kuwo.cn/search/list?key=' + urllib.parse.quote(key)
    para_data = {
        'key': key,  # 歌曲名
        'pn': 1,  # 页码
        'rn': 30,  # 每页条目数
        'httpsStatus': 1
    }
    response = requests.get(url=url, headers=headers, params=para_data)
    search_json = json.loads(response.text.encode('utf-8'))
    data = search_json.get('data').get('list')

    result = []
    for d in data:
        result.append({
            'rid': d.get('rid'),  # 歌曲id，用于下载
            'name': d.get('name'),  # 歌曲名
            'album': d.get('album'),  # 歌曲专辑
            'artist': d.get('artist'),  # 歌手
            'songTimeMinutes': d.get('songTimeMinutes')  # 时长
        })
    return result


# 格式化输出搜索到的歌曲信息
def music_show(result):
    if len(result) > 0:
        print('序号\t歌名\t\t\t\t\t\t\t\t\t\t\t专辑\t\t\t\t\t\t\t\t\t\t\t歌手\t\t\t\t\t时长')

        i = 0  # 计数
        for r in result:
            i += 1
            # 获取指定长度且末尾补齐空格的字符串
            mid = align_print.align_string(str(i), 4)
            name = align_print.align_string(r['name'], 50)
            album = align_print.align_string(r['album'], 50)
            artist = align_print.align_string(r['artist'], 20)
            song_time_minutes = align_print.align_string(r['songTimeMinutes'], 10)
            print(mid + ' ' + name + ' ' + album + ' ' + artist + ' ' + song_time_minutes)

        music_download(result)

    else:
        print('没有找到！')


# 下载音乐
def music_download(result):
    select = input('输入下载的序号（0返回搜索；多个序号用逗号隔开）：')
    s_list = re.split(r'[,，]', select)

    try:
        for s in s_list:
            index = int(s)
            if index == 0:
                return
            if index < 1 or index > len(result):
                raise ValueError()

            url = 'https://www.kuwo.cn/url?'
            para_data = {
                'format': 'mp3',
                'rid': result[index - 1]['rid'],
                'response': 'url',
                'type': 'convert_url3',
                'br': '128kmp3',
                'from': 'web',
                't': str(int(time.time() * 1000)),
                'httpsStatus': '1'
            }
            response = requests.get(url=url, headers=headers, params=para_data)
            if response.status_code == 200:
                download_url = json.loads(response.text.encode('utf-8')).get('url')
                download_response = requests.get(url=download_url)
                if download_response.status_code == 200:
                    with open(result[index - 1]['name'] + '-' + result[index - 1]['artist'] + '.mp3', 'wb') as f:
                        f.write(download_response.content)
                    print(str(index) + ' 下载完成！')
                else:
                    print('解析失败')
            else:
                print('解析失败')

    except ValueError as e:
        print('无效输入！')
        music_download(result)


if __name__ == "__main__":
    while True:
        result = music_search()
        music_show(result)
