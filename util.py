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