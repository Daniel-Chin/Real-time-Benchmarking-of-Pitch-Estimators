import pyaudio
from pyaudio import paFloat32

CHUNK = 2048
SR = 44100

def main():
  pa = pyaudio.PyAudio()
  stream = pa.open(
    format = paFloat32, channels = 1, rate = SR, 
    input = True, frames_per_buffer = CHUNK
  )
  try:
    while True:
      frame = getLatestFrame(stream)
      estimatePitch(frame, CHUNK, SR)
  finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()

def getLatestFrame(stream):
  data = stream.read(CHUNK)
  stream.get_read_available

main()
