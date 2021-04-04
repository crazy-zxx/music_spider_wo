#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""酷我音乐搜索下载"""

__author__ = 'xylx'

import requests
import json
import time
import urllib.parse
import re


def get_str_width(string):
    """获取字符串字节数"""
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
        (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
        (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
        (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
        (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
        (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    width = 0
    for each in string:
        if ord(each) == 0xe or ord(each) == 0xf:
            each_width = 0
            continue
        elif ord(each) <= 1114109:
            for num, wid in widths:
                if ord(each) <= num:
                    each_width = wid
                    width += each_width
                    break
            continue

        else:
            each_width = 1
        width += each_width

    if string.encode('UTF-8').isalpha():
        width = width + 1

    return width


def align_string(string, width):
    """字符串按指定宽度对齐"""
    string_width = get_str_width(string)
    if width > string_width:
        return string + ' ' * (width - string_width)
    else:
        return string


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


def music_search():
    """按歌曲名称搜索，并返回搜索结果的list"""
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


def music_show(result):
    """格式化输出搜索到的歌曲信息"""
    print('序号\t歌名\t\t\t\t\t\t\t\t专辑\t\t\t\t\t\t歌手\t\t\t时长')
    if len(result) > 0:
        i = 0  # 计数
        for r in result:
            i += 1
            # 获取指定长度且末尾补齐空格的字符串
            mid = align_string(str(i), 4)
            name = align_string(r['name'], 60)
            album = align_string(r['album'], 50)
            artist = align_string(r['artist'], 30)
            song_time_minutes = align_string(r['songTimeMinutes'], 10)
            print(mid + ' ' + name + ' ' + album + ' ' + artist + ' ' + song_time_minutes)

        music_download(result)

    else:
        print('没有找到！')


def music_download(result):
    """下载音乐"""
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
                'rid': result[index]['rid'],
                'response': 'url',
                'type': 'convert_url3',
                'br': '128kmp3',
                'from': 'web',
                't': str(int(time.time() * 1000)),
                'httpsStatus': '1'
            }
            response = requests.get(url=url, headers=headers, params=para_data)
            download_url = json.loads(response.text.encode('utf-8')).get('url')
            download_response = requests.get(url=download_url)

            with open(result[index]['name'] + '-' + result[index]['artist'] + '.mp3', 'wb') as f:
                f.write(download_response.content)
            print(str(index) + ' 下载完成！')

    except ValueError as e:
        print('无效输入！')
        music_download(result)


if __name__ == "__main__":
    while True:
        result = music_search()
        music_show(result)
