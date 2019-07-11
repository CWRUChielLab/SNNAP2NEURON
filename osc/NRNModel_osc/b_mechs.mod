: Head Comments
:_A2_B2	K

:_A2_B2	Na


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(S) = (siemens)
	(molar) = (1/liter)
	(mM) = (millimolar)
}

NEURON {
	SUFFIX b_mechs
	USEION k READ ek WRITE ik
	USEION na READ ena WRITE ina

	NONSPECIFIC_CURRENT il
	RANGE
		gl, el, K_g, K_e, K_p,
		K_A_SSA_h, K_A_SSA_s, K_A_SSA_p, K_A_SSA_h, K_A_SSA_s,
		K_A_SSA_p, K_A_tau_tx, K_A_tau_h1, K_A_tau_h1, K_A_tau_tn,
		K_A_tau_p1, K_A_tau_h2, K_A_tau_s2, K_A_tau_p2, K_B_SSB_h,
		K_B_SSB_s, K_B_SSB_p, K_B_SSB_Bn, K_B_tau_tx, K_B_tau_h1,
		K_B_tau_h1, K_B_tau_tn, K_B_tau_p1, Na_g, Na_e,
		Na_p, Na_A_SSA_h, Na_A_SSA_s, Na_A_SSA_p, Na_A_SSA_h,
		Na_A_SSA_s, Na_A_SSA_p, Na_A_tau_tx, Na_A_tau_h1, Na_A_tau_h1,
		Na_A_tau_tn, Na_A_tau_p1, Na_B_SSB_h, Na_B_SSB_s, Na_B_SSB_p,
		Na_B_tau_tx, Na_B_tau_h1, Na_B_tau_h1, Na_B_tau_tn, Na_B_tau_p1
	GLOBAL
		K_A_SSA, K_A_tau, K_B_SSB, K_B_tau, Na_A_SSA, Na_A_tau, Na_B_SSB, Na_B_tau

	THREADSAFE : assigned GLOBALs will be per thread
}

PARAMETER {
	: leak
	gl = 2.5e-07         (S/cm2)
	el = -39.8           (mV)

	: K
	K_gbar = 1.2e-05         (S/cm2)
	K_e = -75.0           (mV)
	K_p = 4               
	K_A_SSA_h = -2.4            (mV)
	K_A_SSA_s = 8.8             (mV)
	K_A_SSA_p = 1
	K_A_SSA_h = -2.4            (mV)
	K_A_SSA_s = 8.8             (mV)
	K_A_SSA_p = 1
	K_A_tau_tx = 27.0            (ms)
	K_A_tau_h1 = -0.0004         (mV)
	K_A_tau_s1 = 11.7            (mV)
	K_A_tau_tn = 2.16            (ms)
	K_A_tau_p1 = 1
	K_A_tau_h2 = -27.0           (mV)
	K_A_tau_s2 = -11.2           (mV)
	K_A_tau_p2 = 1
	K_B_SSB_h = 8.4             (mV)
	K_B_SSB_s = 1.5             (mV)
	K_B_SSB_p = 2
	K_B_SSB_Bn = 0.15
	K_B_tau_tx = 200.0           (ms)
	K_B_tau_h1 = -0.0014         (mV)
	K_B_tau_s1 = 8.3             (mV)
	K_B_tau_tn = 20.0            (ms)
	K_B_tau_p1 = 1

	: Na
	Na_gbar = 7.5e-06         (S/cm2)
	Na_e = 76.6            (mV)
	Na_p = 3               
	Na_A_SSA_h = -18.1           (mV)
	Na_A_SSA_s = 4.8             (mV)
	Na_A_SSA_p = 1
	Na_A_SSA_h = -18.1           (mV)
	Na_A_SSA_s = 4.8             (mV)
	Na_A_SSA_p = 1
	Na_A_tau_tx = 1.5             (ms)
	Na_A_tau_h1 = -8.7            (mV)
	Na_A_tau_s1 = 1.85            (mV)
	Na_A_tau_tn = 0.45            (ms)
	Na_A_tau_p1 = 1
	Na_B_SSB_h = -27.5           (mV)
	Na_B_SSB_s = 9.2             (mV)
	Na_B_SSB_p = 1
	Na_B_tau_tx = 10.0            (ms)
	Na_B_tau_h1 = -15.2           (mV)
	Na_B_tau_s1 = 3.5             (mV)
	Na_B_tau_tn = 2.4             (ms)
	Na_B_tau_p1 = 1

}

