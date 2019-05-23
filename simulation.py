
import re

import util
from network import Network as ntw
from treatment import Treatment as trt

class Simulation ():

    def __init__(self, filePath):
        
        """
        self.LOGICAL_NAME
        self.TIMING
        self.ON_LINE_GRAPH
        self.STORE_RESULTS
        self.INT_METHOD
        self.NETWORK
        self.OUTPUT_SETUP
        self.TREATMENTS

        """

        self.parameters = {"LOGICAL_NAME": "",
                "TIMING": {"t0": 0.0, "tStop": 1.0, "h":0.00004},
                "ON_LINE_GRAPH": 1,
                "STORE_RESULTS":0,
                "INT_METHOD": 1,
                "NETWORK": "",
                "OUTPUT_SETUP": "",
                "TREATMENTS": "",
                "INT_&_FIRE": 0.0}


        
        splitedFilePath = filePath.split('/')

        self.simFilePath = "/".join(splitedFilePath[:-1])
        self.simFileName = splitedFilePath[len(splitedFilePath)-1]
    
        # read simulation(.smu) file
        self.readSimFile(self.simFilePath, self.simFileName)

        # read network(.ntw) file
        self.network = ntw(self.simFilePath, self.parameters['NETWORK'])

        print "Done reading .ntw file"

        if self.parameters['TREATMENTS'] != "":
            self.treatemts = trt(self.simFilePath, self.parameters['TREATMENTS'])
        



    
    def readSimFile(self, filePath, fileName):
        """
        read simulation file
        """
        fileName = filePath + "/" +fileName
        with open(fileName) as f:
            self.text = f.read()

            print "Reading simulaiton file : ", fileName
            # extract useful lines from the the text
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i < len(lineArr):
                l = lineArr[i]

                # get 1st word fo the line
                word1 = l[0][:-1]
                if word1 in self.parameters.keys():
                    i = self.extractParam(i, lineArr, word1)
                else:
                    i = i+1

    def extractParam(self, i, lineArr, word1):
        """
        extract simulation paramters values from lineArr.
        and return line number of the next parameter
        SNNAP states time in seconds in .smu file
        """
        
        if word1 == "TIMING":
            self.parameters['TIMING']['t0']    = lineArr[i+1][0]
            self.parameters['TIMING']['tStop'] = lineArr[i+2][0]
            self.parameters['TIMING']['h']     = lineArr[i+3][0]
            return i+3
        else:
            self.parameters[word1] = lineArr[i+1][0]
            return i+1



