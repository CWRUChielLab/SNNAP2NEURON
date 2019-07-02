import sys
import re
import os

from simulation import Simulation as sim
from nrnModelPoint import NRNModelPoint
from nrnModelDist import NRNModelDist

def parse2Hoc(filename):

    # create simulation object. 
    snnapSim = sim(filename)

    # write model in NEURON
    #nrnModel = NRNModelPoint(snnapSim)
    nrnModel = NRNModelDist(snnapSim)
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

