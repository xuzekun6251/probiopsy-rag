# -*- coding: utf-8 -*-
for f in ['outputs/paper/02_results.md', 'outputs/paper/04_discussion.md']:
    print('=' * 20, f)
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        if line.startswith('#'):
            print(i, line.rstrip())
