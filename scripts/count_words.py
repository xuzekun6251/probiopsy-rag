# -*- coding: utf-8 -*-
import re
t = open('outputs/paper/manuscript.en.md', encoding='utf-8').read()
m = re.search(r'## Abstract\n\n(.*?)\n\n---', t, re.S)
n = len(m.group(1).split())
main = t[t.index('## Introduction'):t.index('## Data availability')]
print('abstract words:', n)
print('main text words:', len(main.split()))
