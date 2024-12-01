# !/usr/bin/env python3

import nbformat

filename = '/autograder/submission/action_castle.ipynb'

f = open(filename)
notebook = nbformat.read(f, as_version=4)
codes = []
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        code = cell['source']
        if 'game.game_loop()' in code:
            code = code.replace('game.game_loop()', '# game.game_loop()')
        codes.append(code)

print('\n'.join(codes))
with open('/autograder/source/action_castle.py', 'w+') as file:
    file.write('\n'.join(codes))
