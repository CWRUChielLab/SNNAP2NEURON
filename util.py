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

def formatedObjectVar(obj, var):
    """
    returns a left justified sting (obj.var) with a length of 20 characters
    Inputs:
    obj - object name
    var - variable name

    Returns:
    a left justified sting with a length of 20 characters
    """
    return (obj+"."+var).ljust(20)

def cleanupFileText(text):
    """
    returns an arry for after striping whitespaces and comments of SNNAP files

    Inputs:
    text - content of a SNNAP file in one single string

    Returns:
    lineArr - an array of lines without comments and empty lines

    """
    fileLines = text.split('\n')
    lineArr = []

    for i in range(len(fileLines)):
        l = fileLines[i].strip()
        if len(l) == 0 or l[0] == '>':
            continue
        else:
            lineArr.append([elem.strip() for elem in l.split('>')])
    return lineArr

def findNextFeature(i, lineArr, feature=""):
    """
    return value assigned to SNNAP keyword(called feature)
    """
    if feature == "":
        return None

    j = i+1
    if j >= len(lineArr):
        return None
    while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
        j = j+1
    return lineArr[j][0]


def writePlottingFile(nrnDirPath, nrnDirName, sSim):
    """
    write .hoc file for making plots
    """
    pf_local = "create_plot.hoc"
    if not os.path.isdir(nrnDirPath + os.sep + nrnDirName):
        print("Failed to write "+ pf_local+" file")
        return

    plotFileName = os.path.join(nrnDirPath,nrnDirName,pf_local)

    plot_BP = """//create plots\nobjref plots\nplots = new Graph(0)\naddplot(plots, 0)\n\n
// view: xmin, ymin, xrange, yrange, winleft, wintop, winwidth, winheight\n
plots.view(0, -110, tstop, 210, 0, 290, 640, 320)\n
//addvar: \"label\", \"variable\", color_index, brush_index\n"""

    with open(plotFileName, "w") as pf:
        pf.write(plot_BP)

        nNeurons = len(sSim.network.neurons.keys())
        if nNeurons > 3:
            nNeurons = 3

        i = 0
        for nName in sSim.network.neurons.keys():
            if i >= nNeurons:
                break
            nrn = sSim.network.neurons[nName]
            pf.write("plots.addvar(\"" +nName+ " Vm\", \""+nName+".v(0.5)\", "+str(i+2)+", 1)\n")
            i = i+1
