import argparse


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=str, default='gpu', help='cpu / gpu')
    parser.add_argument('--train', type=str, default='y', help='y / n')
    opt = parser.parse_args()
    return opt
