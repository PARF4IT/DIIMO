import os


def make():
    if not os.path.isdir('data'):
        os.mkdir('data')
