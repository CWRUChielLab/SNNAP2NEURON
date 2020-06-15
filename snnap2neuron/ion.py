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

import sys
import os
import re
import util

class IonPool():
    """
    Ion pool
    """
    def __init__(self, filePath, fileName, color):
        self.filePath = filePath
        self.fileName =fileName
        self.color = color

        self.cionType = ''
        self.k1 = ''
        self.k2 = ''

        self.readIonFile()

    def readIonFile(self):
        """
        read .ion file
        """
        filename = os.path.join(self.filePath,self.fileName)
        with open(filename.lstrip('/')) as f:
            self.text = f.read()

            print("Reading ion file : ", filename)
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]

                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("Cion", line[0]) is not None:
                    self.cionType, self.k1, self.k2 = self.extractIon(i+1, lineArr)

                i=i+1
            pass

    def extractIon(self, i, lineArr):
        """
        read and return parameters related to ion pool concentration dynamics
        """
        iType = ""
        i_k1 = ""
        i_k2 = ""

        iType = lineArr[i][0]
        if iType == '1':
            print("WARNING!! Ion pool concentration type 1 is not supported yet")
            print("Exiting...")
            sys.exit(1)

        elif iType == '2':
            i_k1 = util.findNextFeature(i, lineArr, "K1")
            i_k2 = util.findNextFeature(i, lineArr, "K2")
        return iType, i_k1, i_k2

class Current2Ion():
    """
    A currunt that is contributing to ion
    """
    def __init__(self, cond, ion, color):
        self.cond = cond
        self.ion = ion
        self.color = color

class ConductanceByIon():
    def __init__(self, cond, ion, filePath, fileName, color):
        self.cond = cond
        self.ion = ion
        self.filePath = filePath
        self.fileName = fileName
        self.color = color

        self.fBRType = ''
        self.BRType = ''
        self.BR_a = ''


        self.readModByRegulatorFile()

    def readModByRegulatorFile(self):
        """
        read fBR  file
        """
        filename = os.path.join(self.filePath,self.fileName)
        print("FBR FIle", filename)
        with open(filename.lstrip('/')) as f:
            self.text = f.read()

            print("Reading fBR file : ", filename)
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("^fBR", line[0]) is not None:
                    self.fBRType  = self.extractfBR(i+1, lineArr)
                if re.search("^BR", line[0]) is not None:
                    self.BRType, self.BR_a  = self.extractBR(i+1, lineArr)

                i=i+1
            pass

    def extractBR(self, i, lineArr):
        """
        read and return parameters related to regulaion of conductances by ion
        """
        BRType = ""
        BR_a = ""

        BRType = lineArr[i][0]
        if BRType == '1':
            print("WARNING!! Ion pool concentration type 1 is not supported yet")
            print("Exiting...")
            sys.exit(1)

        elif BRType == '2' or BRType == '3':
            BR_a = util.findNextFeature(i, lineArr, "a")
        elif BRType == '4':
            # \xc3
            BR_a = lineArr[i+1][0]

        return BRType, BR_a

    # def extractBR(self, i, lineArr):
    #     """
    #     read and return parameters related to regulaion of conductances by ion
    #     """
    #     BRType = ""
    #     BR_a = ""

    #     BRType = lineArr[i][0]
    #     if BRType in ['1', '4']:
    #         print("WARNING!! Ion pool concentration type 1 or 4 not supported yet")
    #         print("Exiting...")
    #         sys.exit(1)

    #     else:
    #         BR_a = util.findNextFeature(i, lineArr, "a")
    #     return BRType, BR_a


    def extractfBR(self, i, lineArr):
        """
        read and return parameters related to regulaion of conductances by ion
        """
        fBRType = lineArr[i][0]
        if fBRType == '3':
            print("WARNING!! Modulation by regulator type 3 is not supported yet")
            print("Exiting...")
            sys.exit(1)

        return fBRType
