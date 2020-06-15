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
import argparse

from .simulation import Simulation as sim
from .nrnModelPoint import NRNModelPoint
from .nrnModelDist import NRNModelDist

def parse2Hoc(filename, cond):
    # create simulation object.
    snnapSim = sim(filename)

    # write model in NEURON
    if cond == 'p':
        print("Conductances will be represented as point mechanisms")
        nrnModel = NRNModelPoint(snnapSim)
    elif cond == 'd':
        print("Conductances will be represented as distributed mechanisms")
        nrnModel = NRNModelDist(snnapSim)
    else:
        print("error: bad conductance mode: " + str(cond))
        return None
    return snnapSim

def printSim(sim):
    pass

def main():

    description = """
    An automated translation tool for converting SNNAP models into NEURON models
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", help="path to SNNAP .smu file")
    parser.add_argument("-c", "--cond", choices=['p', 'd'], default='p',
                        help="representation of conductances (point 'p', or distributed 'd')")
    args = parser.parse_args()

    filePath = args.input
    if not os.path.isfile(filePath):
        print('error: file "' + filePath + '" does not exist')
        exit(1)

    splitedFilePath = filePath.split(os.sep)

    simFilePath = os.sep.join(splitedFilePath[:-1])
    if not simFilePath:
        simFilePath = '.'
    simFileName = splitedFilePath[-1]

    # file paths given within SNNAP files are always specified relative to the
    # SMU file, so change directory now so all files can be located later
    os.chdir(simFilePath)

    currSim = parse2Hoc(simFileName, args.cond)

if __name__ == "__main__":
    main()
