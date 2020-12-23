print('importing...')
import pyaudio
from pyaudio import paFloat32
from time import time
import numpy as np

# YIN
# FRAME_LEN = 2048
# SR = 44100
# from yin import estimateF0

# CREPE
# FRAME_LEN = 1024
# SR = 16000
# from crepp import estimateF0, init
# init('full', 'D:\\Programs\\Anaconda\\Lib\\site-packages\\crepe')

# SFT
# FRAME_LEN = 2048
# SR = 44100
# from sft import estimateF0, init
# init(FRAME_LEN, SR)

def main():
  print('main()')
  pa = pyaudio.PyAudio()
  stream = pa.open(
    format = paFloat32, channels = 1, rate = SR, 
    input = True, frames_per_buffer = FRAME_LEN
  )
  try:
    while True:
      start = time()
      frame = getLatestFrame(stream)
      mid = time()
      f0 = estimateF0(frame, FRAME_LEN, SR)
      # f0 = 220
      pitch = freq2Pitch(f0)
      end = time()
      print('Breathing room', format((mid - start) / (end - start), '.0%'))
      print('#' * round((pitch - 48) * 6))
  except KeyboardInterrupt:
    pass
  finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    print('Resources released. ')

def getLatestFrame(stream):
  waste = stream.get_read_available() - FRAME_LEN
  if waste > 0:
    print('Samples dropped', waste)
    stream.read(waste)
  return np.frombuffer(
    stream.read(FRAME_LEN), dtype = np.float32
  )

def pitch2Freq(x):
  return np.exp(x * 0.057762265046662105 + 2.1011784386926219)

def freq2Pitch(x):
  return (np.log(x) - 2.1011784386926219) / 0.057762265046662105

main()
