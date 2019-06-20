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

import util

#class NRNModel():
class NRNModelPoint():

    def __init__(self, sSim):

        self.simName = sSim.simFileName.split('.')[0]
        self.lJust1 = 16

        # use neuron pas
        self.useNrnPas = False
        
        self.neuronlist = {}
        self.neutonFiles = []
        self.chemSynFiles = []
        self.ElecCouplingFile = ""
        self.treatmentFile = None

        # create directory for nrn model
        self.createModelDir(sSim)
        
        # write neurons into files
        self.writeNeurons(sSim)

        # write treatments
        self.writeTreatments(sSim)

        # print to stdout
        # self.printNeurons(sSim)

        # print chemSyn
        self.writeChemSyns(sSim)

        # write electrical couplings
        self.writeElecCoupling(sSim)
        
        # write main file for simulation 
        self.writeMainSimFile(sSim)


    def writeElecCoupling(self, sSim):

        esList = sSim.network.elecSyns
        if len(esList) == 0:
            return
        
        lj = self.lJust1

        neurons = sSim.network.neurons
        coupledNeurons = []
        esf_local = "create_es.hoc"
        esFileName = os.path.join(self.nrnDirPath,self.nrnDirName,esf_local)

        self.ElecCouplingFile = esf_local

        for es in esList:
            if not es.postSyn in coupledNeurons:
                coupledNeurons.append(es.postSyn)
            if not es.preSyn in coupledNeurons:
                coupledNeurons.append(es.preSyn)

        nES = len(coupledNeurons)
        with open(esFileName, "w") as esf:
            esf.write("objref c, g, y, b, sl, xvec, es\n")
            esf.write("c\t\t= new Matrix(" + str(nES) + ", "+ str(nES) + ", "+"2)    // sparse (unallocated) zero matrix (efficient)\n")
            esf.write("g\t\t= new Matrix(" + str(nES) + ", "+ str(nES) + ")\n")
            esf.write("y\t\t= new Vector(" + str(nES) + ")\n")
            esf.write("b\t\t= new Vector(" + str(nES) + ")\n")
            esf.write("sl\t\t= new SectionList()    // list of cells; order corresponds to y\n")
            esf.write("xvec\t= new Vector(" + str(nES) + ", 0.5)    // locations of the synaptic connections\n\n")

            esf.write("// add each cell to the SectionList\n")
            for nrn in coupledNeurons:
                esf.write(nrn + " sl.append()\n")

            i = 0
            esf.write("\n// create indices for clarity\n")
            for nrn in coupledNeurons:
                esf.write(nrn + "_\t\t = "+str(i)+"\n")
                i = i+1

            for es in esList:

                # convert uS to S
                g1 = float(es.g1) * 1.0e-6
                g2 = float(es.g2) * 1.0e-6

                esf.write("\n//electrical coupling between "+ es.preSyn + " and " + es.postSyn +"\n")
                # G1
                st1 = "g.x["+es.postSyn+"_]["+es.postSyn+"_]"
                st2 = "g.x["+es.postSyn+"_]["+es.preSyn+"_]"
                esf.write("// "+es.postSyn+" receives current I = "+str(g1)+"*("+es.postSyn+".v - "+es.preSyn+".v)\n")
                esf.write(st1.ljust(2*lj) + " += "+str(g1)+"\t//(S/cm2)\n")
                esf.write(st2.ljust(2*lj) + " += "+str(-1.0*g1)+"\t//(S/cm2)\n\n")
                
                # G2
                st1 = "g.x["+es.preSyn+"_]["+es.preSyn+"_]"
                st2 = "g.x["+es.preSyn+"_]["+es.postSyn+"_]"
                esf.write("// "+es.preSyn+" receives current I = "+str(g2)+"*("+es.preSyn+".v - "+es.postSyn+".v)\n")
                esf.write(st1.ljust(2*lj) + " += "+str(g2)+"\t//(S/cm2)\n")
                esf.write(st2.ljust(2*lj) + " += "+str(-1.0*g2)+"\t//(S/cm2)\n\n")

            esf.write("\n// create the electrical synapses\n")
            esf.write("es = new LinearMechanism(c, g, y, b, sl, xvec)\n")
        return



    
    def writeTreatments(self, sSim):
        lj = self.lJust1
        trtList = sSim.network.chemSyns

        self.treatmentFile = "treatments.hoc"
        trtFileName = os.path.join(self.nrnDirPath,self.nrnDirName,self.treatmentFile)

        print "TRTFilename: ", trtFileName
        with open(trtFileName, "w") as tf:

            tf.write("// create stim objects\n")
            
            iClamps = sSim.treatemts.currentInjList
            nIC = len(iClamps)
            if nIC == 0:
                return

            tf.write("objref stim["+str(nIC)+ "]\n\n")

            for i in range(len(iClamps)):
                ic = iClamps[i]
                stimID = "stim["+str(i)+"]"
                tf.write((ic.neuronName+" "+stimID).ljust(lj) + "= new IClamp(0.5)\n")

                # convert seconds to miliseconds
                st = float(ic.start)*1000.0
                stop = float(ic.stop)*1000.0
                # duration of the IClamp
                dur = stop - st

                tf.write(util.formatedObjectVar(stimID, "del") + "= "+ str(st).ljust(lj)+"// (ms)\n")

                tf.write(util.formatedObjectVar(stimID, "dur") + "= "+ str(dur).ljust(lj) + "// (ms)\n")
                # in SNNAP magnitude of current inject is in nA 
                mag = float(ic.magnitude)
                tf.write(util.formatedObjectVar(stimID, "amp") + "= "+ str(mag).ljust(lj) + "// (nA)\n\n")

        return

        
    def writeChemSyns(self, sSim):

        lj = self.lJust1
        csList = sSim.network.chemSyns
        neurons = sSim.network.neurons
        i = 0
        for cs in csList:
            csf_local = "cs_"+cs.preSyn+"_to_" + cs.postSyn + "_" + cs.synType +".hoc"
            csFileName = os.path.join(self.nrnDirPath,self.nrnDirName,csf_local)

            with open(csFileName, "w") as csf:

                # append file name to the chemical synapse filelist
                self.chemSynFiles.append(csf_local)

                AtType = cs.ATType
                XtType = cs.XtType
                csf.write("// presyn: "+ cs.preSyn+ " postSyn: " + cs.postSyn+"\n")
                csf.write("//cs_ fATType:"+ cs.fATType+ " ATType:" + AtType +" XtType:"+ XtType+"\n\n")
                
                csf.write("threshold".ljust(lj)+ "= "+neurons[cs.preSyn].treshold.ljust(lj)+ "// (mV)\n")
                csf.write("delay".ljust(lj)+"= "+ "0.0".ljust(lj)+ "// (ms)\n")
                csf.write("weight".ljust(lj)+ "= "+"1".ljust(lj)+ "\n\n")

                #csf.write(("objref cs_"+str(i)).ljust()+"\n")

                csObjName = "cs_"+str(i)
                csf.write("objref "+ csObjName +"\n")

                if AtType == '1' or AtType == '2':
                    csf.write(cs.postSyn+" "+ csObjName +" = new snnap_cs2_At12(0.5)\n\n")
                if AtType == '3' or AtType == '4':
                    if XtType == '1':
                        csf.write(cs.postSyn+" "+ csObjName +" = new snnap_cs2_At34_Xt1(0.5)\n\n")
                    elif XtType == '3':
                        csf.write(cs.postSyn+" "+ csObjName +" = new snnap_cs2_At34_Xt3(0.5)\n\n")
                    else:
                        print "WARNING: Xt types other than \"1\" or \"3\" are not supported yet!!!"
                if AtType == '5':
                    if XtType == '1':
                        csf.write(cs.postSyn+" "+ csObjName +" = new snnap_cs2_At5_Xt_1(0.5)\n\n")
                    elif XtType == '3':
                        csf.write(cs.postSyn+" "+ csObjName +" = new snnap_cs2_At5_Xt_3(0.5)\n\n") 
                    else:
                        print "WARNING: Xt types other than \"1\" or \"3\" are not supported yet!!!"
                    
                csf.write(util.formatedObjectVar(csObjName, "e")+"= "+ cs.E.ljust(lj) + "// (mV)\n")

                # in SNNAP synaptic conductance is in uS
                g = float(cs.g)
                csf.write(util.formatedObjectVar(csObjName, "g")+"= "+ str(g).ljust(lj) + "// (uS)\n")

                # convert spike duration to ms
                spDur = float(neurons[cs.preSyn].spikeDur) *1000
                csf.write(util.formatedObjectVar(csObjName, "dur")+"= "+ str(spDur).ljust(lj) + "// (ms)\n\n")


                if cs.fATType in ['3', '5', '6']:
                    csf.write(util.formatedObjectVar(csObjName, "fAt_a")+"= "+ cs.fAT_a + "\n")
                if cs.fATType in ['3', '4', '5']:
                    csf.write(util.formatedObjectVar(csObjName, "fAt_b")+"= "+ cs.fAT_b + "\n")
                    
                csf.write(util.formatedObjectVar(csObjName, "Ics_type")+"= "+ cs.iCSType + "\n")
                csf.write(util.formatedObjectVar(csObjName, "fAt_type")+"= "+ cs.fATType + "\n")
                csf.write(util.formatedObjectVar(csObjName, "At_type")+"= "+ cs.ATType + "\n")

                if AtType in ['3', '4', '5']:
                    csf.write(util.formatedObjectVar(csObjName, "Xt_type")+"= "+ cs.XtType + "\n\n")

                if cs.ATType in ['1', '3', '4']:
                    # convert seconds to milliseconds
                    At_u1 = float(cs.At_u1) *1000.0
                    csf.write(util.formatedObjectVar(csObjName, "taucs1")+"= "+ str(At_u1).ljust(lj) + "// (ms)\n")
                    if cs.ATType in ['2', '4']:
                        # convert seconds to milliseconds
                        At_u2 = float(cs.At_u2) *1000.0
                        csf.write(util.formatedObjectVar(csObjName, "taucs2")+"= "+ str(At_u2).ljust(lj) + "// (ms)\n")

                if cs.XtType == "3" or cs.XtType == "4":
                    # convert seconds to milliseconds
                    PSM_ud = float(cs.PSM_ud) *1000.0
                    PSM_ur = float(cs.PSM_ur) *1000.0
                    csf.write(util.formatedObjectVar(csObjName, "tauXt1")+"= "+ str(PSM_ud).ljust(lj) + "// (ms)\n")
                    csf.write(util.formatedObjectVar(csObjName, "tauXt2")+"= "+ str(PSM_ur).ljust(lj) + "// (ms)\n")

                # setup netCon object
                csncObjName = "cs_nc"+str(i)
                csf.write("\nobjref "+ csncObjName +"\n")
                csf.write(cs.preSyn+" "+ csncObjName +" = new NetCon(&v(0.5), "+ csObjName+ ", threshold, delay, weight)\n\n")
            i = i+1
        return
    


    def writeMainSimFile(self, sSim):

        lj = self.lJust1
        
        mainFileName = os.path.join(self.nrnDirPath,self.nrnDirName,"sim_"+self.simName+".hoc")
        print "Main fileName: ", mainFileName
        
        with open(mainFileName, "w") as mf:

            mf.write("// load gui and standard run library\n")
            mf.write("load_file(\"nrngui.hoc\")\n\n")

            mf.write("// create neurons\n")
            for nfile in self .neutonFiles:
                mf.write("load_file(\"" +nfile+ "\")\n")
            mf.write("\n")

            mf.write("// create electrical and chemical synapses\n")
            for csfile in self.chemSynFiles:
                mf.write("load_file(\"" +csfile+ "\")\n")

            if self.ElecCouplingFile != "":
                mf.write("load_file(\"" + self.ElecCouplingFile + "\")\n")
            mf.write("\n")
            

            mf.write("// create stim objects\n")
            mf.write("load_file(\"" + self.treatmentFile + "\")\n\n")

            mf.write("// initialize simulation\n")
            mf.write("v_init = "+"-60.0".ljust(lj)+"// (mV)\n")

            # convert to miliseconds
            tstop = float(sSim.parameters["TIMING"]["tStop"]) * 1000.0
            dt = float(sSim.parameters["TIMING"]["h"]) * 1000.0
            mf.write("dt = " + str(dt).ljust(lj)+"// (ms)\n")
            mf.write("tstop = " + str(tstop).ljust(lj)+"// (ms)\n\n")

            mf.write("//cvode.active(1)      // enable variable time steps\n")
            mf.write("finitialize()        // initialize state variables (INITIAL blocks)\n")
            mf.write("fcurrent()           // initialize all currents    (BREAKPOINT blocks)\n\n")


            mf.write("load_file(\"create_plot.hoc\")\n\n")
            # mf.write("// run()\n\n")

            # as of NEURON version 7.6.5, run() initialize Vm of every sell to v_init before time integration
            mf.write("// alternative run() function which allow cells to be initialize to distict inital Vm.\n")
            mf.write("proc alt_run() {\n")
            mf.write("\trunning_ = 1\n")
            mf.write("\t// initialization\n")
            mf.write("\tcvode_simgraph()\n")
            mf.write("\trealtime = 0\n")
            mf.write("\tsetdt()\n")
            mf.write("\tfinitialize()\n")
            mf.write("\tinitPlot()\n")
            mf.write("\t// advance\n")
            mf.write("\tcontinuerun(tstop)\n")
            mf.write("}\n\n")

            mf.write("alt_run()\n\n")

            mf.write("//load_file(\"fwrite.hoc\")\n\n")
            print "\nSNNAP model was sucessfully converted to NEURON!"
            
        return


    def createModelDir(self, sSim):
        """
        create a directrory called NRNModel_<SNNAP-simulation-name>
        """
        
        self.nrnDirPath = sSim.simFilePath
        self.nrnDirName = "NRNModel_" + self.simName

        if not os.path.isdir(self.nrnDirPath + os.sep + self.nrnDirName):
            os.mkdir(self.nrnDirPath + os.sep + self.nrnDirName)
            print "Neuron model is located in ", self.nrnDirPath + os.sep + self.nrnDirName



    
    def writeNeurons(self, sSim):
        """
        write neuron data into files
        """
        
        lj = self.lJust1
        

        for nName in sSim.network.neurons.keys():
            nf_local = "create_"+nName+".hoc"
            nFileName = os.path.join(self.nrnDirPath,self.nrnDirName,nf_local)
            nrn = sSim.network.neurons[nName]

            with open(nFileName, "w") as nf:

                # append file name to the neuron filelist
                self.neutonFiles.append(nf_local)
                
                nf.write("create "+ nName+"\n")
                nf.write(nName + " {\n")
                nf.write("\tnseg = 1\t\t// single compartment\n")
                nf.write("\tdiam = 1\t\t// (um)\n")
                nf.write("\tL = 3.1831e7\t\t// (um)\n")
                nf.write("\t// total area = pi*diam*L = 1e8 um2 = 1 cm2\n\n")

                # write membrane capacitance
                if nrn.memAreaType == "0" or nrn.memAreaType == "":
                    # membrane capacitance is in uF
                    cm = float(nrn.cm)
                    nf.write("\tcm = "+ str(cm).ljust(lj)+"// (uF/cm2)\n")
                else:
                    print "WARNING: memAreas other than \"0\" are not supported yet!!!"

                # insert leak current
                vdgs = nrn.vdgs

                if self.useNrnPas:
                    for vdgName in vdgs.keys():
                        ivdType = vdgs[vdgName].ivdType
                        if ivdType == '5':
                            nf.write("\tinsert pas\n")
                            nf.write("\te_pas = "+vdgs[vdgName].E.ljust(lj)+ "// (mV)\n")
                            g = float(vdgs[vdgName].g)
                            # in SNNAP cm is given in uS,
                            # convert conductance from uS to S if not using mem_area
                            if nrn.memAreaType == '0' or nrn.memAreaType == "":
                                g = float(vdgs[vdgName].g) * 1.0e-6
                                nf.write("\tg_pas = "+str(g).ljust(lj)+ "// (S/cm2)\n")
                        
                nf.write("}\n\n")

                # write inital Vm
                nf.write(nName+".v(0.5) = " + str(nrn.vmInit).ljust(lj) +" // (mV)\n\n")

                # insert VDGs
                for vdgName in vdgs.keys():
                    ivdType = vdgs[vdgName].ivdType
                    aType = vdgs[vdgName].AType
                    bType = vdgs[vdgName].BType
                    mType = vdgs[vdgName].mType
                    hType = vdgs[vdgName].hType

                    if nrn.memAreaType == '0'or nrn.memAreaType == "":
                        # in SNNAP, if not using memArea conductance is given in uS
                        try:
                            g = float(vdgs[vdgName].g)
                        except:
                            print "WARNING!: could not convert "+vdgName+ " conductance of neuron " + nName
                            print "Exited unexpectedly!"
                            sys.exit(-1)

                    if not self.useNrnPas:
                        if ivdType == '5':
                            nf.write("// passive current\n")
                        
                            vdgObjName = nName+"_"+vdgName
                            nf.write("objref "+vdgObjName+ "\n")
                            nf.write(nName+" "+vdgObjName+ " = new snnap_ionic_pas_ivd5(0.5)\n")
                        
                            nf.write(util.formatedObjectVar(vdgObjName, "e")+ "= "+(vdgs[vdgName].E).ljust(lj) + "// (mV)\n")
                            nf.write(util.formatedObjectVar(vdgObjName, "gmax") + "= " + str(g).ljust(lj) + "// (uS)\n\n\n")
                            continue

                        
                    # create object reference for this vdg
                    vdgObjName = nName+"_"+vdgName
                    nf.write("objref "+vdgObjName+ "\n")

                    if ivdType == '1' or ivdType == '3':
                        nf.write("//_A"+aType+"_B"+bType+"\n")
                        nf.write(nName+" "+vdgObjName+ " = new snnap_ionic_tc_ivd"+ivdType+"_A"+aType+"(0.5)\n")
                        
                        nf.write(util.formatedObjectVar(vdgObjName, "e")+ "= "+(vdgs[vdgName].E).ljust(lj) + "// (mV)\n")
                        nf.write(util.formatedObjectVar(vdgObjName, "gmax") + "= " + str(g).ljust(lj) + "// (uS)\n")
                        nf.write(util.formatedObjectVar(vdgObjName, "p")+ "= "+vdgs[vdgName].P + "\n\n")

                        self.write_ActF_timeConstant(nf, vdgObjName, vdgs[vdgName])

                        if ivdType == '1':
                            self.write_InActF_timeConstant(nf,  vdgObjName, vdgs[vdgName])
                        
                    if ivdType == '2' or ivdType == '4':
                        nf.write("//_m"+mType+"_h"+hType+"\n")
                        
                        nf.write(nName+" "+vdgObjName+ " = new snnap_ionic_rc_ivd"+ivdType+"(0.5)\n")
                        
                        nf.write(util.formatedObjectVar(vdgObjName, "e")+ "= "+(vdgs[vdgName].E).ljust(lj) + "// (mV)\n")
                        nf.write(util.formatedObjectVar(vdgObjName, "gmax") + "= " + str(g).ljust(lj) + "// (uS)\n")
                        nf.write(util.formatedObjectVar(vdgObjName, "p")+ "= "+vdgs[vdgName].P + "\n\n")

                        self.write_ActF_rateConstant(nf,  vdgObjName, vdgs[vdgName])

                        if ivdType == '2':
                            self.write_InActF_rateConstant(nf,  vdgObjName, vdgs[vdgName])
                    nf.write("\n")



    def write_ActF_rateConstant(self, file, vdgObj, ivd):

        # in SNNAP time derivatives are also in seconds. to convert them to Neuron time derivatives
        # must be divided by 1000.0
        lj = self.lJust1
        afType = ivd.mType
        if afType == "2":
            file.write(util.formatedObjectVar(vdgObj, "m_L")+ "= 0.001\n")
        if afType == "3":
            #m_L = float(ivd.m_L) / 3000.0 * 3.23
            m_L = float(ivd.m_L) /1000.0
            file.write(util.formatedObjectVar(vdgObj, "m_L")+ "= "+ str(m_L)+"\n")
            #file.write(util.formatedObjectVar(vdgObj, "m_L")+ "= "+ ivd.m_L+ "\n")
        amType = ivd.amType
        file.write(util.formatedObjectVar(vdgObj, "am_type")+ "= "+ ivd.amType+ "\n")
        file.write(util.formatedObjectVar(vdgObj, "am_A")+ "= "+ ivd.am_A+ "\n")
        
        if amType != '1':
            file.write(util.formatedObjectVar(vdgObj, "am_B")+ "= "+ (ivd.am_B).ljust(lj)+ "// (mV)\n")

            if amType != '4' and amType != '8' and amType != '9':
                file.write(util.formatedObjectVar(vdgObj, "am_C")+ "= "+ (ivd.am_C).ljust(lj)+ "// (mV)\n")

                if amType != '5' and amType != '6' and amType != '7':

                    file.write(util.formatedObjectVar(vdgObj, "am_D")+ "= "+ (ivd.am_D).ljust(lj)+ "// (mV)\n")
            
        bmType = ivd.bmType
        file.write("\n")
        file.write(util.formatedObjectVar(vdgObj, "bm_type")+ "= "+ bmType+ "\n")
        file.write(util.formatedObjectVar(vdgObj, "bm_A")+ "= "+ ivd.bm_A+ "\n")
        
        if bmType != '1':
            file.write(util.formatedObjectVar(vdgObj, "bm_B")+ "= "+ (ivd.bm_B).ljust(lj)+ "// (mV)\n")

            if bmType != '4' and bmType != '8' and bmType != '9':
                file.write(util.formatedObjectVar(vdgObj, "bm_C")+ "= "+ (ivd.bm_C).ljust(lj)+ "// (mV)\n")
                
                if bmType != '5' and bmType != '6' and bmType != '7':
                    file.write(util.formatedObjectVar(vdgObj, "bm_D")+ "= "+ (ivd.bm_D).ljust(lj)+ "// (mV)\n")
                    
        file.write("\n")


    def write_InActF_rateConstant(self, file, vdgObj, ivd):

        lj = self.lJust1
        inactfType = ivd.hType
        if inactfType == "2":
            file.write(util.formatedObjectVar(vdgObj, "h_L")+ "= 0.001\n")
        if inactfType == "3":
            h_L = float(ivd.h_L) / 1000.0
            file.write(util.formatedObjectVar(vdgObj, "h_L")+ "= "+str(h_L)+"\n")
            #file.write(util.formatedObjectVar(vdgObj, "h_L")+ "= "+ ivd.h_L+ "\n")

        ahType = ivd.ahType
        file.write(util.formatedObjectVar(vdgObj, "ah_type")+ "= "+ ivd.ahType+ "\n")

        file.write(util.formatedObjectVar(vdgObj, "ah_A")+ "= "+ ivd.ah_A + "\n")
        if ahType != '1':
            file.write(util.formatedObjectVar(vdgObj, "ah_B")+ "= "+ (ivd.ah_B).ljust(lj)+ "// (mV)\n")

            if ahType != '4' and ahType != '8' and ahType != '9':
                file.write(util.formatedObjectVar(vdgObj, "ah_C")+ "= "+ (ivd.ah_C).ljust(lj)+ "// (mV)\n")

                if ahType != '5' and ahType != '6' and ahType != '7':
                    file.write(util.formatedObjectVar(vdgObj, "ah_D")+ "= "+ (ivd.ah_D).ljust(lj)+ "// (mV)\n")
            
        bhType = ivd.bhType
        file.write("\n")
        file.write(util.formatedObjectVar(vdgObj, "bh_type")+ "= "+ bhType+ "\n")
        file.write(util.formatedObjectVar(vdgObj, "bh_A")+ "= "+ ivd.bh_A+ "\n")

        if bhType != '1':
            file.write(util.formatedObjectVar(vdgObj, "bh_B")+ "= "+ (ivd.bh_B).ljust(lj)+ "// (mV)\n")
 
            if bhType != '4' and bhType != '8' and bhType != '9':
                file.write(util.formatedObjectVar(vdgObj, "bh_C")+ "= "+ (ivd.bh_C).ljust(lj)+ "// (mV)\n")
 
                if bhType != '5' and bhType != '6' and bhType != '7':
                    file.write(util.formatedObjectVar(vdgObj, "bh_D")+ "= "+ (ivd.bh_D).ljust(lj)+ "// (mV)\n")

        file.write("\n")


    def write_ActF_timeConstant(self, file, vdgObj, ivd):

        lj = self.lJust1
        afType = ivd.AType
        if afType == "2":
            #file.write(util.formatedObjectVar(vdgObj, "A_IV")+ "= "+ ivd.A_IV+ "\n")
            
            tAType = ivd.tAType
            file.write(util.formatedObjectVar(vdgObj, "tA_type")+ "= "+ tAType+ "\n")

            # convert seconds to ms
            tA_tx = float(ivd.tA_tx) * 1000.0
            file.write(util.formatedObjectVar(vdgObj, "tA_tx") + "= "+ str(tA_tx).ljust(lj)+ "// (ms)\n")
            
            if tAType in ['2', '3', '6']:
                file.write(util.formatedObjectVar(vdgObj, "tA_h1") + "= "+ (ivd.tA_h1).ljust(lj)+ "// (mV)\n")
                file.write(util.formatedObjectVar(vdgObj, "tA_s1") + "= "+ (ivd.tA_s1).ljust(lj)+ "// (mV)\n")
                if tAType != '6':
                    # convert seconds to ms
                    tA_tn = float(ivd.tA_tn) * 1000.0
                    file.write(util.formatedObjectVar(vdgObj, "tA_tn") + "= "+ str(tA_tn).ljust(lj)+ "// (ms)\n")
                    file.write(util.formatedObjectVar(vdgObj, "tA_p1") + "= "+ (ivd.tA_p1).ljust(lj)+ "\n\n")
                if tAType in ['3', '6']:
                    file.write(util.formatedObjectVar(vdgObj, "tA_h2") + "= "+ (ivd.tA_h2).ljust(lj)+ "// (mV)\n")
                    file.write(util.formatedObjectVar(vdgObj, "tA_s2") + "= "+ (ivd.tA_s2).ljust(lj)+ "// (mV)\n")
                    if tAType != '6':
                        file.write(util.formatedObjectVar(vdgObj, "tA_p2") + "= "+ (ivd.tA_p2).ljust(lj)+ "\n\n")
            elif tAType != '1':
                print "WARNING: Time constant forms other than 1, 2, 3 or 6 are not supported yet!!!"

        # write steady state
        ssAType = ivd.ssAType
        file.write(util.formatedObjectVar(vdgObj, "ssA_type") + "= "+ ssAType+ "\n")
        
        file.write(util.formatedObjectVar(vdgObj, "ssA_h") + "= "+ (ivd.ssA_h).ljust(lj)+ "// (mV)\n")
        file.write(util.formatedObjectVar(vdgObj, "ssA_s") + "= "+ (ivd.ssA_s).ljust(lj)+ "// (mV)\n")
        file.write(util.formatedObjectVar(vdgObj, "ssA_p") + "= "+ ivd.ssA_p+ "\n")
        if ssAType == '2':
            file.write(util.formatedObjectVar(vdgObj, "ssA_An") + "= "+ ivd.ssA_An+ "\n")

        file.write("\n")
        #file.write('%-40s %6s %10s %2s\n' % (filename, type, size, modified))

    def write_InActF_timeConstant(self, file, vdgObj, ivd):

        lj = self.lJust1
        inactfType = ivd.BType
        if inactfType == "2":
            #file.write(util.formatedObjectVar(vdgObj, "B_IV")+ "= "+ ivd.B_IV+ "\n")
            
            tBType = ivd.tBType
            file.write(util.formatedObjectVar(vdgObj, "tB_type")+ "= "+ tBType+ "\n")

            # convert seconds to ms
            tB_tx = float(ivd.tB_tx) * 1000.0
            file.write(util.formatedObjectVar(vdgObj, "tB_tx")+ "= "+ str(tB_tx).ljust(lj)+ "// (ms)\n")

            if tBType in ['2', '3', '6']:
                file.write(util.formatedObjectVar(vdgObj, "tB_h1")+ "= "+ (ivd.tB_h1).ljust(lj)+ "// (mV)\n")
                file.write(util.formatedObjectVar(vdgObj, "tB_s1")+ "= "+ (ivd.tB_s1).ljust(lj)+ "// (mV)\n")
                if tBType != '6':
                    # convert seconds to ms
                    tB_tn = float(ivd.tB_tn) * 1000.0
                    file.write(util.formatedObjectVar(vdgObj, "tB_tn")+ "= "+ str(tB_tn).ljust(lj)+ "// (ms)\n")
                    file.write(util.formatedObjectVar(vdgObj, "tB_p1")+ "= "+ ivd.tB_p1+ "\n\n")
                if tBType in ['3', '6']:
                    file.write(util.formatedObjectVar(vdgObj, "tB_h2")+ "= "+ (ivd.tB_h2).ljust(lj)+ "// (mV)\n")
                    file.write(util.formatedObjectVar(vdgObj, "tB_s2")+ "= "+ (ivd.tB_s2).ljust(lj)+ "// (mV)\n")
                    if tBType != '6':
                        file.write(util.formatedObjectVar(vdgObj, "tB_p2")+ "= "+ ivd.tB_p2+ "\n\n")
            elif tBType != '1':
                print "WARNING: Time constant forms other than 1, 2, 3 or 6 are not supported yet!!!"

        # write steady state
        ssBType = ivd.ssBType
        file.write(util.formatedObjectVar(vdgObj, "ssB_type")+ "= "+ ssBType+ "\n")

        file.write(util.formatedObjectVar(vdgObj, "ssB_h")+ "= "+ (ivd.ssB_h).ljust(lj)+ "// (mV)\n")
        file.write(util.formatedObjectVar(vdgObj, "ssB_s")+ "= "+ (ivd.ssB_s).ljust(lj)+ "// (mV)\n")
        file.write(util.formatedObjectVar(vdgObj, "ssB_p")+ "= "+ ivd.ssB_p+ "\n")

        if ssBType == '2':
            file.write(util.formatedObjectVar(vdgObj, "ssB_Bn")+ "= "+ ivd.ssB_Bn+ "\n")


    def printNeurons(self, sSim):
        """
        print neuron data into stdout
        """
        print "\n::: Neuron data :::"
        for nName in sSim.network.neurons.keys():
            print "Neuron Name: ", nName
            nrn = sSim.network.neurons[nName]
            print "treshold: ", nrn.treshold
            print "spikeDur: ", nrn.spikeDur
            print "vmInit: ", nrn.vmInit
            print "cm: ", nrn.cm
            print "memAreaType: ", nrn.memAreaType

            for vdgName  in nrn.vdgs.keys():
                vdg = nrn.vdgs[vdgName]
                
                print "---"+vdgName
                self.printIvd(vdg)

            print ""

    def print_ActF_rateConstant(self, ivd):
        afType = ivd.mType
        if afType == "2" or afType == "3":
            print "m_IV: ", ivd.m_IV            
        if afType == "3":
            print "m_L: ", ivd.m_L
        amType = ivd.amType
        print "amType: ", ivd.amType
        print "am_A: ", ivd.am_A
        if amType != '1':
            print "am_B: ", ivd.am_B
        if amType != '4' and amType != '8' and amType != '9':
            print "am_C: ", ivd.am_C
        if amType != '5' and amType != '6' and amType != '7':
            print "am_D: ", ivd.am_D
            
        bmType = ivd.bmType
        print "bmType: ", ivd.bmType
        print "bm_A: ", ivd.bm_A
        if bmType != '1':
            print "bm_B: ", ivd.bm_B
            if bmType != '4' and bmType != '8' and bmType != '9':
                print "bm_C: ", ivd.bm_C
                if bmType != '5' and bmType != '6' and bmType != '7':
                    print "bm_D: ", ivd.bm_D


    def print_InActF_rateConstant(self, ivd):
        inactfType = ivd.hType
        if inactfType == "2" or inactfType == "3":
            print "h_IV: ", ivd.h_IV            
        if inactfType == "3":
            print "h_L: ", ivd.h_L
        ahType = ivd.ahType
        print "ahType: ", ahType
        print "ah_A: ", ivd.ah_A
        if ahType != '1':
            print "ah_B: ", ivd.ah_B
        if ahType != '4' and ahType != '8' and ahType != '9':
            print "ah_C: ", ivd.ah_C
        if ahType != '5' and ahType != '6' and ahType != '7':
            print "ah_D: ", ivd.ah_D
            
        bhType = ivd.bhType
        print "bhType: ", ivd.bhType
        print "bh_A: ", ivd.bh_A
        if bhType != '1':
            print "bh_B: ", ivd.bh_B
            if bhType != '4' and bhType != '8' and bhType != '9':
                print "bh_C: ", ivd.bh_C
                if bhType != '5' and bhType != '6' and bhType != '7':
                    print "bh_D: ", ivd.bh_D            

    def print_ActF_timeConstant(self, ivd):
        afType = ivd.AType
        if afType == "2":
            print "A_IV: ", ivd.A_IV
            
            tAType = ivd.tAType
            print "+++tAType: ", tAType
            print "tA_tx: ", ivd.tA_tx
            if tAType == '2':
                print "tA_tn: ", ivd.tA_tn
                print "tA_h1: ", ivd.tA_h1
                print "tA_s1: ", ivd.tA_s1
                print "tA_p1: ", ivd.tA_p1

            elif tAType != '1':
                print "WARNING: Time constant forms other than 1st or 2nd forms are not supported yet!!!"
            
        ssAType = ivd.ssAType
        print "ssAType: ", ssAType
        
        print "ssA_h: ", ivd.ssA_h
        print "ssA_s: ", ivd.ssA_s
        print "ssA_p: ", ivd.ssA_p            
        if ssAType == 2:
            print "ssA_IV: ", ivd.ssA_An


    def print_InActF_timeConstant(self, ivd):
        inactfType = ivd.BType
        if inactfType == "2":
            print "B_IV: ", ivd.B_IV
            
            tBType = ivd.tBType
            print "+++tBType: ", tBType
            print "tB_tx: ", ivd.tB_tx
            if tBType == '2':
                print "tB_tn: ", ivd.tB_tn
                print "tB_h1: ", ivd.tB_h1
                print "tB_s1: ", ivd.tB_s1
                print "tB_p1: ", ivd.tB_p1

            elif tBType != '1':
                print "WARNING: Time constant forms other than 1st or 2nd forms are not supported yet!!!"
            
        ssBType = ivd.ssBType
        print "ssBType: ", ssBType
        
        print "ssB_h: ", ivd.ssB_h
        print "ssB_s: ", ivd.ssB_s
        print "ssB_p: ", ivd.ssB_p            
        if ssBType == 2:
            print "ssB_IV: ", ivd.ssB_Bn
            
            
    def printIvd(self, ivd):
        """
        """
        ivdType = ivd.ivdType
        print "ivd type: ", ivdType
        if ivdType == "1" or ivdType == "3":
            print "------------------AType: ", ivd.AType
            print "P: ", ivd.P
            self.print_ActF_timeConstant(ivd)

        if ivdType == "2" or ivdType == "4":
            print "mType: ", ivd.mType
            print "P: ", ivd.P
            self.print_ActF_rateConstant(ivd)

        if ivdType == "1":
            print "------------------BType: ", ivd.BType
            self.print_InActF_timeConstant(ivd)

        if ivdType == "2":
            print "hType: ", ivd.hType
            self.print_InActF_rateConstant(ivd)


        print "E: ", ivd.E
        print "g: ", ivd.g


