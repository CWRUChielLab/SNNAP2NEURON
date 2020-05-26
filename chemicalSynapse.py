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

from __future__ import print_function

import re
import os
import util

class ChemSynapse():
    def __init__(self, postSyn, preSyn, synType, fileName, color, filePath):
        self.filePath = filePath
        self.fileName = fileName

        # parameters from .ntw file
        self.postSyn = postSyn
        self.preSyn =  preSyn
        self.synType = synType
        self.color = color

        # parameters from .cs file
        self.iCSType = ""
        self.fAtFileName = ""
        self.R = ""
        self.g = ""
        self.E = ""

        # parameters from .fAT file
        self.fATType = ""
        self.fAT_a = ""
        self.fAT_b = ""
        self.At_u1 = ""
        self.At_u2 = ""

        self.ATType = ""
        self.XtType = ""
        self.XtFileName = ""
        self.PSM_ud = ""
        self.PSM_ur = ""

        self.readCSFile()
        if self.iCSType == '1':
            self.readfATFile()
            if self.ATType == '3':
                self.readXtFile()
                pass


    def readXtFile(self):
        """
        read .Xt file
        """
        fileName = os.path.join(self.filePath,self.XtFileName)
        with open(fileName) as f:
            self.text = f.read()

            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i=0
            while i < len(lineArr):
                line =  lineArr[i]
                if re.search("^Xt", line[0]) is not None:
                    self.XtType = lineArr[i+1][0]
                    if self.XtType == "3":
                        self.extractPSM(i+1, lineArr)
                i = i+1


    def extractPSM(self, i, lineArr):
        """
        since PSM has only one option
        """
        self.PSM_ud = self.findNextFeature(i+1, lineArr, feature="ud")
        self.PSM_ur = self.findNextFeature(i+1, lineArr, feature="ur")


    def readfATFile(self):
        """
        read SNNAP time dependent activation function of chemical synapse
        """
        fileName = os.path.join(self.filePath,self.fAtFileName)
        with open(fileName) as f:
            self.text = f.read()

            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i=0
            while i < len(lineArr):
                line =  lineArr[i]

                if re.search("^fAt", line[0]) is not None:
                    self.fATType = lineArr[i+1][0]
                    if self.fATType in ['3', '5', '6']:
                        self.fAT_a = self.findNextFeature(i+1, lineArr, feature="a")
                        #self.fAT_b = self.findNextFeature(i+1, lineArr, feature="b")
                    if self.fATType in ['3', '4', '5']:
                        self.fAT_b = self.findNextFeature(i+1, lineArr, feature="b")
                if re.search("^At", line[0]) is not None:
                    self.extractAt(i, lineArr)

                i = i+1

    def extractAt(self, i, lineArr):
        self.ATType = lineArr[i+1][0]
        if self.ATType == '1':
            self.At_u1 = lineArr[i+2][0]

        if self.ATType == '3':
            self.XtFileName = lineArr[i+2][0]
            self.At_u1 = lineArr[i+3][0]

    def readCSFile(self):
        """
        read SNNAP chemical synapse (.cs) file
        """
        fileName = os.path.join(self.filePath,self.fileName)
        with open(fileName) as f:
            self.text = f.read()
            print("Reading chemical synapse file : ", fileName)

            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i=0
            while i < len(lineArr):
                line =  lineArr[i]
                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("Ics", line[0]) is not None:
                    self.extractCS(i+1, lineArr)

                i = i+1

    def extractCS(self, i, lineArr):
        self.iCSType = lineArr[i][0]
        if self.iCSType == '1':
            self.fAtFileName = self.findNextFeature(i, lineArr, feature="fAt")
            self.R = self.findNextFeature(i, lineArr, feature="R")
            self.g = self.findNextFeature(i, lineArr, feature="g")
            self.E = self.findNextFeature(i, lineArr, feature="E")
        else :
            print("WARNING: Only chemical synapses of type 1(Ics: 1) are supported!!!")

    def findNextFeature(self, i, lineArr, feature=""):
        if feature == "":
            return None

        j = i+1
        if j >= len(lineArr):
            return None
        while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
            j = j+1
        return lineArr[j][0]
