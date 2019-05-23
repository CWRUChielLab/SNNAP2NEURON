COMMENT
 * snnap_cs.mod
 *
 * NEURON mechanism for implementing a SNNAP-style chemical synapse
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
   : name of the mechanism
   : only for At: type 1 or 2 in .fAt file

      snnap_cs2_At12

   NONSPECIFIC_CURRENT
   : currents not associated with varying ion concentrations

      i

   RANGE
   : non-global variables and constants
   : specific to each instance of the mechanism

    i,
    e,
    g,

    on,
    dur,
    taucs1,
    taucs2,
    : tauXt1,
    : tauXt2,


    : model control variables
	Ics_type,
    fAt_type,
    At_type,
    : Xt_type,

    : parameters associated with fAt module
    fAt_a,
    fAt_b

}

UNITS {
      (mV) = (millivolt)
      (uS) = (microsiemens)
      (nA) = (nanoamp)
}

PARAMETER {
   : declaration of fixed-value parameters

    e           (mV)
    g           (uS)

    dur         (ms)
    taucs1      (ms)              : for both At_Type 3 and 4
    taucs2      (ms)              : used only for At_Type 4
    : tauXt1      (ms)
    : tauXt2      (ms)

    Ics_type
    fAt_type
    At_type
    : Xt_type

    : parameters associated with fAt module
    fAt_a
    fAt_b
}

ASSIGNED {
   : declaration of non-state variables

      v           (mV)  : postsynaptic voltage
      i           (nA)
      on                : on=1 during a presynaptic spike
							 : on=0 in the absence of a presynaptic spike

}

BREAKPOINT {
   : main computational block
   : set with fcurrent() and re-evaluated throughout the simulation
   : derivimplicit is used because the equations are not of the form y' = f(v,y)
   :    since they are nonlinear or involve states other than y
   : derivimplicit has first-order accuracy
   : equation A5

    if (Ics_type == 1) {
        : time dependent activation function 
        if (fAt_type == 1) {
	        i = g * At() * (v - e)

        }

        if (fAt_type == 2) {
            : Assuming A_peak = 0.7 :FOR-NOW
	        :i = g * At() / 0.7 * (v - e)
	        i = g * 2.0 * (v - e)
        }

        if (fAt_type == 3) {
            : Assuming A_peak = 0.7 :FOR-NOW
	        i = g * ( fAt_a + fAt_b*At())  * (v - e)
        }
        if (fAt_type == 4) {
            : 
	        i = g * ( 1 + fAt_b*At())  * (v - e)
	        :i = g * 2.0 * (v - e)
        }
    } else {
        : time and voltage dependent activation :TODO
        i = g * 1.0 * (v - e)
    }
}

INITIAL {
   : initial conditions
   : set with finitialize()

      on  = 0
}


FUNCTION At() () {

    if (At_type == 1) {
        At = t * exp(-t/taucs1)
    }
    if (At_type == 2) {
        At = taucs1*taucs2 * (exp(-t/taucs1) - exp(-t/taucs2)) / (taucs1-taucs2)
    }

}

NET_RECEIVE (weight) {
   : receiver for NetCon events
   : external events triggered by a presynatic spike have flag=0
   : self-issued events triggered after a delay have flag=1
   : weight is not used

   if (flag == 0) {
      : presynaptic spike began
      if (!on) {
         on = 1            : turn the synapse on
         net_send(dur, 1)  : offset after dur with flag=1
      } else {
         net_move(t + dur) : already on, so postpone offset time
      }
   }

   if (flag == 1) {
      : presynaptic spike ended
      on = 0               : turn the synapse off
   }
}
