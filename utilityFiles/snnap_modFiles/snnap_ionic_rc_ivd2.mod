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
   : mType = 2|3, hType = 2|3
      snnap_ionic_rc_ivd2

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
      m,       h,

	  m_L, h_L,

	  am_A, am_B, am_C,	am_D,
	  bm_A, bm_B, bm_C, bm_D,

	  ah_A, ah_B, ah_C, ah_D,
	  bh_A, bh_B, bh_C, bh_D,

    : model control variables
	am_type,
    bm_type,
    ah_type,
    bh_type
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
	  h_L
	  
	  am_A
	  am_B       (mV)
	  am_C       (mV)
	  am_D       (mV)

	  bm_A
	  bm_B       (mV)
	  bm_C       (mV)
	  bm_D       (mV)

	  ah_A
	  ah_B       (mV)
	  ah_C       (mV)
	  ah_D       (mV)

	  bh_A
	  bh_B       (mV)
	  bh_C       (mV)
	  bh_D       (mV)

	  am_type
      bm_type
      ah_type
      bh_type
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
      h                 : inactivation
}

BREAKPOINT {
   : main computational block
   : set with fcurrent() and re-evaluated throughout the simulation
   : cnexp is used because the equations are of the form y' = f(v,y), are linear
   :    in y, and involve no other states
   : cnexp has second-order accuracy and is computationally efficient
   : equation A2 '

      SOLVE states METHOD cnexp

      g = gmax * m ^ p * h
      i = g * (v - e)
}

INITIAL {
   : initial conditions
   : set with finitialize()

      m = am(v) / (am(v) + bm(v))
      h = ah(v) / (ah(v) + bh(v))
      : A = ssA(v)
      : B = ssB(v)
}

DERIVATIVE states {
   : differential equations for gating variables
   : equations A3a, A3b

      m' = m_L*(am(v)*(1 - m) - bm(v)*m)
      h' = h_L*(ah(v)*(1 - h) - bh(v)*h)
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

FUNCTION ah(v (mV)) () {
   : 

    if (ah_type == 1) {
      ah = ah_A
    }
    if (ah_type == 2) {
      ah = ah_A *(v + ah_B)/ (1 + exp((ah_C - v)/ah_D))
    }
    if (ah_type == 3) {
      ah = ah_A *(v + ah_B)/ (1 - exp((ah_C - v)/ah_D))
    }
    if (ah_type == 4) {
      ah = 1 + exp((ah_A - v)/ah_B)
    }
    if (ah_type == 5) {
      ah = ah_A * exp((ah_B - v)/ah_C)
    }
    if (ah_type == 6) {
      ah = ah_A / (1 + exp((ah_B - v)/ah_C))
    }
    if (ah_type == 7) {
      ah = ah_A / (1 - exp((ah_B - v)/ah_C))
    }
    if (ah_type == 8) {
      ah = 1 / (1 + exp((ah_A - v)/ah_B))
    }
    if (ah_type == 9) {
      ah = 1 / (1 - exp((ah_A - v)/ah_B))
    }
}


FUNCTION bh(v (mV)) () {
   : 

    if (bh_type == 1) {
      bh = bh_A
    }
    if (bh_type == 2) {
      bh = bh_A *(v + bh_B)/ (1 + exp((bh_C - v)/bh_D))
    }
    if (bh_type == 3) {
      bh = bh_A *(v + bh_B)/ (1 - exp((bh_C - v)/bh_D))
    }
    if (bh_type == 4) {
      bh = 1 + exp((bh_A - v)/bh_B)
    }
    if (bh_type == 5) {
      bh = bh_A * exp((bh_B - v)/bh_C)
    }
    if (bh_type == 6) {
      bh = bh_A / (1 + exp((bh_B - v)/bh_C))
    }
    if (bh_type == 7) {
      bh = bh_A / (1 - exp((bh_B - v)/bh_C))
    }
    if (bh_type == 8) {
      bh = 1 / (1 + exp((bh_A - v)/bh_B))
    }
    if (bh_type == 9) {
      bh = 1 / (1 - exp((bh_A - v)/bh_B))
    }
}

