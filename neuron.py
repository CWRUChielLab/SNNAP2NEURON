# This file is part of SNNAP2NEURON.
#
# Copyright (C) 2019 Jayalath A M M Abeywardhana, Jeffrey Gill, Reid Bolding,
# Peter Thomas
#
# SNNAP2NEURON is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# SNNAP2NEURON is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SNNAP2NEURON.  If not, see <https://www.gnu.org/licenses/>.

import re
import os
import util
from  vdgConductance import VDConductance

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

        self.readNeuronFile()
        
    def readNeuronFile(self):
        """
        read .neu file
        """
        filename = os.path.join(self.filePath,self.fileName)
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

                elif re.search("Name of conductance", line[1]) is not None:
                    self.extractConductance(i, lineArr)

                i = i+1

    def extractConductance(self, i, lineArr):
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