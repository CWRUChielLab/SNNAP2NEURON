
import re

import util
from  vdgConductance import VDConductance
from ion import IonPool, Current2Ion, ConductanceByIon

class Neuron():

    def __init__(self, name, fileName, color, filePath):

        self.name = name
        self.filePath = filePath
        self.fileName = fileName
        self.color = color

        self.treshold = ''
        self.spikeDur = ''
        self.vmInit = ''
        self.cm = ''
        self.memAreaType = ''

        # voltage gated conductances
        self.vdgs = {}
        # ion pools
        self.ionPools = {}
        # list of currents contributing to ion pools
        self.curr2Ions = []
        # regulation of vdg by ion pools
        self.condByIon = []

        
        self.readNeuronFile()
        
        
    def readNeuronFile(self):
        """
        read .neu file
        """
        filename = self.filePath + "/" +  self.fileName
        with open(filename) as f:
            self.text = f.read()

            print "Reading neuron file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("THRESHOLD", line[0]) is not None:
                    self.treshold = self.extractNeuronsFeature(i+1, line[0])

                elif re.search("SPIKDUR", line[0]) is not None:
                    self.spikeDur = self.extractNeuronsFeature(i+1, line[0])

                elif re.search("VMINIT", line[0]) is not None:
                    self.vmInit = self.extractNeuronsFeature(i+1, line[0])

                elif re.search("CM", line[0]) is not None:
                    self.cm = self.extractNeuronsFeature(i+1, line[0])
                    
                elif re.search("^MEM_AREA", line[0]) is not None:
                    self.memAreaType = lineArr[i+1][0]
                    
                elif line[0] == "CONDUCTANCES:":
                    i = self.extractConductance(i+1, lineArr)
                elif line[0] == "LIST_ION:":
                    i = self.extractIonPools(i+1, lineArr)
                elif line[0] == "CURRENT_TO_ION:":
                    i = self.extractCurr2Ions(i+1, lineArr)
                elif line[0] == "COND_BY_ION:":
                    i = self.extractConductanceByIon(i+1, lineArr)
                    
                i = i+1

    def extractConductanceByIon(self, i, lineArr):
        """
        read and store regulation of voltage dependent conductances by ion pools
        """

        print "Reading regulation of voltage dependent conductances by ion pools"
        while lineArr[i][0] != "END":
            print lineArr[i]
            if re.search("Name of Conductance", lineArr[i][1]) is not None:
                condName = lineArr[i][0].replace('(', '_').replace(')', '_')
                ionName = lineArr[i+1][0]
                fileName = lineArr[i+2][0]
                color = lineArr[i+3][0]

                self.condByIon.append(ConductanceByIon(condName, ionName, self.filePath, fileName, color))
            i = i+1
        return i


    def extractCurr2Ions(self, i, lineArr):
        """
        read list of currents that contribute to ion pools
        """
        print "Reading list of currents that contribute to ion pools"
        while lineArr[i][0] != "END":
            if re.search("Name of Conductance", lineArr[i][1]) is not None:
                condName = lineArr[i][0].replace('(', '_').replace(')', '_')
                ionName = lineArr[i+1][0]
                color = lineArr[i+2][0]

                self.curr2Ions.append(Current2Ion(condName, ionName, color))
                
            i = i+1
        return i

    
    def extractIonPools(self, i, lineArr):
        """
        read and store ion pools from
        .neu files
        """

        print "Reading ion pools"
        while lineArr[i][0] != "END":
            if re.search("Name of Ion", lineArr[i][1]) is not None:
                ionName = lineArr[i][0]
                ionFileName = lineArr[i+1][0]
                ionColor = lineArr[i+2][0]

                self.ionPools[ionName] = IonPool(self.filePath, ionFileName, ionColor)
                
            i = i+1
        return i

    def extractConductance(self, i, lineArr):
        """
        read and store leak, Na, K, conductance filenames(*.vdg) and color from
        .neu files
        """

        print "Reading conductances"
        while lineArr[i][0] != "END":
            if re.search("Name of conductance", lineArr[i][1]) is not None:
                # vdg names sometimes had paranthesis!
                vdgName = lineArr[i][0].replace('(', '_').replace(')', '_')
                vdgFileName = lineArr[i+1][0]
                vdgColor = lineArr[i+2][0]
                #vdgFileName = self.findNextFeature(i, lineArr, feature="File Name")
                #vdgColor = self.findNextFeature(i, lineArr, feature="Color")
                self.vdgs[vdgName] = VDConductance(self.filePath, vdgFileName, vdgColor)
                
            i = i+1
        return i

    def extractConductance_OLD(self, i, lineArr):
        """
        read and store leak, Na, K, conductance filenames(*.vdg) and color from
        .neu files
        """
        vdgName = lineArr[i][0]
        vdgFileName = self.findNextFeature(i, lineArr, feature="File Name")
        vdgColor = self.findNextFeature(i, lineArr, feature="Color")
        self.vdgs[vdgName] = VDConductance(self.filePath, vdgFileName, vdgColor)


    def findNextFeature(self, i, lineArr, feature=""):
        if feature == "":
            return None        
        j = i+1
        if j >= len(lineArr):
            return None
        while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
            j = j+1
        return lineArr[j][0]


    def extractNeuronsFeature(self, i, str):
        return str.split(':')[1].strip()

