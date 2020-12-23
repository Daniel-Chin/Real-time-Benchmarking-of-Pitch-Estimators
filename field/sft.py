import numpy as np
from numpy import pi
from numpy.fft import rfft
import scipy.signal
from blindDescend import blindDescend

def init(frame_len, sr, upper_limit = 1600):
    global arange_size, hann, hann_half, \
    COEF_freq2Bin, PROD_freqWithCpesBin, \
    LEFT_TRIM, half_frame_len
    
    half_frame_len = frame_len // 2
    arange_size = np.arange(half_frame_len)
    hann = scipy.signal.get_window('hann', frame_len, True)
    hann_half = scipy.signal.get_window('hann', half_frame_len, True)
    COEF_freq2Bin = frame_len / sr
    PROD_freqWithCpesBin = sr / 2
    LEFT_TRIM = int(PROD_freqWithCpesBin / upper_limit) + 1

def getRotator(bin_period, size):
    coef = pi * 2j * bin_period / size
    return np.exp(arange_size * coef)

def sft(signal, size, bin):
    # Slow Fourier Transform
    return np.abs(np.sum(signal * getRotator(bin, size))) / size

def refineGuess(guess, guess_score, hanned_spectrum):
    def loss(x):
        return - sft(
            hanned_spectrum, half_frame_len, 
            x,
        )
    return blindDescend(loss, .01, .4, guess)[0]

def estimateF0(frame, frame_len, sr):
    hanned_spectrum = np.abs(rfft(frame * hann))[:-1] * hann_half
    cepstrum = np.abs(rfft(hanned_spectrum))
    guess = np.argmax(cepstrum[LEFT_TRIM:]) + LEFT_TRIM
    return PROD_freqWithCpesBin / refineGuess(
    guess, cepstrum[guess], hanned_spectrum
    )
