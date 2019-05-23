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
   : AType = 5
      snnap_ionic_pas_ivd5

   NONSPECIFIC_CURRENT
   : currents not associated with varying ion concentrations

      i

   RANGE
   : non-global variables and constants
   : specific to each instance of the mechanism

      i,
      e,
      g,
      gmax
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
}

ASSIGNED {
   : declaration of non-state variables

      v           (mV)
      i           (nA)
      g           (uS)
}


BREAKPOINT {
   : main computational block
   : set with fcurrent() and re-evaluated throughout the simulation

      g = gmax
      i = g * (v - e)
}

INITIAL {
   : initial conditions
   : set with finitialize()

      g = gmax
}


