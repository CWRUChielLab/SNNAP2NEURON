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

from __future__ import print_function

import sys
import re
import os
import argparse
from contextlib import contextmanager

from .simulation import Simulation as sim
from .nrnModelPoint import NRNModelPoint
from .nrnModelDist import NRNModelDist


@contextmanager
def cd(newdir):
    """
    A context manager for temporarily changing directory
    """
    prevdir = os.getcwd()
    if newdir:
        os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def snnap2neuron(filePath, cond='p'):
    """
    Run the SNNAP-to-NEURON model translation tool

    Parameters
    ----------

    filePath : string
        Path to SNNAP .smu file.

    cond : {'p', 'd'}
        Method for representing conductances (point or distributed).
        Default: 'p'

    Returns
    -------
    (snnapSim, nrnModel)

    """

    if not os.path.isfile(filePath):
        print('error: file does not exist: ' + str(filePath))
        return None, None

    if cond not in ['p', 'd']:
        print("error: bad conductance mode: " + str(cond))
        return None, None

    simFilePath, simFileName = os.path.split(filePath)

    # file paths given within SNNAP files are always specified relative to the
    # SMU file, so change directory now so all files can be located later
    with cd(simFilePath):

        # create simulation object.
        snnapSim = sim(simFileName)

        # write model in NEURON
        if cond == 'p':
            print("Conductances will be represented as point mechanisms")
            nrnModel = NRNModelPoint(snnapSim)
        elif cond == 'd':
            print("Conductances will be represented as distributed mechanisms")
            nrnModel = NRNModelDist(snnapSim)

        return snnapSim, nrnModel


def main():

    description = """
    An automated translation tool for converting SNNAP models into NEURON models
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", help="path to SNNAP .smu file")
    parser.add_argument("-c", "--cond", choices=['p', 'd'], default='p',
                        help="representation of conductances (point 'p', or distributed 'd')")
    args = parser.parse_args()

    snnap2neuron(args.input, args.cond)


if __name__ == "__main__":
    main()
