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
import os

class AssignedBlock():
    def __init__(self):
        self.fromNEURON = ['v (mV)', 'celsius (degC)']
        self.rateParameters = []
        self.currents = []
        self.conductances = []
        self.reversePots = []

class NEURONBlock():
    def __init__(self, nName):
        self.mechName = nName+ "_mechs"
        self.useIons = []
        self.nsCurrents = []
        self.specificCurrents = []
        self.rangeVariables = []
        self.globalVariables = []

class ModVariables():
    def __init__(self):
        self.varName = ''
        # variable is ranged or not
        self.isRanged = 1
        # variable is parameter or assigned
        self.isParameter = 1
        self.unit = ''

class NRNModFile():
    def __init__(self, nName, modFilePath, nObject, modInjList):
        self.nrnName = nName
        self.modFilePath = modFilePath
        self.nrnObject = nObject
        self.modInjList = modInjList

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
        self.readIons()

        self.readSMs()

        # write mod file
        self.writeModFile()


    def readSMs(self):
        secondMessengers = self.nrnObject.smPools
        lj = self.lJust1

        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        for smName in secondMessengers.keys():
            sm = secondMessengers[smName]

            smName = smName.lower()
            smPrefix = smName+ '_'
            smConcName = smPrefix+'C'
            smConcPrefix = smConcName +'_'
            smConcType = sm.smType
            smConc_tau = sm.tau
            sm_xCsmType = sm.xCsmType

            tauName = smConcPrefix+'tau'
            smModName = smConcPrefix+'MOD'
            smModPrefix = smModName+'_'
            # convert tau in SNNAP to correct units in modfile (sec to milisec)

            print("smConc_tau: ", smConc_tau)
            smConc_tau = 1000.0*float(smConc_tau)

            # for: Csm type = 1
            # add sm concentration fucntion to state varables block
            stateblck.append(smConcName+ "\t(mM)")
            # add intialitation of sm concentration
            initblck.append(smConcName +" = 0.0")

            xCsm = 1.0
            if sm_xCsmType == '2':
                print("WARNING!: xCsm type 2 is not supported yet!!")
                print("Exiting...")
                sys.exit(-1)
            dvblck.append(smConcName+"\' = ("+smModName+" - "+smConcName+")/"+str(smConc_tau))

            modInj_start = '0.0'
            modInj_stop = '0.0'
            modInj_mag = '0.0'

            for modInj in self.modInjList:
                # check modulator treatment is applied to this neuron
                if modInj.neuronName != self.nrnName and modInj.sm != smName:
                    continue
                modInj_start = str(1000* float(modInj.start))
                modInj_stop = str(1000* float(modInj.stop))
                # convert units of concentraion
                # (modulator magnitude is in the same units in both SNNAP and NEURON)
                modInj_mag = str(1.0* float(modInj.magnitude))

                # set up sm modulation
                # modulation of sm is also calculated by rates(v, t) function
                prName = "sm modulation, " + smModName
                self.procRates[prName] = []
                self.procRates[prName].append("if(t>"+modInj_start+" && t<"+modInj_stop+") {")
                self.procRates[prName].append("\t"+smModName+" = "+modInj_mag+"\n\t}")
                self.procRates[prName].append("else {")
                self.procRates[prName].append("\t"+smModName+" = 0.0\n\t}")

                nblck.globalVariables.append(smModName)
                assgndblck.rateParameters.append(smModName.ljust(lj) +"(mM)")

                pBlockComment = smPrefix+'SM'
                prmblck[pBlockComment] = []
                # add sm parameters to RANGE and PARAMETER blocks
                prmblck[pBlockComment].append(tauName+ " = "+(str(smConc_tau)).ljust(lj) + "(ms)")
                nblck.rangeVariables.append(tauName)

            # find VDGs regulated by this second messenger and ammend it's calculation
            for cBySM in self.nrnObject.condBySM:
                print("+++++cBySM.cond " + cBySM.cond +" SM : "+ smName)
                print("cBySM.sm,  smName: ", cBySM.sm, smName)
                if cBySM.sm.lower() == smName.lower():
                    print("SM " +smName + " regulates cond. "  +cBySM.cond)

                    BRType = cBySM.fbr.BRType
                    fBRType = cBySM.fbr.fBRType
                    BR_a = cBySM.fbr.BR_a
                    br_aName = smPrefix + '2' + cBySM.cond+'_br_a'

                    # add fBR file parameter to RANGE and PARAMETER blocks
                    prmblck[pBlockComment].append(br_aName+ " = "+BR_a.ljust(lj) + "(mM)")
                    nblck.rangeVariables.append(br_aName)

                    # default br
                    br='0.0'
                    if BRType =='2':
                        br = smConcName + '/('+br_aName+'+'+smConcName+')'
                    elif BRType =='3':
                        br = '1'+ iConcName + '/('+br_aName+'+'+smConcName+')'
                    elif BRType =='4':
                        br = '1 / (1+ '+br_aName+'*'+smConcName+')'
                    else:
                        print("WARNING!: Modulation by regulator models(BR) 1 is not supported yet!!")

                    # default fbr
                    fbr = '0.0'
                    if fBRType == '1':
                        fbr = br
                    elif fBRType == '2':
                        fbr = '1.0 + ' + br
                    else:
                        print("WARNING!: Modulation by regulator model(fBR) 3 is not supported yet!!")

                    print("FBR = ", fbr)
                    brkpblck[cBySM.cond][0] = brkpblck[cBySM.cond][0] + ' * (' +fbr+')'
                    print(brkpblck[cBySM.cond][0])
                    print("cBySM.cond " , cBySM.cond)

    def readIons(self):
        ions = self.nrnObject.ionPools
        lj = self.lJust1

        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        for ionName in ions.keys():
            ion = ions[ionName]

            iName = ionName.lower()
            iPrefix = iName+ '_'
            iConcName = iPrefix+'C'
            iConcPrefix = iConcName +'_'
            iConcType = ion.cionType
            iConc_k1 = ion.k1
            iConc_k2 = ion.k2

            tauName = iConcPrefix+'tau'
            k2Name = iConcPrefix+'k2'
            # convert K2 in SNNAP to correct units in modfile
            k2 = 1.0e6 * float(iConc_k2)
            # rearrange K1 in SNNAP as a time constant
            tauName = iConcPrefix+'tau'
            iConc_tau = 1000.0/float(iConc_k1)


            if iConcType == '2':
                # add ion concentration fucntion to state varables block
                stateblck.append(iConcName+ "\t(mM)")
                # add intialitation of ion concentration
                initblck.append(iConcName +" = 0.0")

                # find contributing currntes for this ion
                contributingvdgName = []
                for cr2Ion in self.nrnObject.curr2Ions:
                    if ionName ==cr2Ion.ion:
                        vdgName = cr2Ion.cond
                        # construction of vName has to match with vName construction in readVDG()
                        vName = vdgName.lower()
                        currName = 'i'+vName
                        contributingvdgName.append(currName)

                # add ion concentration to derivative block
                dvblck.append(iConcName+"\' = (-"+k2Name+" * ("+ "+".join(contributingvdgName) + ") - "+iConcName +")/"+str(iConc_tau))

                pBlockComment = iPrefix+'ion'
                # add ion parameters to RANGE and PARAMETER blocks
                prmblck[pBlockComment] = [k2Name+ " = "+str(k2).ljust(lj) + "(mM-cm2/mA)"]
                nblck.rangeVariables.append(k2Name)
                prmblck[pBlockComment].append(tauName+ " = "+(str(iConc_tau)).ljust(lj) + "(ms)")
                nblck.rangeVariables.append(tauName)

                # find VDGs regulated by this ion and ammend it's calculation
                for cByI in self.nrnObject.condByIon:
                    print("-----cByI.cond " + cByI.cond +" ION: "+ ionName)
                    if cByI.ion == ionName:
                        print("Ion " +ionName + " regulates cond. "  +cByI.cond)

                        BRType = cByI.BRType
                        fBRType = cByI.fBRType
                        BR_a = cByI.BR_a
                        br_aName = iPrefix + '2' + cByI.cond+'_br_a'
                        # br_aName = iPrefix+'br_a'

                        # add fBR file parameter to RANGE and PARAMETER blocks
                        prmblck[pBlockComment].append(br_aName+ " = "+BR_a.ljust(lj) + "(mM)")
                        nblck.rangeVariables.append(br_aName)

                        # default br
                        br='0.0'
                        if BRType =='2':
                            br = iConcName + '/('+br_aName+'+'+iConcName+')'
                        elif BRType =='3':
                            br = '1'+ iConcName + '/('+br_aName+'+'+iConcName+')'
                        elif BRType =='4':
                            br = '1 / (1+ '+br_aName+'*'+iConcName+')'
                        else:
                            print("WARNING!: Modulation by regulator models(BR) 1 is not supported yet!!")

                        # default fbr
                        fbr = '0.0'
                        if fBRType == '1':
                            fbr = br
                        elif fBRType == '2':
                            fbr = '1.0 + ' + br
                        else:
                            print("WARNING!: Modulation by regulator model(fBR) 3 is not supported yet!!")

                        brkpblck[cByI.cond][0] = brkpblck[cByI.cond][0] + ' * (' +fbr+')'
                        print(brkpblck[cByI.cond][0])
                        print("cByI.cond " , cByI.cond)

                        # find which specific or non-spec. current cByI.cond need to be added
                        # for cByI.cond to be accounted towards the current balance eqn.
                        # if cByI.cond[0].lower() == 'k':
                        #     brkpblck['ammend K'] = ['ik = ik + i'+cByI.cond.lower()]
            else:
                print("WARNING!: ion concentraion model 1 is not supported yet!!")
                print("Exiting...")
                sys.exit(-1)

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
                print("vdgName: ", vdgName)
                ui = "USEION " +vName+ " READ e" +vName+ " WRITE " +currntName
                nblck.useIons.append(ui)
            else:
                nblck.nsCurrents.append(currntName)

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
                    print("WARNING!: could not convert "+vdgName+ " conductance of neuron " + nName)
                    print("Exited unexpectedly!")
                    sys.exit(-1)

            if ivdType == '5':
                if vName == "leak":
                    #currntName = "il"
                    revPotName = "el"
                    gName = "gl"
                    #nblck.nsCurrents.append('NONSPECIFIC_CURRENT ' + currntName)

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
                self.headComments.append(":_A"+aType+"_B"+bType+"\t"+vdgName)

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

                # add current parameters to BREAKPOINT block
                ivd_A = vgdPrefix +"A"
                ivd_p = vgdPrefix +"p"
                prmblck[vdgName].append(ivd_p+ " = "+(vdgs[vdgName].P).ljust(lj))
                nblck.rangeVariables.append(ivd_p)
                if ivdType == '1':
                    ivd_B = vgdPrefix +"B"
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * ('+ivd_A+'^'+ivd_p+') * '+ivd_B]
                    self.fill_ivd_A(vdgName, vgdPrefix, vdgs[vdgName])
                    self.fill_ivd_B(vdgName, vgdPrefix, vdgs[vdgName])

                if ivdType == '3':
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * '+ivd_A+'^'+ivd_p]
                    self.fill_ivd_A(vdgName, vgdPrefix, vdgs[vdgName])

                brkpblck[vdgName].append(currntName+ ' = '+gName +'*(v - '+revPotName+')')

            if ivdType == '2' or ivdType == '4':
                self.headComments.append(":_m"+mType+"_h"+hType+"\t"+vdgName)

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

                # add current parameters to BREAKPOINT block
                ivd_m = vgdPrefix +"m"
                ivd_p = vgdPrefix +"p"
                prmblck[vdgName].append(ivd_p+ " = "+(vdgs[vdgName].P).ljust(lj))
                nblck.rangeVariables.append(ivd_p)
                if ivdType == '2':
                    ivd_h = vgdPrefix +"h"
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * ('+ivd_m+'^'+ivd_p+') * '+ivd_h]
                    self.fill_ivd_m(vdgName, vgdPrefix, vdgs[vdgName])
                    self.fill_ivd_h(vdgName, vgdPrefix, vdgs[vdgName])

                if ivdType == '4':
                    brkpblck[vdgName] = [gName+ ' = '+gbarName +' * '+ivd_m+'^'+ivd_p]
                    self.fill_ivd_m(vdgName, vgdPrefix, vdgs[vdgName])
                brkpblck[vdgName].append(currntName+ ' = '+gName +'*(v - '+revPotName+')')
                pass

    def fill_ivd_h(self, vdgName, vgdPrefix, ivd):
        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        lj = self.lJust1

        af_Type = ivd.hType

        af = vgdPrefix+'h'
        afPrefix = af+'_'

        af_L = afPrefix+'L'
        af_ah = afPrefix+'ah'
        af_bh = afPrefix+'bh'

        af_ah_prefix = af_ah + '_'
        af_bh_prefix = af_bh + '_'

        if af_Type == '1':
            print("WARNING: Activation function type 1 is not suppoeterd yet!!")
            print("Exiting...")
            sys.exit()

        # scale L, and add it to parameter block as well as Range block
        m_L = 1
        if af_Type == '3':
            m_L = ivd.m_L
        # reciprocal of m_L in 1/ms
        m_rL = 1000.0/float(m_L)
        prmblck[vdgName].append(af_L+ " = "+str(m_rL).ljust(lj) + "(ms)")
        nblck.rangeVariables.append(af_L)

        # add rate parameters to GLOBAL variable list
        nblck.globalVariables.append(af_ah)
        nblck.globalVariables.append(af_bh)
        #add rate paramters to ASSIGNED block
        assgndblck.rateParameters.append(af_ah)
        assgndblck.rateParameters.append(af_bh)

        # add activation fucntion to state varables block
        stateblck.append(af)
        # add intialitation of activation fucntion
        initblck.append(af +" = " + af_ah +"/("+af_ah+"+"+af_bh+")")

        # add activation fucntion to derivative block
        dvblck.append(af+"\' = ("+af_ah+"*(1-"+af+ ") - " +af_bh+"*"+af+")/"+af_L)

        # write rate paramtes
        ah_Type = ivd.ahType

        af_ah_A = af_ah_prefix + 'A'
        af_ah_B = af_ah_prefix + 'B'
        af_ah_C = af_ah_prefix + 'C'
        af_ah_D = af_ah_prefix + 'D'

        prName = vdgName+"_m"
        if ah_Type == '1':
            self.procRates[prName].append(af_ah+ ' = ' + af_ah_A)
            prmblck[vdgName].append(af_ah_A+ " = "+ivd.ah_A)
            nblck.rangeVariables.append(af_ah_A)

        if ah_Type in ['2', '3']:
            prmblck[vdgName].append(af_ah_A+ " = "+ivd.ah_A)
            prmblck[vdgName].append(af_ah_B+ " = "+(ivd.ah_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_ah_C+ " = "+(ivd.ah_C).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_ah_D+ " = "+(ivd.ah_D).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_ah_A)
            nblck.rangeVariables.append(af_ah_D)
            nblck.rangeVariables.append(af_ah_C)
            nblck.rangeVariables.append(af_ah_D)

            if ah_Type == '2':
                self.procRates[prName].append(af_ah+ ' = '+af_ah_A+'*(v+' +af_ah_B+')/(1+exp(('+af_ah_C+'-v)/'+af_ah_D+'))')
            if ah_Type == '3':
                self.procRates[prName].append(af_ah+ ' = '+af_ah_A+'*(v+' +af_ah_B+')/(1-exp(('+af_ah_C+'-v)/'+af_ah_D+'))')

        if ah_Type in ['4', '8', '9']:
            prmblck[vdgName].append(af_ah_A+ " = "+(ivd.ah_A).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_ah_B+ " = "+(ivd.ah_B).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_ah_A)
            nblck.rangeVariables.append(af_ah_B)

            if ah_Type == '4':
                self.procRates[prName].append(af_ah+ ' = 1+exp(('+af_ah_A+'-v)/'+af_ah_B+')')
            if ah_Type == '8':
                self.procRates[prName].append(af_ah+ ' = 1/(1+exp(('+af_ah_A+'-v)/'+af_ah_B+'))')
            if ah_Type == '9':
                self.procRates[prName].append(af_ah+ ' = 1/(1-exp(('+af_ah_A+'-v)/'+af_ah_B+'))')

        if ah_Type in ['5', '6', '7']:
            prmblck[vdgName].append(af_ah_A+ " = "+ivd.ah_A)
            prmblck[vdgName].append(af_ah_B+ " = "+(ivd.ah_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_ah_C+ " = "+(ivd.ah_C).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_ah_A)
            nblck.rangeVariables.append(af_ah_D)
            nblck.rangeVariables.append(af_ah_C)

            if ah_Type == '5':
                self.procRates[prName].append(af_ah+ ' = '+af_ah_A+'*exp(('+af_ah_B+'-v)/'+af_ah_C+')')
            if ah_Type == '6':
                self.procRates[prName].append(af_ah+ ' = '+af_ah_A+'/(1+exp(('+af_ah_B+'-v)/'+af_ah_C+'))')
            if ah_Type == '7':
                self.procRates[prName].append(af_ah+ ' = '+af_ah_A+'/(1-exp(('+af_ah_B+'-v)/'+af_ah_C+'))')

        # write rate paramte: bh
        bh_Type = ivd.bhType

        af_bh_A = af_bh_prefix + 'A'
        af_bh_B = af_bh_prefix + 'B'
        af_bh_C = af_bh_prefix + 'C'
        af_bh_D = af_bh_prefix + 'D'

        if bh_Type == '1':
            self.procRates[prName].append(af_bh+ ' = ' + af_bh_A)
            prmblck[vdgName].append(af_bh_A+ " = "+ivd.bh_A)
            nblck.rangeVariables.append(af_bh_A)

        if bh_Type in ['2', '3']:
            prmblck[vdgName].append(af_bh_A+ " = "+ivd.bh_A)
            prmblck[vdgName].append(af_bh_B+ " = "+(ivd.bh_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bh_C+ " = "+(ivd.bh_C).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bh_D+ " = "+(ivd.bh_D).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bh_A)
            nblck.rangeVariables.append(af_bh_D)
            nblck.rangeVariables.append(af_bh_C)
            nblck.rangeVariables.append(af_bh_D)

            if bh_Type == '2':
                self.procRates[prName].append(af_bh+ ' = '+af_bh_A+'*(v+' +af_bh_B+')/(1+exp(('+af_bh_C+'-v)/'+af_bh_D+'))')
            if bh_Type == '3':
                self.procRates[prName].append(af_bh+ ' = '+af_bh_A+'*(v+' +af_bh_B+')/(1-exp(('+af_bh_C+'-v)/'+af_bh_D+'))')

        if bh_Type in ['4', '8', '9']:
            prmblck[vdgName].append(af_bh_A+ " = "+(ivd.bh_A).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bh_B+ " = "+(ivd.bh_B).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bh_A)
            nblck.rangeVariables.append(af_bh_B)

            if bh_Type == '4':
                self.procRates[prName].append(af_bh+ ' = 1+exp(('+af_bh_A+'-v)/'+af_bh_B+')')
            if bh_Type == '8':
                self.procRates[prName].append(af_bh+ ' = 1/(1+exp(('+af_bh_A+'-v)/'+af_bh_B+'))')
            if bh_Type == '9':
                self.procRates[prName].append(af_bh+ ' = 1/(1-exp(('+af_bh_A+'-v)/'+af_bh_B+'))')

        if bh_Type in ['5', '6', '7']:
            prmblck[vdgName].append(af_bh_A+ " = "+ivd.bh_A)
            prmblck[vdgName].append(af_bh_B+ " = "+(ivd.bh_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bh_C+ " = "+(ivd.bh_C).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bh_A)
            nblck.rangeVariables.append(af_bh_D)
            nblck.rangeVariables.append(af_bh_C)

            if bh_Type == '5':
                self.procRates[prName].append(af_bh+ ' = '+af+bh_A+'*exp(('+af_bh_B+'-v)/'+af_bh_C+')')
            if bh_Type == '6':
                self.procRates[prName].append(af_bh+ ' = '+af_bh_A+'/(1+exp(('+af_bh_B+'-v)/'+af_bh_C+'))')
            if bh_Type == '7':
                self.procRates[prName].append(af_bh+ ' = '+af_bh_A+'/(1-exp(('+af_bh_B+'-v)/'+af_bh_C+'))')

    def fill_ivd_m(self, vdgName, vgdPrefix, ivd):
        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        lj = self.lJust1

        af_Type = ivd.mType

        af = vgdPrefix+'m'
        afPrefix = af+'_'

        af_L = afPrefix+'L'
        af_am = afPrefix+'am'
        af_bm = afPrefix+'bm'

        af_am_prefix = af_am + '_'
        af_bm_prefix = af_bm + '_'

        if af_Type == '1':
            print("WARNING: Activation function type 1 is not suppoeterd yet!!")
            print("Exiting...")
            sys.exit()

        # scale L, and add it to parameter block as well as Range block
        m_L = 1
        if af_Type == '3':
            m_L = ivd.m_L
        m_rL = 1000.0 /float(m_L)
        prmblck[vdgName].append(af_L+ " = "+str(m_rL).ljust(lj) + "(ms)")
        nblck.rangeVariables.append(af_L)

        # add rate parameters to GLOBAL variable list
        nblck.globalVariables.append(af_am)
        nblck.globalVariables.append(af_bm)
        #add rate paramters to ASSIGNED block
        assgndblck.rateParameters.append(af_am)
        assgndblck.rateParameters.append(af_bm)

        # add activation fucntion to state varables block
        stateblck.append(af)
        # add intialitation of activation fucntion
        initblck.append(af +" = " + af_am +"/("+af_am+"+"+af_bm+")")

        # add activation fucntion to derivative block
        dvblck.append(af+"\' = ("+af_am+"*(1-"+af+ ") - " +af_bm+"*"+af+")/"+af_L )

        # write rate paramtes
        am_Type = ivd.amType

        af_am_A = af_am_prefix + 'A'
        af_am_B = af_am_prefix + 'B'
        af_am_C = af_am_prefix + 'C'
        af_am_D = af_am_prefix + 'D'

        prName = vdgName+"_m"
        if am_Type == '1':
            self.procRates[prName] = [af_am+ ' = ' + af_am_A]
            prmblck[vdgName].append(af_am_A+ " = "+ivd.am_A)
            nblck.rangeVariables.append(af_am_A)

        if am_Type in ['2', '3']:
            prmblck[vdgName].append(af_am_A+ " = "+ivd.am_A)
            prmblck[vdgName].append(af_am_B+ " = "+(ivd.am_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_am_C+ " = "+(ivd.am_C).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_am_D+ " = "+(ivd.am_D).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_am_A)
            nblck.rangeVariables.append(af_am_D)
            nblck.rangeVariables.append(af_am_C)
            nblck.rangeVariables.append(af_am_D)

            if am_Type == '2':
                self.procRates[prName] = [af_am+ ' = '+af_am_A+'*(v+' +af_am_B+')/(1+exp(('+af_am_C+'-v)/'+af_am_D+'))']
            if am_Type == '3':
                self.procRates[prName] = [af_am+ ' = '+af_am_A+'*(v+' +af_am_B+')/(1-exp(('+af_am_C+'-v)/'+af_am_D+'))']

        if am_Type in ['4', '8', '9']:
            prmblck[vdgName].append(af_am_A+ " = "+(ivd.am_A).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_am_B+ " = "+(ivd.am_B).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_am_A)
            nblck.rangeVariables.append(af_am_B)

            if am_Type == '4':
                self.procRates[prName] = [af_am+ ' = 1+exp(('+af_am_A+'-v)/'+af_am_B+')']
            if am_Type == '8':
                self.procRates[prName] = [af_am+ ' = 1/(1+exp(('+af_am_A+'-v)/'+af_am_B+'))']
            if am_Type == '9':
                self.procRates[prName] = [af_am+ ' = 1/(1-exp(('+af_am_A+'-v)/'+af_am_B+'))']

        if am_Type in ['5', '6', '7']:
            prmblck[vdgName].append(af_am_A+ " = "+ivd.am_A)
            prmblck[vdgName].append(af_am_B+ " = "+(ivd.am_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_am_C+ " = "+(ivd.am_C).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_am_A)
            nblck.rangeVariables.append(af_am_D)
            nblck.rangeVariables.append(af_am_C)

            if am_Type == '5':
                self.procRates[prName] = [af_am+ ' = '+af+am_A+'*exp(('+af_am_B+'-v)/'+af_am_C+')']
            if am_Type == '6':
                self.procRates[prName] = [af_am+ ' = '+af_am_A+'/(1+exp(('+af_am_B+'-v)/'+af_am_C+'))']
            if am_Type == '7':
                self.procRates[prName] = [af_am+ ' = '+af_am_A+'/(1-exp(('+af_am_B+'-v)/'+af_am_C+'))']

        # write rate paramte: bm
        bm_Type = ivd.bmType

        af_bm_A = af_bm_prefix + 'A'
        af_bm_B = af_bm_prefix + 'B'
        af_bm_C = af_bm_prefix + 'C'
        af_bm_D = af_bm_prefix + 'D'

        if bm_Type == '1':
            self.procRates[prName].append(af_bm+ ' = ' + af_bm_A)
            prmblck[vdgName].append(af_bm_A+ " = "+ivd.bm_A)
            nblck.rangeVariables.append(af_bm_A)

        if bm_Type in ['2', '3']:
            prmblck[vdgName].append(af_bm_A+ " = "+ivd.bm_A)
            prmblck[vdgName].append(af_bm_B+ " = "+(ivd.bm_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bm_C+ " = "+(ivd.bm_C).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bm_D+ " = "+(ivd.bm_D).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bm_A)
            nblck.rangeVariables.append(af_bm_D)
            nblck.rangeVariables.append(af_bm_C)
            nblck.rangeVariables.append(af_bm_D)

            if bm_Type == '2':
                self.procRates[prName].append(af_bm+ ' = '+af_bm_A+'*(v+' +af_bm_B+')/(1+exp(('+af_bm_C+'-v)/'+af_bm_D+'))')
            if bm_Type == '3':
                self.procRates[prName].append(af_bm+ ' = '+af_bm_A+'*(v+' +af_bm_B+')/(1-exp(('+af_bm_C+'-v)/'+af_bm_D+'))')

        if bm_Type in ['4', '8', '9']:
            prmblck[vdgName].append(af_bm_A+ " = "+(ivd.bm_A).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bm_B+ " = "+(ivd.bm_B).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bm_A)
            nblck.rangeVariables.append(af_bm_B)

            if bm_Type == '4':
                self.procRates[prName].append(af_bm+ ' = 1+exp(('+af_bm_A+'-v)/'+af_bm_B+')')
            if bm_Type == '8':
                self.procRates[prName].append(af_bm+ ' = 1/(1+exp(('+af_bm_A+'-v)/'+af_bm_B+'))')
            if bm_Type == '9':
                self.procRates[prName].append(af_bm+ ' = 1/(1-exp(('+af_bm_A+'-v)/'+af_bm_B+'))')

        if bm_Type in ['5', '6', '7']:
            prmblck[vdgName].append(af_bm_A+ " = "+ivd.bm_A)
            prmblck[vdgName].append(af_bm_B+ " = "+(ivd.bm_B).ljust(lj) + "(mV)")
            prmblck[vdgName].append(af_bm_C+ " = "+(ivd.bm_C).ljust(lj) + "(mV)")

            nblck.rangeVariables.append(af_bm_A)
            nblck.rangeVariables.append(af_bm_D)
            nblck.rangeVariables.append(af_bm_C)

            if bm_Type == '5':
                self.procRates[prName].append(af_bm+ ' = '+af_bm_A+'*exp(('+af_bm_B+'-v)/'+af_bm_C+')')
            if bm_Type == '6':
                self.procRates[prName].append(af_bm+ ' = '+af_bm_A+'/(1+exp(('+af_bm_B+'-v)/'+af_bm_C+'))')
            if bm_Type == '7':
                self.procRates[prName].append(af_bm+ ' = '+af_bm_A+'/(1-exp(('+af_bm_B+'-v)/'+af_bm_C+'))')

    def fill_ivd_A(self, vdgName, vgdPrefix, ivd):
        nblck = self.neuronBlock
        prmblck = self.parameterBlock
        brkpblck = self.breakpointBlock
        assgndblck = self.assignedBlock
        stateblck = self.stateBlock
        initblck = self.initialBlock
        dvblck  = self.derivativeBlock

        lj = self.lJust1

        af_Type = ivd.AType

        af = vgdPrefix+'A'
        afPrefix = af+'_'

        af_SSA = afPrefix +'SSA'
        af_tau = afPrefix +'tau'
        af_SSA_prefix = af_SSA+'_'
        af_tau_prefix = af_tau +'_'

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

        prName = vdgName+"_A"
        if ssA_Type == '1':
            self.procRates[prName] = [af_SSA+ ' = 1/(1 + exp(('+af_SSA_h+'-v)/'+af_SSA_s+'))^'+af_SSA_p]
        if ssA_Type == '2':
            af_SSA_An = af_SSA_prefix+ 'An'
            self.procRates[prName] = [af_SSA+ ' = (1 - '+af_SSA_An+')/(1 + exp(('+af_SSA_h+'-v)/'+af_SSA_s+'))^'+af_SSA_p+' + '+ af_SSA_An]
            prmblck[vdgName].append(af_SSA_An+ " = "+ivd.ssA_An)
            nblck.rangeVariables.append(af_SSA_An)

        # add rate paramters to GLOBAL variable list
        nblck.globalVariables.append(af_SSA)

        #add rate paramters to ASSIGNED block
        assgndblck.rateParameters.append(af_SSA)
        if af_Type == "1":
            assgndblck.rateParameters.append(af)
            self.procRates[prName].append(af +" = " + af_SSA)

        elif af_Type == "2":
            nblck.globalVariables.append(af_tau)
            assgndblck.rateParameters.append(af_tau.ljust(lj) +"(ms)")

            # add activation fucntion to state varables block
            stateblck.append(af)
            # add intialitation of activation fucntion
            initblck.append(af +" = " + af_SSA)
            # add activation fucntion to derivative block
            dvblck.append(af+"\' = ("+af_SSA+ " - " +af+") / " +af_tau)

            tauType = ivd.tAType
            af_tau_tx = af_tau_prefix +'tx'

            # convert seconds to ms
            tau_tx = float(ivd.tA_tx) * 1000.0

            prmblck[vdgName].append(af_tau_tx+ " = "+str(tau_tx).ljust(lj) + "(ms)")
            nblck.rangeVariables.append(af_tau_tx)

            # only time constant types 1, 2 and 3 are suppoeterd yet!!
            if tauType == '1':
                self.procRates[prName].append(af_tau+ ' = ' + af_tau_tx)

            elif tauType in ['2', '3', '6']:

                af_tau_h1 = af_tau_prefix +'h1'
                prmblck[vdgName].append(af_tau_h1+ " = "+ivd.tA_h1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(af_tau_h1)

                af_tau_s1 = af_tau_prefix +'s1'
                prmblck[vdgName].append(af_tau_s1+ " = "+ivd.tA_s1.ljust(lj) + "(mV)")
                nblck.rangeVariables.append(af_tau_h1)

                af_tau_p1 = af_tau_prefix +'p1'
                af_tau_tn = af_tau_prefix +'tn'

                if tauType in ['2', '3']:
                    # af_tau_p1 = af_tau_prefix +'p1'
                    prmblck[vdgName].append(af_tau_p1+ " = "+ivd.tA_p1)
                    nblck.rangeVariables.append(af_tau_p1)

                    tau_tn = float(ivd.tA_tn) * 1000.0
                    #af_tau_tn = af_tau_prefix +'tn'
                    prmblck[vdgName].append(af_tau_tn+ " = "+str(tau_tn).ljust(lj) + "(ms)")
                    nblck.rangeVariables.append(af_tau_tn)

                    if tauType == '2':
                        self.procRates[prName].append(af_tau+ ' = (' +af_tau_tx+ ' - '+af_tau_tn+')/ (1 + exp((v-'+af_tau_h1+')/'+af_tau_s1+'))^'+af_tau_p1 + ' + ' + af_tau_tn)

                if tauType in ['3', '6']:
                    af_tau_h2 = af_tau_prefix +'h2'
                    prmblck[vdgName].append(af_tau_h2+ " = "+ivd.tA_h2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(af_tau_h2)

                    af_tau_s2 = af_tau_prefix +'s2'
                    prmblck[vdgName].append(af_tau_s2+ " = "+ivd.tA_s2.ljust(lj) + "(mV)")
                    nblck.rangeVariables.append(af_tau_s2)

                    if tauType == '3':
                        af_tau_p2 = af_tau_prefix +'p2'
                        prmblck[vdgName].append(af_tau_p2+ " = "+ivd.tA_p2)
                        nblck.rangeVariables.append(af_tau_p2)

                        self.procRates[prName].append(af_tau+ ' = (' +af_tau_tx+ ' - '+af_tau_tn+')/ (1 + exp((v-'+af_tau_h1+')/'+af_tau_s1+'))^'+af_tau_p1 + ' /(1+exp((v-' +af_tau_h2+ ')/' +af_tau_s2+ '))^'+af_tau_p2 +' + ' + af_tau_tn)

                    if tauType == '6':
                        self.procRates[prName].append(af_tau+ ' = ' +af_tau_tx+ '/ (exp((v-'+af_tau_h1+')/'+af_tau_s1+') + exp((' +af_tau_h2+ '-v)/' +af_tau_s2+ '))')

            elif tauType in ['4', '5']:
                print("WARNING: only time constant types 1, 2, 3 and 6 are suppoeterd yet!!")
                print("Exiting...")
                sys.exit()

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


            prName = vdgName+"_B"
            if ssB_Type == '1':
                self.procRates[prName] = [bf_SSB+ ' = 1/(1 + exp((v-'+bf_SSB_h+')/'+bf_SSB_s+'))^'+bf_SSB_p]
            if ssB_Type == '2':
                bf_SSB_Bn = bf_SSB_prefix+ 'Bn'
                self.procRates[prName] = [bf_SSB+ ' = (1 - '+bf_SSB_Bn+')/(1 + exp((v-'+bf_SSB_h+')/'+bf_SSB_s+'))^'+bf_SSB_p+' + '+ bf_SSB_Bn]
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
                self.procRates[prName].append(bf_tau+ ' = ' + bf_tau_tx)

            elif tauType in ['2', '3']:

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
                    self.procRates[prName].append(bf_tau+ ' = (' +bf_tau_tx+ ' - '+bf_tau_tn+')/ (1 + exp((v-'+bf_tau_h1+')/'+bf_tau_s1+'))^'+bf_tau_p1 + ' + ' + bf_tau_tn)

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


                    self.procRates[prName].append(bf_tau+ ' = (' +bf_tau_tx+ ' - '+bf_tau_tn+')/ (1 + exp((v-'+bf_tau_h1+')/'+bf_tau_s1+'))^'+bf_tau_p1 + ' /(1+exp((v-' +bf_tau_h2+ ')/' +bf_tau_s2+ '))^'+bf_tau_p2 +' + ' + bf_tau_tn)
            else:
                print("WARNING: only time constant types 1, 2 and 3 are suppoeterd yet!!")
                print("Exiting...")
                sys.exit()

        else:
            print("WARNING: Inactivation function type 1 is not suppoeterd yet!!")
            print("Exiting...")
            sys.exit()

    def fillUnitsBlock(self):
        self.unitsBlock = ['(mA) = (milliamp)', '(mV) = (millivolt)', '(S) = (siemens)',
                           '(molar) = (1/liter)', '(mM) = (millimolar)']

    def writeModFile(self):
        modFile = os.path.join(self.modFilePath,self.neuronBlock.mechName + ".mod")
        with open(modFile, "w") as mf:
            # write self.headComments
            self.writeHeadComments(mf)

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

    def writeHeadComments(self, mf):
        mf.write(": Head Comments\n")
        for cl in self.headComments:
            mf.write(cl+"\n")

    def writeAssignedBlock(self, mf):
        mf.write("ASSIGNED {\n")

        mf.write("\t: from NEURON\n")
        for cr in self.assignedBlock.fromNEURON:
            mf.write("\t"+cr+"\n")
        mf.write("\n")

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

    def writeParameterBlock(self, mf):
        mf.write("PARAMETER {\n")
        for vName in self.parameterBlock.keys():
            mf.write("\t: "+vName+"\n")
            for pbl in self.parameterBlock[vName]:
                mf.write("\t"+pbl+"\n")
            mf.write("\n")
        mf.write("}\n\n")

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

    def writeBreakpointBlock(self, mf):
        mf.write("BREAKPOINT {\n")
        if len(self.stateBlock) > 0:
            mf.write("\tSOLVE states METHOD cnexp\n")
            mf.write("\trates(v,t)\n") #
        for vName in self.breakpointBlock.keys():
            mf.write("\t: "+vName+"\n")
            for bpl in self.breakpointBlock[vName]:
                mf.write("\t"+bpl+"\n")
            mf.write("\n")
        mf.write("}\n\n")

    def writeNEURONBlock(self, mf):
        mf.write("NEURON {\n")
        mf.write("\tSUFFIX " +self.neuronBlock.mechName+ "\n")

        # write USEION statements
        for ions in self.neuronBlock.useIons:
            mf.write("\t"+ions+"\n")
        mf.write("\n")

        # write NONSPECIFIC_CURRENT statements
        mf.write("\tNONSPECIFIC_CURRENT " + ', '.join(self.neuronBlock.nsCurrents)+"\n\n")
        # nblck.nsCurrents.append('NONSPECIFIC_CURRENT ' + currntName)
        # for ns in self.neuronBlock.nsCurrents:
        #     mf.write("\t"+ns+"\n")

        # write RANGE variables
        mf.write("\tRANGE\n")
        rLine = ", ".join(self.neuronBlock.rangeVariables)
        nRangeVars = len(self.neuronBlock.rangeVariables)

        i = 0
        varsPerLine = 5
        while i < nRangeVars:
            if i+varsPerLine < nRangeVars:
                mf.write("\t\t"+", ".join(self.neuronBlock.rangeVariables[i:i+varsPerLine])+",\n")
            else:
                mf.write("\t\t"+", ".join(self.neuronBlock.rangeVariables[i:])+"\n")
            i = i+varsPerLine

        # write GLOBAL variables
        mf.write("\tGLOBAL\n")
        mf.write("\t\t" + ", ".join(self.neuronBlock.globalVariables) + "\n\n")
        mf.write("\tTHREADSAFE : assigned GLOBALs will be per thread\n")
        mf.write("}\n\n")

    def writeProcRates(self, mf):
        mf.write("PROCEDURE rates(v(mV), t(ms)) {\n")
        mf.write("\tUNITSOFF\n")
        for prName in self.procRates.keys():
            mf.write("\t: "+prName+"\n")
            for prl in self.procRates[prName]:
                mf.write("\t"+prl+"\n")
            mf.write("\n")

        mf.write("\tUNITSON\n")
        mf.write("}\n\n")

    def writeUnitsBlock(self, mf):
        mf.write("\nUNITS {\n")
        for u in self.unitsBlock:
            mf.write("\t"+u+"\n")
        mf.write("}\n\n")