ASSIGNED {
	: from NEURON
	v (mV)
	celsius (degC)

	: currents
	il              (mA/cm2)
	ik              (mA/cm2)
	ina             (mA/cm2)

	: conductances
	K_g             (S/cm2)
	Na_g            (S/cm2)

	: reverse potentials
	ek              (mV)
	ena             (mV)

	: rateParameters
	K_A_SSA
	K_A_tau         (ms)
	K_B_SSB
	K_B_tau         (ms)
	Na_A_SSA
	Na_A_tau        (ms)
	Na_B_SSB
	Na_B_tau        (ms)
}
INITIAL {
	rates(v,t)
	K_A = K_A_SSA
	K_B = K_B_SSB
	Na_A = Na_A_SSA
	Na_B = Na_B_SSB
}

STATE {
	K_A
	K_B
	Na_A
	Na_B
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	rates(v,t)
	: leak
	il = gl*(v - el)

	: K
	K_g = K_gbar * (K_A^K_p) * K_B
	ik = K_g*(v - K_e)

	: Na
	Na_g = Na_gbar * (Na_A^Na_p) * Na_B
	ina = Na_g*(v - Na_e)

}

DERIVATIVE states  {
	rates(v,t)
	K_A' = (K_A_SSA - K_A) / K_A_tau
	K_B' = (K_B_SSB - K_B) / K_B_tau
	Na_A' = (Na_A_SSA - Na_A) / Na_A_tau
	Na_B' = (Na_B_SSB - Na_B) / Na_B_tau
}

PROCEDURE rates(v(mV), t(ms)) {
	UNITSOFF
	: Na
	Na_A_SSA = 1/(1 + exp((Na_A_SSA_h-v)/Na_A_SSA_s))^Na_A_SSA_p

	: K
	K_A_SSA = 1/(1 + exp((K_A_SSA_h-v)/K_A_SSA_s))^K_A_SSA_p

	: K_A
	K_A_SSA = 1/(1 + exp((K_A_SSA_h-v)/K_A_SSA_s))^K_A_SSA_p
	K_A_tau = (K_A_tau_tx - K_A_tau_tn)/ (1 + exp((v-K_A_tau_h1)/K_A_tau_s1))^K_A_tau_p1 /(1+exp((v-K_A_tau_h2)/K_A_tau_s2))^K_A_tau_p2 + K_A_tau_tn

	: K_B
	K_B_SSB = (1 - K_B_SSB_Bn)/(1 + exp((v-K_B_SSB_h)/K_B_SSB_s))^K_B_SSB_p + K_B_SSB_Bn
	K_B_tau = (K_B_tau_tx - K_B_tau_tn)/ (1 + exp((v-K_B_tau_h1)/K_B_tau_s1))^K_B_tau_p1 + K_B_tau_tn

	: Na_B
	Na_B_SSB = 1/(1 + exp((v-Na_B_SSB_h)/Na_B_SSB_s))^Na_B_SSB_p
	Na_B_tau = (Na_B_tau_tx - Na_B_tau_tn)/ (1 + exp((v-Na_B_tau_h1)/Na_B_tau_s1))^Na_B_tau_p1 + Na_B_tau_tn

	: Na_A
	Na_A_SSA = 1/(1 + exp((Na_A_SSA_h-v)/Na_A_SSA_s))^Na_A_SSA_p

	UNITSON
}

