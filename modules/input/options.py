import argparse


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=str, default='gpu', help='cpu / gpu')
    opt = parser.parse_args()
    return opt
