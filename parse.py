#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import jieba
import thulac
import collections
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def parse():
	stop_list = [l.strip().decode('utf8') for l in open('ENstopwords.txt').readlines()]
	stop_list += [l.strip().decode('utf8') for l in open('CNstopwords.txt').readlines()]
	counter = collections.Counter()
	cur_counter = collections.Counter()
	#thu = thulac.thulac(filt=True, T2S=True, seg_only=True)
	for root, dirs, files in os.walk('data/'):    
		for f in files:            
			for line in open(os.path.join(root, f)).readlines():
				if not line.strip():
					for k, v in cur_counter.most_common():
						if v > 5:
							cur_counter[k] = 5
					counter.update(cur_counter)
					cur_counter = collections.Counter()
				line = line.replace('\xc2\xa0', '').replace('\xe3\x80\x80', '')
				if line[0].isalpha() and line[len(line) / 2].isalpha():
					cut_list = filter(lambda x: not x in stop_list, \
						[_.lower().decode('utf8') for _ in line.strip().split()])
					if cut_list:
						cur_counter.update(cut_list)
					continue
				cut_list = jieba.cut(line.strip().lower().decode('utf8'))
				cut_list = filter(lambda x: not x in stop_list, cut_list)
				cur_counter.update(cut_list)

	cloud_list = []
	del counter[' ']
	wc = WordCloud().generate_from_frequencies(dict(counter.most_common(50)))
 
	plt.imshow(wc)
	plt.axis("off")
	plt.show()
	plt.savefig('houyao.png')


if __name__ == '__main__':
	parse()

