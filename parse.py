#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import jieba
import thulac
import numpy as np
import collections
import pandas as pd
#from snownlp import SnowNLP
from scipy.misc import imread
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
stop_list = [l.strip().decode('utf8') for l in open('ENstopwords.txt').readlines()]
stop_list += [l.strip().decode('utf8') for l in open('CNstopwords.txt').readlines()]


def self_cut(line, filt=True):
	line = line.replace('\xc2\xa0', '').replace('\xe3\x80\x80', '')
	if line[0].isalpha() and line[len(line) / 2].isalpha():
		cut_list = [_.lower().decode('utf8') for _ in line.strip().split()]
		if filt:
			cut_list = filter(lambda x: not x in stop_list, cut_list)
		return cut_list
	cut_list = jieba.cut(line.strip().lower().decode('utf8'))
	if filt:
		cut_list = filter(lambda x: not x in stop_list, cut_list)
	return [_ for _ in cut_list]


def word_parse():
	counter = collections.Counter()
	cur_counter = collections.Counter()
	#thu = thulac.thulac(filt=True, T2S=True, seg_only=True)
	if 1:#for root, dirs, files in os.walk('data/'):    
		if 1:#for f in files:            
			#for line in open(os.path.join(root, f)).readlines():
			for line in open('data/all.lrc').readlines():
				if not line.strip():
					for k, v in cur_counter.most_common():
						if v > 5:
							cur_counter[k] = 5
					counter.update(cur_counter)
					cur_counter = collections.Counter()
				cut_list = self_cut(line)
				if len(cut_list) > 0:
					cur_counter.update(cut_list)

	cloud_list = []
	del counter[' ']
	back = imread('yellowman.jpg')
	wc = WordCloud(mask=back, background_color='white', \
			width=1200, height=800).generate_from_frequencies(dict(counter.most_common(75)))
 
	#plt.imshow(wc)
	#plt.axis("off")
	#plt.show()
	wc.to_file('rock.jpg')


def emotion_parse():
	reverse_dict = set([l.strip().decode('utf8') for l in \
						open('emotion/reverse.txt').readlines()])
	pos_dict = set([l.strip().decode('utf8') for l in \
						open('emotion/positive.txt').readlines()])
	neg_dict = set([l.strip().decode('utf8') for l in \
						open('emotion/negative.txt').readlines()])
	level_words = [l.strip() for l in \
						open('emotion/level.txt').readlines()]
	mostdict = level_words[level_words.index('extreme') + 1: \
						level_words.index('very')] #权重4，即在情感前乘以3
	verydict = level_words[level_words.index('very') + 1: \
						level_words.index('more')] #权重3
	moredict = level_words[level_words.index('more') + 1: \
						level_words.index('ish')] #权重2
	ishdict = level_words[level_words.index('ish') + 1: \
						level_words.index('last')] #权重0.5
	level_dict = dict([(_.decode('utf8'), 4) for _ in mostdict])
	level_dict = dict([(_.decode('utf8'), 3) for _ in verydict] + level_dict.items())
	level_dict = dict([(_.decode('utf8'), 2) for _ in moredict] + level_dict.items())
	level_dict = dict([(_.decode('utf8'), 0.5) for _ in ishdict] + level_dict.items())

	data = []
	label = []
	for root, dirs, files in os.walk('data/'):
		for f in files:
			if not f in ['old.lrc', 'new.lrc']:
				score = [0, 0]
				wordcount = 0
				for line in open(os.path.join(root, f)).readlines():
					if not line.strip():
						continue
					'''s = SnowNLP(line.strip().decode('utf8'))
					if s.sentiments > 0.6:
						score[0] += 1
					elif s.sentiments < 0.4:
						score[1] += 1'''
					
					pos, neg = 0, 0
					wordcount += len(line.strip().decode('utf8'))
					cut_list = self_cut(line, False)
					for i, word in enumerate(cut_list):
						if word in pos_dict:
							pos = 1
							if i > 0 and cut_list[i - 1] in level_dict:
								pos = pos * level_dict[cut_list[i - 1]]
							if i < len(cut_list) - 1: 
								if cut_list[i + 1] in ['!'.decode('utf8'), '！'.decode('utf8')]:
									pos += 2

						if word in neg_dict:
							neg = 1
							if i > 0 and cut_list[i - 1] in level_dict:
								neg = neg * level_dict[cut_list[i - 1]]
							if i < len(cut_list) - 1:
								if cut_list[i + 1] in ['!'.decode('utf8'), '！'.decode('utf8')]:
									neg += 2
					score[0] += pos
					score[1] += neg
					
				label.append(f[: -4])
				data.append([np.log(1.0 * score[0] / score[1]),
							 np.exp(100.0 * (score[0] + score[1]) / wordcount)])

		df = pd.DataFrame(np.array(data), columns=['emotion', 'tension'], index=label)
		fig = plt.figure(figsize=(15, 12))
		ax1 = fig.add_subplot(2,1,1)
		ax2 = fig.add_subplot(2,1,2)

		df.emotion.plot(kind='bar', ax=ax1, title=u'情绪分析')
		df.tension.plot(kind='bar', ax=ax2, title=u'情绪强度')
		ax1.set_ylim([-1, 2.5])
		ax1.set_xticklabels([_.decode('utf8') for _ in label], rotation = 40)
		ax1.text(-1.8, 2.6, u'正面')
		ax1.text(-1.8, -1.2, u'负面')
		ax2.set_xticklabels([_.decode('utf8') for _ in label], rotation = 40)
		#plt.show()
		plt.savefig('emotion.jpg')

if __name__ == '__main__':
	word_parse()
	#emotion_parse()

