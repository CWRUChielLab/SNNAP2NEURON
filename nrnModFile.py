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

class AssignedBlock():

    def __init__(self):
        self.fromNEURON = ['V (mV)', 'celsius (degC)']
        self.rateParameters = []
        self.currents = []
        self.conductances = []
        self.reversePots = []
    pass

class NEURONBlock():

    def __init__(self, nName):
        self.mechName = nName+ "_mechs"
        self.useIons = []
        self.nsCurrents = []
        self.specificCurrents = []
        self.rangeVariables = []
        self.globalVariables = []
        
        pass

    pass

class ModVariables():

    def __init__(self):
        self.varName = ''
        # variable is ranged or not
        self.isRanged = 1
        # variable is parameter or assigned
        self.isParameter = 1
        self.unit = ''
    pass

class NRNModFile():
    
    def __init__(self, nName, modFilePath, nObject):

        self.nrnName = nName
        self.modFilePath = modFilePath
        self.nrnObject = nObject

        self.lJust1 = 16
        self.unitsBlock = []
        self.parameterBlock = {}
    
        self.stateBlock = []
        self.breakpointBlock = {}
        self.initialBlock = []

        self.derivativeBlock = []
        self.headComments = []
        self.procRates = {}

        # assigned block object
        self.assignedBlock =  AssignedBlock()
        # NEURON block object
        self.neuronBlock =  NEURONBlock(self.nrnName)
        
        self.fillUnitsBlock()
        self.readVDGs()

        # write mod file
        self.writeModFile()


    
    def readVDGs(self):
        vdgs = self.nrnObject.vdgs

        lj = self.lJust1
        # insert VDGs
        for vdgName in vdgs.keys():

            nblck = self.neuronBlock
            prmblck = self.parameterBlock
            brkpblck = self.breakpointBlock
            assgndblck = self.assignedBlock
            
            vName = vdgName.lower()

            vgdPrefix = vdgName+"_"
            currntName = "i"+vName
            revPotName = vgdPrefix+"e"
            gbarName = vgdPrefix+"gbar"
            gName = vgdPrefix+"g"
            
            # create USEION statements
            if vName in ['na', 'k','ca']:
                print "vdgName: ", vdgName
                ui = "USEION " +vName+ " READ e" +vName+ " WRITE " +currntName
                nblck.useIons.append(ui)
                
            ivdType = vdgs[vdgName].ivdType
            aType = vdgs[vdgName].AType
            bType = vdgs[vdgName].BType
            mType = vdgs[vdgName].mType
            hType = vdgs[vdgName].hType
            
            if self.nrnObject.memAreaType == '0'or self.nrnObject.memAreaType == "":
                # in SNNAP, if not using memArea conductance is given in uS
                try:
                    g = float(vdgs[vdgName].g) * 1.0e-6
                except:
                    print "WARNING!: could not convert "+vdgName+ " conductance of neuron " + self.nrnName
                    print "Exited unexpectedly!"
                    sys.exit(-1)
                    
            if vName == "leak" and ivdType == '5':
                currntName = "il"
                revPotName = "el"
                gName = "gl"
                
                nblck.nsCurrents.append('NONSPECIFIC_CURRENT ' + currntName)
                # add leak current parameters to RANGE varible list
                nblck.rangeVariables.append(gName)
                nblck.rangeVariables.append(revPotName)

                # add leak current parameters to PARAMETER block
                prmblck[vdgName] = [gName+ " = "+(str(g)).ljust(lj) + "(S/cm2)"]
                prmblck[vdgName].append(revPotName+ " = "+(vdgs[vdgName].E).ljust(lj) + "(mV)")
        
                # add leak current parameters to ASSIGNED varible list
                #assgndblck.conductances.append(gName.ljust(lj) + "(S/cm2)")
                assgndblck.currents.append(currntName.ljust(lj) +"(mA/cm2)")
                
                # add leak current parameters to BREAKPOINT block
                brkpblck[vdgName] = [currntName+ ' = '+gName +'*(v - '+revPotName+')']
                
            if ivdType == '1' or ivdType == '3':
                self.headComments.append(":_A"+aType+"_B"+bType+"\t"+vdgName+"\n")
                
                
                #nf.write(nName+" "+vdgObjName+ " = new snnap_ionic_tc_ivd"+ivdType+"_A"+aType+"(0.5)\n")

                # add leak current parameters to PARAMETER block
                prmblck[vdgName] = [gbarName+ " = "+(str(g)).ljust(lj) + "(S/cm2)"]
                prmblck[vdgName].append(revPotName+ " = "+(vdgs[vdgName].E).ljust(lj) + "(mV)")
                
                # add parameters to RANGE varible list
                nblck.rangeVariables.append(gName)
                nblck.rangeVariables.append(revPotName)

                # add parameters to ASSIGNED varible list
                assgndblck.currents.append(currntName.ljust(lj) +"(mA/cm2)")
                assgndblck.conductances.append(gName.ljust(lj) +"(S/cm2)")
                assgndblck.reversePots.append(("e" +vName).ljust(lj) +"(mV)")

                # add leak current parameters to BREAKPOINT block
                ivd_A = vgdPrefix +"A"
                ivd_p = vgdPrefix +"p"
                prmblck[vdgName].append(ivd_p+ " = "+(vdgs[vdgName].P).ljust(lj))
                if ivdType == '1':
                    ivd_B = vgdPrefix +"B"
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * '+ivd_A+'^'+ivd_p+' * '+ivd_B]
                    self.fill_ivd_A(vdgName, vgdPrefix, vdgs[vdgName])
                    self.fill_ivd_B(vdgName, vgdPrefix, vdgs[vdgName])
                    
                if ivdType == '3':
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * '+ivd_A+'^'+ivd_p+')']
                    self.fill_ivd_A(vdgName, vgdPrefix, vdgs[vdgName])

                brkpblck[vdgName].append(currntName+ ' = '+gName +'*(v - '+revPotName+')')
        pass


    def fill_ivd_A(self, vdgName, vgdPrefix, ivd):
        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        #self.globalVariables
        
        lj = self.lJust1
        
        af_Type = ivd.AType
        
        af = vgdPrefix+'A'
        afPrefix = af+'_'
        
        af_SSA = afPrefix +'SSA'
        af_tau = afPrefix +'tau'
        af_SSA_prefix = af_SSA+'_'
        af_tau_prefix = af_tau +'_'
        
        if af_Type == "2":
            # add rate paramters to GLOBAL variable list
            nblck.globalVariables.append(af_SSA)
            nblck.globalVariables.append(af_tau)
            #add rate paramters to ASSIGNED block
            assgndblck.rateParameters.append(af_SSA)
            assgndblck.rateParameters.append(af_tau.ljust(lj) +"(ms)")
            
            # add activation fucntion to state varables block
            stateblck.append(af)
            # add intialitation of activation fucntion
            initblck.append(af +" = " + af_SSA)

            # add activation fucntion to derivative block
            dvblck.append(af+"\' = ("+af_SSA+ " - " +af+") / " +af_tau)

            # write steady state
            ssA_Type = ivd.ssAType
            af_SSA_h = af_SSA_prefix+ 'h'
            af_SSA_s = af_SSA_prefix+ 's'
            af_SSA_p = af_SSA_prefix+ 'p'
            
            # add to parameter block
            prmblck[vdgName].append(af_SSA_h+ " = "+ivd.ssA_h.ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_SSA_s+ " = "+ivd.ssA_s.ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_SSA_p+ " = "+ivd.ssA_p)
            # add parameters to RANGE varible list
            nblck.rangeVariables.append(af_SSA_h)
            nblck.rangeVariables.append(af_SSA_s)
            nblck.rangeVariables.append(af_SSA_p)


            if ssA_Type == '1':
                self.procRates[vdgName] = [af_SSA+ ' = 1/(1 + exp(('+af_SSA_h+'-v)/'+af_SSA_s+'))^'+af_SSA_p]
            if ssA_Type == '2':
                af_SSA_An = af_SSA_prefix+ 'An'
                self.procRates[vdgName] = [af_SSA+ ' = (1 - '+af_SSA_An+')/(1 + exp(('+af_SSA_h+'-v)/'+af_SSA_s+'))^'+af_SSA_p+' + '+ af_SSA_An]
                prmblck[vdgName].append(af_SSA_An+ " = "+ivd.ssA_An)
                nblck.rangeVariables.append(af_SSA_An)

            # write time constant
            tauType = ivd.tAType
            af_tau_tx = af_tau_prefix +'tx'
            
            # convert seconds to ms
            tau_tx = float(ivd.tA_tx) * 1000.0

            
            prmblck[vdgName].append(af_tau_tx+ " = "+str(tau_tx).ljust(lj) + "(ms)")
            nblck.rangeVariables.append(af_tau_tx)
            if tauType == '1':
                self.procRates[vdgName].append(af_tau+ ' = ' + af_tau_tx)
                
            if tauType in ['2', '3']:

                af_tau_h1 = af_tau_prefix +'h1'
                prmblck[vdgName].append(af_tau_h1+ " = "+ivd.tA_h1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(af_tau_h1)
                
                af_tau_s1 = af_tau_prefix +'s1'
                prmblck[vdgName].append(af_tau_s1+ " = "+ivd.tA_s1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(af_tau_h1)


                tau_tn = float(ivd.tA_tn) * 1000.0
                af_tau_tn = af_tau_prefix +'tn'
                prmblck[vdgName].append(af_tau_tn+ " = "+str(tau_tn).ljust(lj) + "(ms)")
                nblck.rangeVariables.append(af_tau_tn)
                    
                af_tau_p1 = af_tau_prefix +'p1'
                prmblck[vdgName].append(af_tau_p1+ " = "+ivd.tA_p1)
                nblck.rangeVariables.append(af_tau_p1)
                
                if tauType == '2':
                    self.procRates[vdgName].append(af_tau+ ' = (' +af_tau_tx+ ' - '+af_tau_tn+')/ (1 + exp((v-'+af_tau_h1+')/'+af_tau_s1+'))^'+af_tau_p1 + ' + ' + af_tau_tn)
                    
                if tauType == '3':
                    af_tau_p2 = af_tau_prefix +'p2'
                    prmblck[vdgName].append(af_tau_p2+ " = "+ivd.tA_p2)
                    nblck.rangeVariables.append(af_tau_p2)

                    af_tau_h2 = af_tau_prefix +'h2'
                    prmblck[vdgName].append(af_tau_h2+ " = "+ivd.tA_h2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(af_tau_h2)

                    af_tau_s2 = af_tau_prefix +'s2'
                    prmblck[vdgName].append(af_tau_s2+ " = "+ivd.tA_s2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(af_tau_s2)
                    
                    
                    self.procRates[vdgName].append(af_tau+ ' = (' +af_tau_tx+ ' - '+af_tau_tn+')/ (1 + exp((v-'+af_tau_h1+')/'+af_tau_s1+'))^'+af_tau_p1 + ' /(1+exp((v-' +af_tau_h2+ ')/' +af_tau_s2+ '))^'+af_tau_p2 +' + ' + af_tau_tn)
        pass


    def fill_ivd_B(self, vdgName, vgdPrefix, ivd):
        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        #self.globalVariables
        
        lj = self.lJust1
        
        bf_Type = ivd.BType
        
        bf = vgdPrefix+'B'
        bfPrefix = bf+'_'
        
        bf_SSB = bfPrefix +'SSB'
        bf_tau = bfPrefix +'tau'
        bf_SSB_prefix = bf_SSB+'_'
        bf_tau_prefix = bf_tau +'_'
        
        if bf_Type == "2":
            # add rate paramters to GLOBAL variable list
            nblck.globalVariables.append(bf_SSB)
            nblck.globalVariables.append(bf_tau)
            #add rate paramters to ASSIGNED block
            assgndblck.rateParameters.append(bf_SSB)
            assgndblck.rateParameters.append(bf_tau.ljust(lj) +"(ms)")
            
            # add activation fucntion to state varables block
            stateblck.append(bf)
            # add intialitation of activation fucntion
            initblck.append(bf +" = " + bf_SSB)

            # add activation fucntion to derivative block
            dvblck.append(bf+"\' = ("+bf_SSB+ " - " +bf+") / " +bf_tau)

            # write steady state
            ssB_Type = ivd.ssBType
            bf_SSB_h = bf_SSB_prefix+ 'h'
            bf_SSB_s = bf_SSB_prefix+ 's'
            bf_SSB_p = bf_SSB_prefix+ 'p'
            
            # add to parameter block
            prmblck[vdgName].append(bf_SSB_h+ " = "+ivd.ssB_h.ljust(lj) + "(mV)")
            prmblck[vdgName].append(bf_SSB_s+ " = "+ivd.ssB_s.ljust(lj) + "(mV)")
            prmblck[vdgName].append(bf_SSB_p+ " = "+ivd.ssB_p)
            # add parameters to RANGE varible list
            nblck.rangeVariables.append(bf_SSB_h)
            nblck.rangeVariables.append(bf_SSB_s)
            nblck.rangeVariables.append(bf_SSB_p)


            if ssB_Type == '1':
                self.procRates[vdgName] = [bf_SSB+ ' = 1/(1 + exp(('+bf_SSB_h+'-v)/'+bf_SSB_s+'))^'+bf_SSB_p]
            if ssB_Type == '2':
                bf_SSB_Bn = bf_SSB_prefix+ 'Bn'
                self.procRates[vdgName] = [bf_SSB+ ' = (1 - '+bf_SSB_Bn+')/(1 + exp(('+bf_SSB_h+'-v)/'+bf_SSB_s+'))^'+bf_SSB_p+' + '+ bf_SSB_Bn]
                prmblck[vdgName].append(bf_SSB_Bn+ " = "+ivd.ssB_Bn)
                nblck.rangeVariables.append(bf_SSB_Bn)

            # write time constant
            tauType = ivd.tBType
            bf_tau_tx = bf_tau_prefix +'tx'
            
            # convert seconds to ms
            tau_tx = float(ivd.tB_tx) * 1000.0

            
            prmblck[vdgName].append(bf_tau_tx+ " = "+str(tau_tx).ljust(lj) + "(ms)")
            nblck.rangeVariables.append(bf_tau_tx)
            if tauType == '1':
                self.procRates[vdgName].append(bf_tau+ ' = ' + bf_tau_tx)
                
            if tauType in ['2', '3']:

                bf_tau_h1 = bf_tau_prefix +'h1'
                prmblck[vdgName].append(bf_tau_h1+ " = "+ivd.tB_h1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(bf_tau_h1)
                
                bf_tau_s1 = bf_tau_prefix +'s1'
                prmblck[vdgName].append(bf_tau_s1+ " = "+ivd.tB_s1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(bf_tau_h1)


                tau_tn = float(ivd.tB_tn) * 1000.0
                bf_tau_tn = bf_tau_prefix +'tn'
                prmblck[vdgName].append(bf_tau_tn+ " = "+str(tau_tn).ljust(lj) + "(ms)")
                nblck.rangeVariables.append(bf_tau_tn)
                    
                bf_tau_p1 = bf_tau_prefix +'p1'
                prmblck[vdgName].append(bf_tau_p1+ " = "+ivd.tB_p1)
                nblck.rangeVariables.append(bf_tau_p1)
                
                if tauType == '2':
                    self.procRates[vdgName].append(bf_tau+ ' = (' +bf_tau_tx+ ' - '+bf_tau_tn+')/ (1 + exp((v-'+bf_tau_h1+')/'+bf_tau_s1+'))^'+bf_tau_p1 + ' + ' + bf_tau_tn)
                    
                if tauType == '3':
                    bf_tau_p2 = bf_tau_prefix +'p2'
                    prmblck[vdgName].append(bf_tau_p2+ " = "+ivd.tB_p2)
                    nblck.rangeVariables.append(bf_tau_p2)

                    bf_tau_h2 = bf_tau_prefix +'h2'
                    prmblck[vdgName].append(bf_tau_h2+ " = "+ivd.tB_h2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(bf_tau_h2)

                    bf_tau_s2 = bf_tau_prefix +'s2'
                    prmblck[vdgName].append(bf_tau_s2+ " = "+ivd.tB_s2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(bf_tau_s2)
                    
                    
                    self.procRates[vdgName].append(bf_tau+ ' = (' +bf_tau_tx+ ' - '+bf_tau_tn+')/ (1 + exp((v-'+bf_tau_h1+')/'+bf_tau_s1+'))^'+bf_tau_p1 + ' /(1+exp((v-' +bf_tau_h2+ ')/' +bf_tau_s2+ '))^'+bf_tau_p2 +' + ' + bf_tau_tn)
        pass



    def fillUnitsBlock(self):

        self.unitsBlock = ['(mA) = (milliamp)', '(mV) = (millivolt)', '(S) = (siemens)',
                           '(molar) = (1/liter)', '(mM) = (millimolar)']
        pass

    def writeModFile(self):

        modFile = os.path.join(self.modFilePath,self.neuronBlock.mechName+".mod")
        with open(modFile, "w") as mf:

            # write UNITS Block
            self.writeUnitsBlock(mf)
            
            # write NEURON Block
            self.writeNEURONBlock(mf)

            # write PARAMETER Block
            self.writeParameterBlock(mf)

            # write ASSIGNED Block
            self.writeAssignedBlock(mf)

            # write INITIAL Block
            self.writeInitialBlock(mf)

            # write STATE Block
            self.writeStateBlock(mf)
            
            # write BREAKPOINT Block
            self.writeBreakpointBlock(mf)

            # write DERIVATIVE Block
            self.writeDerivativeBlock(mf)

            # write PROCEDURE rates
            self.writeProcRates(mf)
            pass
        pass

    

    def writeAssignedBlock(self, mf):
        mf.write("ASSIGNED {\n")

        mf.write("\t: currents\n")
        for cr in self.assignedBlock.currents:
            mf.write("\t"+cr+"\n")
        mf.write("\n")
        
        mf.write("\t: conductances\n")
        for cd in self.assignedBlock.conductances:
            mf.write("\t"+cd+"\n")
        mf.write("\n")
        
        mf.write("\t: reverse potentials\n")
        for rp in self.assignedBlock.reversePots:
            mf.write("\t"+rp+"\n")
        mf.write("\n")
        
        mf.write("\t: rateParameters\n")
        for rp in self.assignedBlock.rateParameters:
            mf.write("\t"+rp+"\n")

        mf.write("}\n")
        pass

    def writeParameterBlock(self, mf):
        mf.write("PARAMETER {\n")
        for vName in self.parameterBlock.keys():
            mf.write("\t: "+vName+"\n")
            for pbl in self.parameterBlock[vName]:
                mf.write("\t"+pbl+"\n")
            mf.write("\n")
        mf.write("}\n\n")
        pass


    def writeInitialBlock(self, mf):
        mf.write("INITIAL {\n")
        mf.write("\trates(v,t)\n")
        for inl in self.initialBlock:
            mf.write("\t"+inl+"\n")
        mf.write("}\n\n")
        pass
    
    def writeStateBlock(self, mf):
        mf.write("STATE {\n")

        for stl in self.stateBlock:
            mf.write("\t"+stl+"\n")
        mf.write("}\n\n")
        pass
    
    def writeDerivativeBlock(self, mf):
        mf.write("DERIVATIVE states  {\n")
        mf.write("\trates(v,t)\n")
        for dvl in self.derivativeBlock:
            mf.write("\t"+dvl+"\n")
        mf.write("}\n\n")
        pass


    def writeBreakpointBlock(self, mf):
        mf.write("BREAKPOINT {\n")
        if len(self.stateBlock) > 0:
            mf.write("\tSOLVE states METHOD cnexp\n")
        for vName in self.breakpointBlock.keys():
            mf.write("\t: "+vName+"\n")
            for bpl in self.breakpointBlock[vName]:
                mf.write("\t"+bpl+"\n")
            mf.write("\n")
        mf.write("}\n\n")
        pass

    def writeNEURONBlock(self, mf):
        mf.write("NEURON {\n")
        mf.write("\tSUFFIX " +self.neuronBlock.mechName+ "\n")

        # write USEION statements
        for ions in self.neuronBlock.useIons:
            mf.write("\t"+ions+"\n")
        mf.write("\n")

        # write NONSPECIFIC_CURRENT statements
        for ns in self.neuronBlock.nsCurrents:
            mf.write("\t"+ns+"\n")
            
        # write RANGE variables
        mf.write("\tRANGE\n")
        mf.write("\t\t" + ", ".join(self.neuronBlock.rangeVariables) + "\n\n")
        
        # write GLOBAL variables
        mf.write("\tGLOBAL\n")
        mf.write("\t\t" + ", ".join(self.neuronBlock.globalVariables) + "\n\n")
        mf.write("\tTHREADSAFE : assigned GLOBALs will be per thread\n")
        
            
        mf.write("}\n\n")
        pass

    def writeProcRates(self, mf):
        mf.write("PROCEDURE rates(v(mV), t(ms)) {\n")
        mf.write("\tUNITSOFF\n")
        for vName in self.procRates.keys():
            mf.write("\t: "+vName+"\n")
            for prl in self.procRates[vName]:
                mf.write("\t"+prl+"\n")
            mf.write("\n")
            
        mf.write("\tUNITSON\n")
        mf.write("}\n\n")
        pass


    
    def writeUnitsBlock(self, mf):
        mf.write("UNITS {\n")
        for u in self.unitsBlock:
            mf.write("\t"+u+"\n")
        mf.write("}\n\n")
        pass

    
    pass

