import sys
import re
import os

import util

class CurrentInj():

    def __init__(self, nName, start, stop, magnitude):
        """
        SNNAP .trt files contain time and magnitude in units of seconds
        and nA respectively
        """
        
        self.neuronName = nName
        self.start = start
        self.stop = stop
        self.magnitude = magnitude

class Treatment():


    def __init__(self, filePath, fileName):

        self.fileName = fileName
        self.filePath = filePath

        self.currentInjList = []

        self.readTrtFile()

    def readTrtFile(self):
        filename = self.filePath + "/" +  self.fileName
        with open(filename) as f:
            self.text = f.read()

            print "Reading treatment file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("CURNT_INJ", line[0]) is not None:
                    self.extractCurntInj(i, lineArr)

                i = i+1



    def extractCurntInj(self, i, lineArr):
        
        print "Reading current injections in .trt file"
        while lineArr[i][0] != "END":

            if re.search("Name of Neuron", lineArr[i][1]) is not None:
                nrn = lineArr[i][0]
                start = self.findNextFeature(i, lineArr, feature="Start")
                stop = self.findNextFeature(i, lineArr, feature="Stop")
                magnitude = self.findNextFeature(i, lineArr, feature="Magnitude")
                if float(magnitude) != 0.0:
                    self.currentInjList.append(CurrentInj(nrn, start, stop, magnitude))
            i = i+1
        print "Found", len(self.currentInjList), "current injections."
        return i+1


    def findNextFeature(self, i, lineArr, feature=""):
        if feature == "":
            return None
        
        j = i+1
        if j >= len(lineArr):
            return None
        while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
            j = j+1
        return lineArr[j][0]
