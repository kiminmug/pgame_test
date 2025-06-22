import numpy as np
import wave

# 0.1초짜리 880Hz 삐 소리 만들기
framerate = 44100
length = 0.1  # 초
frequency = 880  # Hz

# 시간축 만들기
samples = np.linspace(0, length, int(framerate * length), False)
# 사인파 만들기
waveform = np.sin(frequency * 2 * np.pi * samples)
# 16비트 PCM으로 변환
sound = (waveform * 32767).astype(np.int16)

# ping.wav 파일로 저장
with wave.open('ping.wav', 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(framerate)
    f.writeframes(sound.tobytes())

print('ping.wav 파일이 만들어졌어요!') 