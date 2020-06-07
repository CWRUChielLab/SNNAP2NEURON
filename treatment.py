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
import re
import os
import util

class CurrentInj():
    def __init__(self, nName, start, stop, magnitude):
        """
        Current injection
        SNNAP .trt files contain time and magnitude in units of seconds
        and nA respectively
        """
        self.neuronName = nName
        self.start = start
        self.stop = stop
        self.magnitude = magnitude

class ModInj():
    def __init__(self, nName, mod, sm, start, stop, magnitude):
        """
        Modulator injection: changes the availability of second messenger
        concentration [MOD]
        """
        self.neuronName = nName
        self.mod = mod
        self.sm = sm
        self.start = start
        self.stop = stop
        self.magnitude = magnitude

class Treatment():
    def __init__(self, filePath, fileName):
        self.fileName = fileName
        self.filePath = filePath

        self.currentInjList = []
        self.modInjList = []

        self.readTrtFile()

    def readTrtFile(self):
        filename = os.path.join(self.filePath,self.fileName)
        with open(filename.lstrip('/')) as f:
            self.text = f.read()

            print("Reading treatment file : ", filename)
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if len(line) < 2:
                    i = i+1
                    continue
                if re.search("CURNT_INJ", line[0]) is not None:
                    self.extractCurntInj(i, lineArr)
                if re.search("MOD_INJ", line[0]) is not None:
                    self.extractModInj(i, lineArr)

                i = i+1

    def extractCurntInj(self, i, lineArr):
        print("Reading current injections in .trt file")

        while lineArr[i][0] != "END":
            if re.search("Name of Neuron", lineArr[i][1]) is not None:
                nrn = lineArr[i][0]
                start = util.findNextFeature(i, lineArr, feature="Start")
                stop = util.findNextFeature(i, lineArr, feature="Stop")
                magnitude = util.findNextFeature(i, lineArr, feature="Magnitude")
                if float(magnitude) != 0.0:
                    self.currentInjList.append(CurrentInj(nrn, start, stop, magnitude))
            i = i+1
        print("Found", len(self.currentInjList), "current injections.")
        return i+1

    def extractModInj(self, i, lineArr):
        print("Reading modulator injections in .trt file")

        while lineArr[i][0] != "END":
            if re.search("Name of Neuron", lineArr[i][1]) is not None:
                nrn = lineArr[i][0]
                mod = util.findNextFeature(i, lineArr, feature="Name of Modulator")
                sm = util.findNextFeature(i, lineArr, feature="Name of sm")
                start = util.findNextFeature(i, lineArr, feature="Start")
                stop = util.findNextFeature(i, lineArr, feature="Stop")
                magnitude = util.findNextFeature(i, lineArr, feature="Magnitude")

                # magnitude can be a .fnc file
                if re.search("fnc", magnitude) is not None:
                    print("WARNING: Modulator treatments by .fnc files are not supported yet!")
                    sys.exit()
                if float(magnitude) != 0.0:
                    self.modInjList.append(ModInj(nrn, mod, sm, start, stop, magnitude))
            i = i+1
        print("Found", len(self.currentInjList), "modulator injections.")
        return i+1
