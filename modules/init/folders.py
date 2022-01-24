import os


def make():
    if not os.path.isdir('data'):
        os.mkdir('data')

    if not os.path.isdir('data/resampled'):
        os.mkdir('data/resampled')
