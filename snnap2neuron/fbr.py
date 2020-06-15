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

class FBR():
    def __init__(self, filePath, fileName):
        self.filePath = filePath
        self.fileName = fileName

        self.fBRtype = ''
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
            # unicode character: \xc3
            # get value without using findNextFeature()
            BR_a = lineArr[i+1][0]

        return BRType, BR_a

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
