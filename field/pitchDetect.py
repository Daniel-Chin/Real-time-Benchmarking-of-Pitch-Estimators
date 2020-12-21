print('importing...')
import pyaudio
from pyaudio import paFloat32
from time import sleep
import numpy as np

# from yin import estimateF0
# FRAME_LEN = 2048
# SR = 44100

from crepp import estimateF0, init
init('full', 'D:\\Programs\\Anaconda\\Lib\\site-packages\\crepe')
FRAME_LEN = 1024
SR = 16000

# from sft import estimateF0

def main():
  print('main()')
  pa = pyaudio.PyAudio()
  stream = pa.open(
    format = paFloat32, channels = 1, rate = SR, 
    input = True, frames_per_buffer = FRAME_LEN
  )
  try:
    while True:
      frame = getLatestFrame(stream)
      f0 = estimateF0(frame, FRAME_LEN, SR)
      pitch = freq2Pitch(f0)
      print('#' * round((pitch - 48) * 6))

  finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()

def getLatestFrame(stream):
  waste = stream.get_read_available() - FRAME_LEN
  waited = 0
  while waste < 0:
    sleep(.001)
    waited += 1
    waste = stream.get_read_available() - FRAME_LEN
  stream.read(waste)
  print('waste', waste, 'waited', waited)
  return np.array(np.frombuffer(stream.read(FRAME_LEN), dtype=np.float32))

def pitch2Freq(x):
  return np.exp(x * 0.057762265046662105 + 2.1011784386926219)

def freq2Pitch(x):
  return (np.log(x) - 2.1011784386926219) / 0.057762265046662105

main()
