import re

import util


class VDConductance():
    def __init__(self, filePath, fileName, color):

        self.filePath = filePath
        self.fileName = fileName
        self.color = color


        # will be filled from vdg file
        self.ivdType = ""
        self.g = ""
        self.E = ""
        self.P = ""
        # activation/inactivation function filenames
        self.A = ""
        self.B = ""
        self.m = ""
        self.h = ""


        # will be filled from .A file (if ivdType equal to 1 or 3)
        self.AType = ""
        self.A_IV = ""
        
        self.ssAType = ""
        self.ssA_h = ""
        self.ssA_s = ""
        self.ssA_p = ""
        self.ssA_An = ""
        
        self.tAType = ""
        self.tA_tx = ""
        self.tA_tn = ""
        self.tA_h1 = ""
        self.tA_h2 = ""
        self.tA_s1 = ""
        self.tA_s2 = ""
        self.tA_p1 = ""
        self.tA_p2 = ""

        # will be filled from .B file (if ivdType equal to 1)
        self.BType = ""
        self.B_IV = ""
        
        self.ssBType = ""
        self.ssB_h = ""
        self.ssB_s = ""
        self.ssB_p = ""
        self.ssB_Bn = ""
        
        self.tBType = ""
        self.tB_tx = ""
        self.tB_tn = ""
        self.tB_h1 = ""
        self.tB_h2 = ""
        self.tB_s1 = ""
        self.tB_s2 = ""
        self.tB_p1 = ""
        self.tB_p2 = ""

        # will be filled from .m file (if ivdType equal to 2 or 4)
        self.mType = ""
        self.m_IV = ""
        self.m_L = ""
        
        self.amType = ""
        self.am_A = ""
        self.am_B = ""
        self.am_C = ""
        self.am_D = ""

        self.bmType = ""
        self.bm_A = ""
        self.bm_B = ""
        self.bm_C = ""
        self.bm_D = ""

        # will be filled from .h file (if ivdType equal to 2)
        self.hType = ""
        self.h_IV = ""
        self.h_L = ""
        
        self.ahType = ""
        self.ah_A = ""
        self.ah_B = ""
        self.ah_C = ""
        self.ah_D = ""

        self.bhType = ""
        self.bh_A = ""
        self.bh_B = ""
        self.bh_C = ""
        self.bh_D = ""
        
        
        
        self.readVDGFile()
        if self.ivdType == "2" or self.ivdType == "4":
            self.read_mFile()
            if self.ivdType == "2":
                self.read_hFile()
        if self.ivdType == "1" or self.ivdType == "3":
            self.read_AFile()
            if self.ivdType == "1":
                self.read_BFile()
            pass
    

    def read_AFile(self):
        filename = self.filePath + "/" + self.A
        with open(filename) as f:
            self.text = f.read()

            print "Reading .A file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if re.search("^A", line[0]) is not None:
                    self.AType, self.A_IV = self.extractActivation_timeConst(i+1, lineArr)
                if re.search("^ssA", line[0]) is not None:
                    self.ssAType, self.ssA_h, self.ssA_s, self.ssA_p, self.ssA_An = self.extractSteadyState(i+1, lineArr, 1)
                if re.search("^tA", line[0]) is not None:
                    self.tAType, self.tA_tx, self.tA_tn, self.tA_h1, self.tA_h2, self.tA_s1, self.tA_s2, self.tA_p1, self.tA_p2  = self.extractTimeConstant(i+1, lineArr)

                i = i+1
        return

    def read_BFile(self):
        filename = self.filePath + "/" + self.B
        with open(filename) as f:
            self.text = f.read()

            print "Reading .B file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if re.search("^B", line[0]) is not None:
                    self.BType, self.B_IV = self.extractActivation_timeConst(i+1, lineArr)
                if re.search("^ssB", line[0]) is not None:
                    self.ssBType, self.ssB_h, self.ssB_s, self.ssB_p, self.ssB_Bn = self.extractSteadyState(i+1, lineArr, 0)
                if re.search("^tB", line[0]) is not None:
                    self.tBType, self.tB_tx, self.tB_tn, self.tB_h1, self.tB_h2, self.tB_s1, self.tB_s2, self.tB_p1, self.tB_p2  = self.extractTimeConstant(i+1, lineArr)
                i = i+1
        return

    
    def extractTimeConstant(self, i, lineArr):
        """
        read and return parameters related to time constant for activation (tA from .A files)
        or inactivation (tB from .B files)
        """
        tConstType = lineArr[i][0]
        tx = self.findNextFeature(i, lineArr, "tx")
        tn = ""
        h1 = ""
        h2 = ""
        s1 = ""
        s2 = ""
        p1 = ""
        p2 = ""
        if tConstType == '2':
            tn = self.findNextFeature(i, lineArr, "tn")
            h1 = self.findNextFeature(i, lineArr, "h")
            s1 = self.findNextFeature(i, lineArr, "s")
            p1 = self.findNextFeature(i, lineArr, "p")
        elif tConstType == '3':
            tn = self.findNextFeature(i, lineArr, "tn")
            h1 = self.findNextFeature(i, lineArr, "h1")
            s1 = self.findNextFeature(i, lineArr, "s1")
            p1 = self.findNextFeature(i, lineArr, "p1")
            h2 = self.findNextFeature(i, lineArr, "h2")
            s2 = self.findNextFeature(i, lineArr, "s2")
            p2 = self.findNextFeature(i, lineArr, "p2")
        elif tConstType != '1':
            print "WARNING: Time constant forms other than 1, 2 or 3 are not supported yet!!!"
        return tConstType, tx, tn, h1, h2, s1, s2, p1, p2

    
    def extractSteadyState(self, i, lineArr, isActivation):
        """
        read and return parameters related to steady state of acivation (ssA from .A files)
        or inactivation (ssB from .B files)
        """
        ssType = ""
        ss_h = ""
        ss_s = ""
        ss_p = ""
        ss_Xn = ""

        ssType = lineArr[i][0]
        if ssType == '2' and isActivation == 1:
            ss_Xn= self.findNextFeature(i, lineArr, "An")
        if ssType == '2' and isActivation == 0:
            ss_Xn= self.findNextFeature(i, lineArr, "Bn")
            
        ss_h = self.findNextFeature(i, lineArr, "h")
        ss_s = self.findNextFeature(i, lineArr, "s")
        ss_p = self.findNextFeature(i, lineArr, "p")
        return ssType, ss_h, ss_s, ss_p, ss_Xn

    def extractActivation_timeConst(self, i, lineArr):
        """
        read and return time constant activation (A) or inactivation (B) function form and ralated
        parameters (A_* from .A file or B_* from .B file)
        """
        funcType = ""
        iv = ""
        funcType = lineArr[i][0]
        if funcType == "2":
            iv = self.findNextFeature(i, lineArr, "IV")
            
        return funcType, iv


    def read_mFile(self):
        filename = self.filePath + "/" + self.m
        with open(filename) as f:
            self.text = f.read()

            print "Reading .m file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if re.search("^m", line[0]) is not None:
                    self.mType, self.m_IV, self.m_L = self.extractActivation_rateConst(i+1, lineArr)
                if re.search("^am", line[0]) is not None:
                    self.amType, self.am_A, self.am_B, self.am_C, self.am_D = self.extractRateParameter(i+1, lineArr)
                if re.search("^bm", line[0]) is not None:
                    self.bmType, self.bm_A, self.bm_B, self.bm_C, self.bm_D = self.extractRateParameter(i+1, lineArr)

                i = i+1
        return
    
            
    def read_hFile(self):
        filename = self.filePath + "/" + self.h
        with open(filename) as f:
            self.text = f.read()

            print "Reading .h file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if re.search("^h", line[0]) is not None:
                    self.hType, self.h_IV, self.h_L = self.extractActivation_rateConst(i+1, lineArr)
                if re.search("^ah", line[0]) is not None:
                    self.ahType, self.ah_A, self.ah_B, self.ah_C, self.ah_D = self.extractRateParameter(i+1, lineArr)
                if re.search("^bh", line[0]) is not None:
                    self.bhType, self.bh_A, self.bh_B, self.bh_C, self.bh_D = self.extractRateParameter(i+1, lineArr)

                i = i+1
        return

    
    def extractActivation_rateConst(self, i, lineArr):
        """
        extract rate constant activation (m) or inactivation (h) parameters
        """
        funcType = ""
        iv = ""
        l = ""
        funcType = lineArr[i][0]
        if funcType == "2" or funcType == "3":
            iv = self.findNextFeature(i, lineArr, "IV")
        if funcType == "3":
            l = self.findNextFeature(i, lineArr, "L")
            
        return funcType, iv, l


    def extractRateParameter(self, i, lineArr):
        """
        read and store rate parameter. can be used to get
        am, and bm from .m files and ah, and bh from .h files
        """
        parmType = lineArr[i][0]
        rp_A = self.findNextFeature(i, lineArr, "A")
        rp_B = ""
        rp_C = ""
        rp_D = ""
        if parmType != '1':
            rp_B = self.findNextFeature(i, lineArr, "B")
            if parmType != '4' and parmType != '8' and parmType != '9':
                rp_C = self.findNextFeature(i, lineArr, "C")
                if parmType != '5' and parmType != '6' and parmType != '7':
                    rp_D = self.findNextFeature(i, lineArr, "D")
        return (parmType, rp_A, rp_B, rp_C,rp_D)

    
    def readVDGFile(self):
        filename = self.filePath + "/" + self.fileName
        with open(filename) as f:
            self.text = f.read()

            print "Reading .vdg file : ", filename
            lineArr = util.cleanupFileText(self.text)

            i = 0
            while i< len(lineArr):
                line = lineArr[i]
                if re.search("^Ivd", line[0]) is not None:
                    self.extractIvd(i+1, lineArr)
                i = i+1
        return

    def extractIvd(self, i, lineArr):
        """
        """
        self.ivdType = lineArr[i][0]
        if self.ivdType == "1" or self.ivdType == "3":
            self.A = self.findNextFeature(i, lineArr, "A")
            self.P = self.findNextFeature(i, lineArr, "P")

        if self.ivdType == "2" or self.ivdType == "4":
            self.m = self.findNextFeature(i, lineArr, "m")
            self.P = self.findNextFeature(i, lineArr, "P")

        if self.ivdType == "1":
            self.B = self.findNextFeature(i, lineArr, "B")
        if self.ivdType == "2":
            self.h = self.findNextFeature(i, lineArr, "h")

        self.g = self.findNextFeature(i, lineArr, "g")
        self.E = self.findNextFeature(i, lineArr, "E")


    def findNextFeature(self, i, lineArr, feature=""):
        if feature == "":
            return None
        
        j = i+1
        if j >= len(lineArr):
            return None
        while len(lineArr[j]) > 1 and re.search(feature, lineArr[j][1]) is None:
            j = j+1
        return lineArr[j][0]

        
