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
   : Activation function (rate constant method)
   : mType = 2|3
      snnap_ionic_rc_ivd4

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

	: activation fucntion (A)
      m,

	  m_L,

	  am_A, am_B, am_C,	am_D,
	  bm_A, bm_B, bm_C, bm_D,


    : model control variables
	am_type,
    bm_type
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

	  m_L
	  
	  am_A
	  am_B       (mV)
	  am_C       (mV)
	  am_D       (mV)

	  bm_A
	  bm_B       (mV)
	  bm_C       (mV)
	  bm_D       (mV)

	  am_type
      bm_type
}

ASSIGNED {
   : declaration of non-state variables

      v           (mV)
      i           (nA)
      g           (uS)
}

STATE {
   : declaration of state variables

      m                 : activation
}

BREAKPOINT {
   : main computational block
   : set with fcurrent() and re-evaluated throughout the simulation
   : cnexp is used because the equations are of the form y' = f(v,y), are linear
   :    in y, and involve no other states
   : cnexp has second-order accuracy and is computationally efficient
   : equation A2 '

      SOLVE states METHOD cnexp

      g = gmax * m ^ p
      i = g * (v - e)
}

INITIAL {
   : initial conditions
   : set with finitialize()

      m = am(v) / (am(v) + bm(v))
}

DERIVATIVE states {
   : differential equations for gating variables
   : equations A3a, A3b

      m' = m_L*(am(v)*(1 - m) - bm(v)*m)
}

FUNCTION am(v (mV)) () {
   : 

    if (am_type == 1) {
      am = am_A
    }
    if (am_type == 2) {
      am = am_A *(v + am_B)/ (1 + exp((am_C - v)/am_D))
    }
    if (am_type == 3) {
      am = am_A *(v + am_B)/ (1 - exp((am_C - v)/am_D))
    }
    if (am_type == 4) {
      am = 1 + exp((am_A - v)/am_B)
    }
    if (am_type == 5) {
      am = am_A * exp((am_B - v)/am_C)
    }
    if (am_type == 6) {
      am = am_A / (1 + exp((am_B - v)/am_C))
    }
    if (am_type == 7) {
      am = am_A / (1 - exp((am_B - v)/am_C))
    }
    if (am_type == 8) {
      am = 1 / (1 + exp((am_A - v)/am_B))
    }
    if (am_type == 9) {
      am = 1 / (1 - exp((am_A - v)/am_B))
    }
}

FUNCTION bm(v (mV)) () {
   : 

    if (bm_type == 1) {
      bm = bm_A
    }
    if (bm_type == 2) {
      bm = bm_A *(v + bm_B)/ (1 + exp((bm_C - v)/bm_D))
    }
    if (bm_type == 3) {
      bm = bm_A *(v + bm_B)/ (1 - exp((bm_C - v)/bm_D))
    }
    if (bm_type == 4) {
      bm = 1 + exp((bm_A - v)/bm_B)
    }
    if (bm_type == 5) {
      bm = bm_A * exp((bm_B - v)/bm_C)
    }
    if (bm_type == 6) {
      bm = bm_A / (1 + exp((bm_B - v)/bm_C))
    }
    if (bm_type == 7) {
      bm = bm_A / (1 - exp((bm_B - v)/bm_C))
    }
    if (bm_type == 8) {
      bm = 1 / (1 + exp((bm_A - v)/bm_B))
    }
    if (bm_type == 9) {
      bm = 1 / (1 - exp((bm_A - v)/bm_B))
    }
}


