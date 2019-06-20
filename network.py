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


import re
import os

import util
from neuron import Neuron
from chemicalSynapse import ChemSynapse


class ElecSynapse():

    def __init__(self, postSyn, preSyn, fileName, color, filePath):
        """
        """
        self.postSyn = postSyn
        self.preSyn =  preSyn
        self.fileName = fileName
        self.filePath = filePath
        self.color = color

        self.g1 = ""
        self.g2 = ""

        self.readESFile()


    def readESFile(self):
        """
        read electrical coupling file
        """
        filename = os.path.join(self.filePath,self.fileName)
        with open(filename) as f:
            self.text = f.read()
            print "Reading electrical coupling file : ", filename
            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i <len(lineArr):
                line = lineArr[i]

                if len(lineArr[i]) > 1:
                    if not re.search("G1", lineArr[i][1]) is None:
                        self.g1 = lineArr[i][0]
                    if not re.search("G2", lineArr[i][1]) is None:
                        self.g2 = lineArr[i][0]
                i = i+1
        return



class Network():

    def __init__(self, filePath, fileName):

        self.neurons = {}
        self.chemSyns = []
        self.elecSyns = []
        self.filePath = filePath
        self.fileName = fileName
        #self.readNtwFile(self.filePath, self.fileName)
        self.readNtwFile()


    
    def readNtwFile(self):
        """
        read network file
        """
        filename = os.path.join(self.filePath,self.fileName)
        with open(filename) as f:
            self.text = f.read()

            print "Reading network file : ", filename

            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i <len(lineArr):
                line = lineArr[i]

                if len(line) < 2:
                    i = i+1
                    continue
                
                if line[0] == "LIST_NEURONS:":
                    i = self.extractNeurons(i+1, lineArr)

                elif line[0] == "CHEMSYN:":
                    i = self.extractChemSynapses(i+1, lineArr)
                elif line[0] == "ELCTRCPL:":
                    i = self.extractElecSynapses(i+1, lineArr)
                elif line[0] == "MODULSYN:":
                    i = self.extractModularySynapses(i+1, lineArr)
                else:
                    i = i+1

    def extractModularySynapses(self, i, lineArr):
        """
        TODO
        """
        print "Reading Modulatory synapses"
        while lineArr[i][0] != "END":
            i = i+1
        print "Done reading Modulatory synapses"
        return i+1


    
    def extractElecSynapses(self, i, lineArr):
        print "Reading electrical coupling"
        while lineArr[i][0] != "END":
            if re.search("postsynaptic", lineArr[i][1]) is not None:
                postSyn = lineArr[i][0]
                preSyn = self.findNextFeature(i, lineArr, feature="presynaptic")
                elecSynapseFilename = self.findNextFeature(i, lineArr, feature="File Name")
                elecSynapseColor = self.findNextFeature(i, lineArr, feature="Color")
                self.elecSyns.append(ElecSynapse(postSyn, preSyn, elecSynapseFilename, elecSynapseColor, self.filePath))
            i = i+1
        print "Found", len(self.elecSyns), "electrical synapses."
        return i+1

    
    def extractChemSynapses(self, i, lineArr):
        print "Reading chemical synapses in .ntw file"
        while lineArr[i][0] != "END":
            if re.search("postsynaptic", lineArr[i][1]) is not None:
                postSyn = lineArr[i][0]
                preSyn = self.findNextFeature(i, lineArr, feature="presynaptic")
                chemSynapseType = self.findNextFeature(i, lineArr, feature="type")
                chemSynapseFilename = self.findNextFeature(i, lineArr, feature="File Name")
                chemSynapseColor = self.findNextFeature(i, lineArr, feature="Color")
                self.chemSyns.append(ChemSynapse(postSyn, preSyn, chemSynapseType, chemSynapseFilename, chemSynapseColor, self.filePath))
            i = i+1
        print "Found", len(self.chemSyns), "chemical synapses."
        return i+1

    def findNextFeature(self, i, lineArr, feature=""):
        if feature == "":
            return None
        
        j = i+1
        if j >= len(lineArr):
            return None
        while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
            #while re.search(feature, lineArr[j][1]) is None:
            j = j+1
        return lineArr[j][0]

    
    def extractNeurons(self, i, lineArr):
        """
        read neuron name, filename, and color from .ntw file and create a Neuron object 
        for each of the read neurons and store them in dictionary 'self.neurons'
        """
        
        print "Reading neurons in .ntw file"
        while (lineArr[i][0] != "END"):
            if lineArr[i][1] == "Neuron's name":
                nName = lineArr[i][0]
                nFilename = self.findNextFeature(i, lineArr, feature="File Name")
                nColor = self.findNextFeature(i, lineArr, feature="Color")
                self.neurons[nName] = Neuron(nName, nFilename, nColor, self.filePath)

            i = i+1
        print "Found", len(self.neurons.keys()), "nerons."
        return i+1
        
    def findNextFilename(self, i, lineArr):
        j = i+1

        while(lineArr[j][1] != "File Name"):
            j = j+1
        return lineArr[j][0]

        
    def findNextColor(self, i, lineArr):
        j = i+1

        while(lineArr[j][1] != "Color Name"):
            j = j+1
        return lineArr[j][0]


        
            
