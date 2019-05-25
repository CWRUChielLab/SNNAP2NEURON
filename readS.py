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
import re
import os

from simulation import Simulation as sim
from nrnModel import NRNModel
        
def parse2Hoc(filename):

    # create simulation object. 
    snnapSim = sim(filename)

    nrnModel = NRNModel(snnapSim)
    return snnapSim

def printSim(sim):
    pass

    
if __name__ == "__main__":
    print "main"
    if len(sys.argv) > 1:
        filePath = sys.argv[1]
    else:
        print("usage: parseSNNAP <simulationFile>")
        filePath = "model/hhNetwork.smu"

    splitedFilePath = filePath.split('/')

    simFilePath = splitedFilePath[:-1]
    simFileName = splitedFilePath[len(splitedFilePath)-1]
    
    currSim = parse2Hoc(filePath)

