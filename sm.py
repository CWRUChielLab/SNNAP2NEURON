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

import sys
import os
import re
import util
from fbr import FBR

class SMPool():
    """
    Second messenger pool
    """
    def __init__(self, filePath, fileName, color):
        self.filePath = filePath
        self.fileName =fileName
        self.color = color

        self.smType = ''
        self.iv = ''
        self.tau = ''

        self.readSMFile()

    def readSMFile(self):
        """
        read .sm file
        """
        filename = os.path.join(self.filePath,self.fileName)
        with open(filename) as f:
            self.text = f.read()

            print "Reading second messenger file : ", filename
            lineArr = util.cleanupFileText(self.text)
            
            i = 0
            while i< len(lineArr):
                line = lineArr[i]

                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("Csm", line[0]) is not None:
                    self.smType, self.iv, self.tau = self.extractSM(i+1, lineArr)

                i=i+1
            pass

    def extractSM(self, i, lineArr):
        """
        read and return parameters related to sm concentration dynamics
        """
        smType = ""
        sm_k1 = ""
        sm_k2 = ""

        smType = lineArr[i][0]
        if smType == '1':
            sm_iv = util.findNextFeature(i, lineArr, "IV")
            sm_tau = util.findNextFeature(i, lineArr, "u")
        return smType, sm_k1, sm_k2

class ConductanceBySM():
    def __init__(self, cond, sm, filePath, fileName, color):
        self.cond = cond
        self.sm = sm
        #self.filePath = filePath
        #self.fileName = fileName
        self.color = color

        self.fbr = FBR(filePth, fileName)
        # self.fBRType = ''
        # self.BRType = ''
        # self.BR_a = ''
        
