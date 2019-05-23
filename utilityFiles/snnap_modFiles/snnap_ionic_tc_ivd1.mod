COMMENT
 * snnap_ionic.mod
 *
 * NEURON mechanism for implementing a SNNAP-style ionic current
 *
 * Copyright (c) 2012, Jeffrey P Gill and Shang-Shen Yu
 *
 * This file is part of NEURON Reconstruction of Susswein et al. 2002.
 * 
 * NEURON Reconstruction of Susswein et al. 2002 is free software: you can
 * redistribute it and/or modify it under the terms of the GNU General Public
 * License as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 * 
 * NEURON Reconstruction of Susswein et al. 2002 is distributed in the hope
 * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with NEURON Reconstruction of Susswein et al. 2002.  If not, see
 * <http://www.gnu.org/licenses/>.
ENDCOMMENT


NEURON {
   : specify the interface to NEURON

   POINT_PROCESS
   : Activation function (time constant method)
   : AType = 2, BType = 2
      snnap_ionic_tc_ivd1

   NONSPECIFIC_CURRENT
   : currents not associated with varying ion concentrations

      i

   RANGE
   : non-global variables and constants
   : specific to each instance of the mechanism

      i,
      e,
      g,
      gmax,
      p,

	: activation fucntion (A), and inactivation function (B)
      A,       B,

	: parameters for calculating steady state
	  ssA_An, ssA_h, ssA_s, ssA_p,
	  ssB_Bn, ssB_h, ssB_s, ssB_p,
	  
	: parameters for calculating time constant 
      tA_tn, tA_tx,
      tA_h1, tA_h2,
      tA_s1, tA_s2,
      tA_p1, tA_p2,

      tB_tn, tB_tx,
      tB_h1, tB_h2,
      tB_s1, tB_s2,
      tB_p1, tB_p2,


    : model control variables
	ssA_type,
    ssB_type,
    tA_type,
    tB_type,

    : for debugging
    debug_var
}

UNITS {
      (mV) = (millivolt)
      (uS) = (microsiemens)
      (nA) = (nanoamp)
}

PARAMETER {
   : declaration of fixed-value parameters

      e           (mV)
      gmax        (uS)
      p

      ssA_h       (mV)
      ssA_s       (mV)
      ssA_p
	  ssA_An
	  
      ssB_h       (mV)
      ssB_s       (mV)
      ssB_p
      ssB_Bn

      tA_tn     (ms)
      tA_tx     (ms)
      tA_h1     (mV)
      tA_s1     (mV)
      tA_p1
      tA_h2     (mV)
      tA_s2     (mV)
      tA_p2

      tB_tn     (ms)
      tB_tx     (ms)
      tB_h1     (mV)
      tB_s1     (mV)
      tB_p1
      tB_h2     (mV)
      tB_s2     (mV)
      tB_p2


	  ssA_type
      ssB_type
      tA_type
      tB_type
}

ASSIGNED {
   : declaration of non-state variables

      v           (mV)
      i           (nA)
      g           (uS)

      : for debugging
      debug_var
}

STATE {
   : declaration of state variables

      A                 : activation
      B                 : inactivation
}

BREAKPOINT {
   : main computational block
   : set with fcurrent() and re-evaluated throughout the simulation
   : cnexp is used because the equations are of the form y' = f(v,y), are linear
   :    in y, and involve no other states
   : cnexp has second-order accuracy and is computationally efficient
   : equation A2 '

      SOLVE states METHOD cnexp

      g = gmax * A ^ p * B
      debug_var = A
      i = g * (v - e)
}

INITIAL {
   : initial conditions
   : set with finitialize()

      A = ssA(v)
      B = ssB(v)
}

DERIVATIVE states {
   : differential equations for gating variables
   : equations A3a, A3b

      A' = (ssA(v) - A) / tA(v)
      B' = (ssB(v) - B) / tB(v)
}

FUNCTION ssA(v (mV)) () {
   : steady state value of activation variable
   : equation A4a

    if (ssA_type == 1) {
      ssA = 1 / (1 + exp((ssA_h - v)/ssA_s))^ssA_p
    }
    if (ssA_type == 2) {
      ssA = (1 - ssA_An)/ (1 + exp((ssA_h - v)/ssA_s))^ssA_p + ssA_An
    }
}

FUNCTION ssB(v (mV)) () {
   : steady state value of inactivation variable
   : equation A4b

    if (ssB_type == 1) {
      ssB = 1 / (1 + exp((v - ssB_h)/ssB_s))^ssB_p
    }
    if (ssB_type == 2) {
      ssB = (1 - ssB_Bn)/ (1 + exp((v - ssB_h)/ssB_s))^ssB_p + ssB_Bn
    }
}

FUNCTION tA(v (mV)) (ms) {
   : time constant of activation variable (double exponential form)
   : equation A4c (see also Ziv et. al 1994, table 1)

    if (tA_type == 1) {
        tA = tA_tx
    }
    if (tA_type == 2) {
        tA = tA_tn + (tA_tx - tA_tn) / (1 + exp((v-tA_h1)/tA_s1))^tA_p1
    }
    if (tA_type == 3) {
        tA = tA_tn + (tA_tx - tA_tn) / ((1 + exp((v-tA_h1)/tA_s1))^tA_p1) /(1 + exp((v-tA_h2)/tA_s2))^tA_p2
    }
    if (tA_type == 6) {
        tA = tA_tx / (exp((v-tA_h1)/tA_s1) + exp(-(v-tA_h2)/tA_s2))
    }
    
:      tauA = tauAmin + (tauAmax - tauAmin) / (1 + exp((v - htauA)/stauA))^ptauA / (1 + exp((v - htauA2)/stauA2))^ptauA2
}

FUNCTION tB(v (mV)) (ms) {
   : time constant of inactivation variable
   : equation A4d (see also Ziv et. al 1994, table 1)
   :  tauB = tauBmin + (tauBmax - tauBmin) / (1 + exp((v - htauB)/stauB))^ptauB

    if (tB_type == 1) {
        tB = tB_tx
    }
    if (tB_type == 2) {
        tB = tB_tn + (tB_tx - tB_tn) / (1 + exp((v-tB_h1)/tB_s1))^tB_p1
    }
    if (tB_type == 3) {
        tB = tB_tn + (tB_tx - tB_tn) / ((1 + exp((v-tB_h1)/tB_s1))^tB_p1) / (1 + exp((v-tB_h2)/tB_s2))^tB_p2
    }
    if (tB_type == 6) {
        tB = tB_tx / (exp((v-tB_h1)/tB_s1) + exp(-(v-tB_h2)/tB_s2))
    }
}
