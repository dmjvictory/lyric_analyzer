#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import thulac
import pprint
import chardet
import requests
import collections 
from lxml import etree
from selenium import webdriver


re_pattern = re.compile(ur'[\[\(（].*?[\]\)）]')
headers = \
    {'User-Agent': \
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
     'Host': 'music.163.com'}


def down(url):
	browser = webdriver.PhantomJS()
	browser.get(url)
	html = browser.execute_script("return document.documentElement.innerHTML")
	return etree.HTML(html.encode('utf8'))


def down2(url):
	html = requests.get(url).text
	return etree.HTML(html.encode('utf8'))


def extract_lyric(url):
	root = down2(url)
	lyric = eval(root.xpath('//body/p[1]')[0].text.encode('raw_unicode_escape').\
				replace('false', 'False').\
				replace('null', 'None').\
				replace('true', 'True'))
	try:
		lines = lyric['lrc']['lyric'].split('\n')
	except Exception as e:
		return
	lyrics = []
	for line in lines:
		lyric = re_pattern.sub('', line)
		if lyric and '作词' not in lyric and '作曲' not in lyric and \
		             '编曲' not in lyric and '：' not in lyric:
			lyrics.extend([lyric])
	return lyrics


def extract_song_list():
	singer_map = {
		'11830': '海龟先生', 
		'13223': '万年青年旅店',
		'11760': '后海大鲨鱼',
		'12971': '痛仰',
		'11679': 'GALA',
		'12977': '逃跑计划',
		'11238': '刺猬',
		'12465': '南无',
		'13585': '指人儿'}

	for i in singer_map:
		url = 'http://music.163.com/artist?id=%s' % i 
		song_map = {}
		song_list = []
		root = down2(url)
		for a in root.xpath('//ul[@class="f-hide"][1]/li/a'):
			song_id = a.get('href')[9:]
			song = re_pattern.sub('', a.text)
			song = re.sub(ur'\xa0', '', song)
			if not song in song_map:
				song_map[song] = song_id
			else:
				continue
			song_url = 'http://music.163.com/api/song/lyric?id=' + str(song_id) + '&lv=1&kv=1&tv=-1'
			lyrics = extract_lyric(song_url)
			if lyrics is not None:
				with open('data/%s.lrc' % singer_map[i], 'a') as writer:
					writer.write(song.encode('utf8') + '\n')
					writer.write('\n'.join(lyrics) + '\n\n')					
					
		
if __name__ == '__main__':
    #extract_lyric('http://music.163.com/api/song/lyric?id=191232&lv=1&kv=1&tv=-1')
	extract_song_list()



