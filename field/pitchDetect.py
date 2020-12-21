import pyaudio
from pyaudio import paFloat32
from time import sleep

from yin import estimatePitch

FRAME_LEN = 2048
SR = 44100

def main():
  pa = pyaudio.PyAudio()
  stream = pa.open(
    format = paFloat32, channels = 1, rate = SR, 
    input = True, frames_per_buffer = FRAME_LEN
  )
  try:
    while True:
      frame = getLatestFrame(stream)
      estimatePitch(frame, FRAME_LEN, SR)
  finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()

def getLatestFrame(stream):
  waste = stream.get_read_available() - FRAME_LEN
  while waste < 0:
    sleep(.001)
    waste = stream.get_read_available() - FRAME_LEN
  stream.read(waste)
  print('waste', waste)
  return stream.read(FRAME_LEN)

main()
