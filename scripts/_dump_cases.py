# -*- coding: utf-8 -*-
import json, glob
for p in sorted(glob.glob('outputs/demo_cases/*.json')):
    d = json.load(open(p, encoding='utf-8'))
    print('==', d['case_id'], '|', d['title'])
    print('Q:', d['question'])
    print('verdict:', d['verdict']['action'], 'conf', d['verdict']['confidence'],
          '| items:', d['decision_items'])
    print()
