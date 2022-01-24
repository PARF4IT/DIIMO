import math
import time
import librosa
import matplotlib.pyplot as plt
import torch
import torchaudio
import torchaudio.functional as F
import torchaudio.transforms as T
import wave
from IPython.display import Audio, display

DEFAULT_OFFSET = 100
MAX_SAMPLE_RATE = 48000
DEFAULT_LOWPASS_FILTER_WIDTH = 128
DEFAULT_RESAMPLING_METHOD = 'sinc_interpolation'
DEFAULT_ROLLOFF = 0.99


def resample(audio):
    for fa in audio:
        with wave.open(fa, "rb") as wave_file:
            frame_rate = wave_file.getframerate()

        resample_rate = 48000

        waveform = get_sine_sweep(frame_rate)
        plot_sweep(waveform, frame_rate, title="Original Waveform")\
        

        resampler = T.Resample(frame_rate, resample_rate, dtype=waveform.dtype)
        resampled_waveform = resampler(waveform)
        plot_sweep(resampled_waveform, resample_rate, title="Resampled Waveform")

        torchaudio.save(f"./data/resampled/a.wav", resampled_waveform, resample_rate)


def get_log_freq(sample_rate, max_sweep_rate, offset):
    half = sample_rate // 2
    start, stop = math.log(offset), math.log(offset + max_sweep_rate) - offset
    return torch.exp(torch.linspace(start, stop, sample_rate, dtype=torch.double)) - offset


def get_inverse_log_freq(freq, sample_rate, offset):
    half = sample_rate // 2
    return sample_rate * (math.log(1 + freq / offset) / math.log(1 + half / offset))


def get_freq_ticks(sample_rate, offset, f_max):
    time, freq = [], []
    for exp in range(2, 5):
        for v in range(1, 10):
            f = v * 10 ** exp
            if f < sample_rate // 2:
                t = get_inverse_log_freq(f, sample_rate, offset) / sample_rate
                time.append(t)
                freq.append(f)
            t_max = get_inverse_log_freq(f_max, sample_rate, offset) / sample_rate
            time.append(t_max)
            freq.append(f_max)

            return time, freq


def get_sine_sweep(sample_rate, offset=DEFAULT_OFFSET):
    max_sweep_rate = sample_rate
    freq = get_log_freq(sample_rate, max_sweep_rate, offset)
    delta = 2 * math.pi * freq / sample_rate
    cummulative = torch.cumsum(delta, dim=0)
    signal = torch.sin(cummulative).unsqueeze(dim=0)
    return signal


def plot_sweep(waveform, sample_rate, title, max_sweep_rate=MAX_SAMPLE_RATE, offset=DEFAULT_OFFSET):
    x_ticks = [100, 500, 1000, 5000, 10000, 20000, max_sweep_rate // 2]
    y_ticks = [1000, 5000, 10000, 20000, sample_rate // 2]

    time, freq = get_freq_ticks(max_sweep_rate, offset, sample_rate // 2)
    freq_x = [f if f in x_ticks and f <= max_sweep_rate // 2 else None for f in freq]
    freq_y = [f for f in freq if f >= 1000 and f in y_ticks and f <= sample_rate // 2]

    figure, axis = plt.subplots(1, 1)
    axis.specgram(waveform[0].numpy(), Fs=sample_rate)
    plt.xticks(time, freq_x)
    plt.yticks(freq_y, freq_y)
    axis.set_xlabel('Original Signal Frequency (Hz, log scale)')
    axis.set_ylabel('Waveform Frequency (Hz)')
    axis.xaxis.grid(True, alpha=0.67)
    axis.yaxis.grid(True, alpha=0.67)
    figure.suptitle(f'{title} (sample rate: {sample_rate} Hz)')
    plt.show(block=True)


def plot_specgram(waveform, sample_rate, title="Spectrogram", xlim=None):
    waveform = waveform.numpy()

    num_channels, num_frames = waveform.shape
    time_axis = torch.arange(0, num_frames) / sample_rate

    figure, axes = plt.subplots(num_channels, 1)
    if num_channels == 1:
        axes = [axes]
    for c in range(num_channels):
        axes[c].specgram(waveform[c], Fs=sample_rate)
        if num_channels > 1:
            axes[c].set_ylabel(f'Channel {c + 1}')
        if xlim:
            axes[c].set_xlim(xlim)
    figure.suptitle(title)
    plt.show(block=False)


def benchmark_resample(
        method,
        waveform,
        sample_rate,
        resample_rate,
        lowpass_filter_width=DEFAULT_LOWPASS_FILTER_WIDTH,
        rolloff=DEFAULT_ROLLOFF,
        resampling_method=DEFAULT_RESAMPLING_METHOD,
        beta=None,
        librosa_type=None,
        iters=5
):
    if method == "functional":
        begin = time.time()
        for _ in range(iters):
            F.resample(waveform, sample_rate, resample_rate, lowpass_filter_width=lowpass_filter_width,
                       rolloff=rolloff, resampling_method=resampling_method)
        elapsed = time.time() - begin
        return elapsed / iters
    elif method == "transforms":
        resampler = T.Resample(sample_rate, resample_rate, lowpass_filter_width=lowpass_filter_width,
                               rolloff=rolloff, resampling_method=resampling_method, dtype=waveform.dtype)
        begin = time.time()
        for _ in range(iters):
            resampler(waveform)
        elapsed = time.time() - begin
        return elapsed / iters
    elif method == "librosa":
        waveform_np = waveform.squeeze().numpy()
        begin = time.time()
        for _ in range(iters):
            librosa.resample(waveform_np, sample_rate, resample_rate, res_type=librosa_type)
        elapsed = time.time() - begin
        return elapsed / iters
