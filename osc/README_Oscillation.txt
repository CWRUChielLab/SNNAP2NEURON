README_OSC.txt

The goal of the present simulation is to illustrate
how to construct a simple nerual network, which in
turn can produce interesting patterns of nerual activity.

This simulation illustrates how a simple three cell
network might function as a central pattern
generator (CPG).

The network of three cells and three synaptic connections
is illustrated in Network.jpg.

Cells 'a' and 'b' have identical properties (i.e., they
both use the same *.neu file).  Cell 'c' is different
only in that is uses a different leakage conductance
(i.e. leak1.vdg vs. leak.vdg for cell 'c' vs. cells
'a' and 'b', respectively).  This minor difference makes
cell 'c' spontaneously active.

A depolarizing current is injected into cell 'a' 500 ms
into the simulation.  This causes cell 'a' to spike, which
excites cell 'b' and inhibits cell 'c'.  When cell 'b' reaches
threshold, it fires, which in turn inhibit cell 'a' and 
releases cell 'c' from inhibition.  

This cycle of alternating excitation and inhibition produces
patterned neural activity in this simple three cell network.

The results of this simulation are illustrated in
Oscillation.jpg.