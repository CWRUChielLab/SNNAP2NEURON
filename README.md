# SNNAP2NEURON
*An automated translation tool for converting SNNAP models into NEURON models*

## Usage

1. Download this project, extract it, and navigate to the extracted directory.

2. Install the tool by running `python setup.py develop`.

3. From any directory, you can now run the `snnap2neuron` command on a SNNAP
   `.smu` simulation file, e.g.,

    `snnap2neuron my_sim.smu`

   Alternatively, use the Python API:

    ```python
    >>> from snnap2neuron import snnap2neuron
    >>> snnap2neuron('my_sim.smu')
    ```

In the directory containing the SNNAP `.smu` file, a new folder named
`NRNModel_[name]` will be created, containing the necessary `.hoc` files to
replicate the results of the SNNAP simulation in NEURON.

All the necessary `.mod` files will be found in the directory of this project:
`SNNAP2NEURON/utilityFiles/snnap_modFiles`.

1. Compile the `*.mod` files:

    - [Windows](https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html)
    - [Mac](https://www.neuron.yale.edu/neuron/static/docs/nmodl/macos.html)
    - [Linux/Unix](https://www.neuron.yale.edu/neuron/static/docs/nmodl/unix.html)

2. Run `NRNModel_[name]/sim_[name].hoc` with NEURON.

Your SNNAP results should be reproduced. For help visualizing them, check
[`UseExample.ipynb`](UseExample.ipynb).
