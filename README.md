# SNNAP2NEURON
Automatically translate SNNAP simulations to NEURON.

## Usage

1. Download this project, extract it, and navigate to the extracted directory

2. Run `readS.py -i [.smu file you wish to translate]`

In the directory of the SNNAP project you translated, a new folder named `NRNModel_[name]` will be created, containing the necesary `.hoc` files to replicated the results of the SNNAP simulation in NEURON.

All the necessary `.mod` files will be found in the directory of this project: `SNNAP2NEURON/utilityFiles/snnap_modFiles`.

1. Compile the `*.mod` files

    - [Windows](https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html)
    - [Mac](https://www.neuron.yale.edu/neuron/static/docs/nmodl/macos.html)
    - [Linux/Unix](https://www.neuron.yale.edu/neuron/static/docs/nmodl/unix.html)

2. Run `NRNModel_[name]/sim_[name].hoc` with NEURON.

Your SNNAP results should be reproduced. For help visualizing them, check `UseExample.ipynb`.
