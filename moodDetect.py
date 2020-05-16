import pyaudio
import asyncio
import time
import numpy as np
import scipy as sp
import math
import matplotlib.pyplot as plt

class MoodDetect(object):

    def __init__(self):
        self.paudio = pyaudio.PyAudio()
        self.stream = None
        self.samplingRate = 44100
        self.dataStream = None
        self.timeData = None
        self.frames = 2048
        self.rmsList = np.array([])
        self.noneCount = 0

        self.plot = plt.plot([])
        self.xAxis = np.array(np.linspace(0, self.samplingRate, self.frames))
        # self.plot.set_ylim(0, 0.1)

    def startStream(self):
        self.stream = self.paudio.open(format=pyaudio.paInt16, channels=1, frames_per_buffer=self.frames, rate=self.samplingRate, input=True)

    def closeStream(self):
        if self.stream:
            self.stream.close()
        else:
            print("No running stream detected.")

    def getOutputStream(self):
        dataInput = (np.frombuffer(self.stream.read(self.stream.get_read_available()), dtype=np.short)[-self.frames:])
        self.timeData = dataInput
        dataInput = dataInput / 32678.0
        hammingWindow = sp.hamming(2048)
        self.dataStream = np.array(abs(hammingWindow * sp.fft(dataInput))[:self.frames//10])
        limit = np.full(len(self.dataStream), 0.003)
        plt.plot(self.xAxis[:len(self.dataStream)], self.dataStream, 'b-', self.xAxis[:len(self.dataStream)], limit, 'r--')
        plt.pause(0.1)
        plt.clf()
        return self.dataStream

    def calcAverageVal(self, dataStream):
        if np.amax(dataStream[15:]) > 0.004:
            detectedFrequencies = {}
            sumDiv = 0
            for i in range(1, len(dataStream) - 1):
                if dataStream[i] > 0.003:
                    self.noneCount = 0
                    sumDiv += dataStream[i]
                    a, b, g = np.log(dataStream[i-1:i+2])
                    p = (0.5) * ((a - g)/(a - (2*b) + g))
                    freq = (i + p) * self.samplingRate/self.frames
                    detectedFrequencies[freq] = dataStream[i]
            sumTotal = 0
            for val in detectedFrequencies:
                sumTotal += (val * detectedFrequencies[val])
        
            return sumTotal/sumDiv
        
        else:
            self.noneCount += 1

    def averageOfAverage(self):
        avgSum = 0
        i = 0
        interval = 3
        foundAverage = False
        while (i < interval):
            average = self.calcAverageVal(self.getOutputStream())
            if average:
                avgSum += average
                if i == 2:
                    foundAverage = True
            i += 1
            time.sleep(0.1)
        if foundAverage:
            return avgSum / interval
        else:
            return None

    def calcCentDifference(self, firstVal=None, currVal=None):
        print("Last Val: {}".format(firstVal))
        print("Curr Val: {}".format(currVal))
        if firstVal and firstVal > 0 and currVal > 0:
            centDif = 12 * math.log((currVal / firstVal), 2)
            return round(centDif)

    async def rootMeanSquare(self):
        if self.timeData is not None:
            rms = np.sqrt(np.mean(np.power(self.timeData, 2)))
            if self.rmsList.shape[0] == 5:
                self.rmsList = np.delete(self.rmsList, 0)
            self.rmsList = np.append(self.rmsList, rms)
            return np.average(self.rmsList)

    async def avgRms(self):
        average = np.zeros(5)
        for i in range(5):
            average[i] = await self.rootMeanSquare()
        
        return np.average(average)

