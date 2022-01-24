import torch
import torchaudio
import torchaudio.functional as F
import torchaudio.transforms as T
from modules.utility import audioresample
import os
import glob


def run(args):
    worker = str(args[0])
    train = str(args[1])

    if train == "y":
        print(worker)

        print(torch.__version__)
        print(torchaudio.__version__)

        file_list_wav = glob.glob("./data/*.wav")
        print(file_list_wav)
        audioresample.resample(file_list_wav)
    else:
        pass
