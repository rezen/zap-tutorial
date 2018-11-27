#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate README based on numbered markdown files."""
from __future__ import unicode_literals
import json  # noqa: F401
from glob import iglob
import re

preamble = """
# Andres smells

""".lstrip()


toc = []
for idx, i in enumerate(sorted(iglob('*.md'))):
    v = re.split('[\W_]+', i)
    mint = v.pop(0)
    if not mint.isdigit():
        continue
    v.pop(-1)
    title = ' '.join(v).title()
    url = './{}'.format(i)
    toc.append('## [{}]({})'.format(title, url))

output = '\n'.join([preamble] + toc)
print(output)

with open('./README.md', 'w') as fh:
    fh.write(output)
