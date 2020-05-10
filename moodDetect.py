import pyaudio
import asyncio
import numpy as np
import scipy as sp

class MoodDetect(object):

    def __init__(self):
        self.paudio = pyaudio.PyAudio()
        self.stream = None
        self.samplingRate = 44100
        self.dataStream = None
        self.frames = 2048

    def startStream(self):
        self.stream = self.paudio.open(format=pyaudio.paInt16, channels=1, frames_per_buffer=self.frames, rate=self.samplingRate, input=True)

    def closeStream(self):
        if self.stream:
            self.stream.close()
        else:
            print("No running stream detected.")

    def getOutputStream(self):
        dataInput = (np.frombuffer(self.stream.read(self.stream.get_read_available()), dtype=np.short)[-self.frames:])
        dataInput = dataInput / 32678.0
        hanningWindow = sp.hanning(2048)
        self.dataStream = np.array(abs(hanningWindow * sp.fft(dataInput))[:self.frames//2])
        return self.dataStream[15:]

    def calcAverageVal(self, dataStream):
        if np.amax(dataStream) > 0.01:
            detectedFrequencies = {}
            sumDiv = 0
            for i in range(1, len(dataStream) - 1):
                if dataStream[i] > 0.01:
                    sumDiv += dataStream[i]
                    a, b, g = np.log(dataStream[i-1:i+2])
                    p = (0.5) * ((a - g)/(a - (2*b) + g))
                    freq = (i + p) * self.samplingRate/self.frames
                    detectedFrequencies[freq] = dataStream[i]

            print(detectedFrequencies)
            sumTotal = 0
            for val in detectedFrequencies:
                sumTotal += (val * detectedFrequencies[val])
        
            return sumTotal/sumDiv
        
        else:
            pass

    def calcCentDifference(self, lastVal, currVal):
        pass
