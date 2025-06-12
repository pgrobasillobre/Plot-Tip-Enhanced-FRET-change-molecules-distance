import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from classes import acceptor, donor, parameters
from functions import calcs

param = parameters.parameters()
# -------------------------------------------------------------------------------------
def error(error_message):
    print("")
    print("")
    print("   " + error_message)
    print("")
    print("")
    sys.exit()
# -------------------------------------------------------------------------------------
def plot_fluor_intensities(donor,acceptor,n_dist,distances):
    #
    """ Plot fluorescence intensities of donor and acceptor"""
    #
    # Define peaks at which simulated fluorescence intensities are centered
    # We consider the tip-perturbed excitation energies of the donor and acceptor
    donor_peak    = 2.16 # eV emission peak in simulation
    acceptor_peak = 2.05 # eV emission peak in simulation
    #
    min_energy = 1.99 # eV
    max_energy = 2.21 # eV
    #
    grid_points = 1000 # For the Gaussian functions
    #
    x_points = np.linspace(min_energy, max_energy, grid_points)
    #
    fontsize_tics   = 20
    fontsize_labels = 22
    fontsize_titles = 28
    #
    xlabel = 'Energy (eV)'
    ylabel = 'Fluorescence Intensity (arb. units)'
    #
    # Adjust figure and subplots layout    
    fig, ax = plt.subplots(1, 2, figsize=(12, 8))
    plt.subplots_adjust(left=0.12, hspace=0.4, wspace=0.5, top=0.9, bottom=0.1)
    #
    #
    for axes in ax.flat:
        axes.title.set_fontname('Times New Roman')
        axes.xaxis.label.set_fontname('Times New Roman')
        axes.yaxis.label.set_fontname('Times New Roman')
        axes.tick_params(axis='x', labelsize=fontsize_tics)  
        axes.tick_params(axis='y', labelsize=fontsize_tics)  
        for label in axes.get_xticklabels() + axes.get_yticklabels():
            label.set_fontname('Times New Roman')
    #
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Times New Roman'
    plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
    plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'
    plt.rcParams['mathtext.sf'] = 'Times New Roman'
    plt.rcParams['mathtext.default'] = 'regular'

    # Add column titles
    fig.text(0.283, 0.96, 'Experiment', ha='center', va='center', fontsize=fontsize_titles, fontweight='bold', fontname='Times New Roman')
    fig.text(0.730, 0.96, 'Simulation', ha='center', va='center', fontsize=fontsize_titles, fontweight='bold', fontname='Times New Roman')

    # Get the directory of this script to access the experimental data files
    base_dir = os.path.dirname(__file__)
    exp_files = [
        os.path.join(base_dir, "../data/experiment/exp-acceptor.csv"),
        os.path.join(base_dir, "../data/experiment/exp-donor.csv"),
    ]

    # Load experimental data and find global max
    exp_data = []
    exp_global_max = 0
    for file in exp_files:
        try:
            df = pd.read_csv(file, delim_whitespace=True, header=None)
            energy = df.iloc[:,0].values
            intensity = df.iloc[:,1].values
            exp_data.append((energy, intensity))
            if np.max(intensity) > exp_global_max:
                exp_global_max = np.max(intensity)
        except Exception as e:
            error("Could not load {file}: {e}")
            

    # Plot
    #ax[0].set_title('Experiment',fontsize=fontsize_titles)
    ax[0].plot(exp_data[0][0],exp_data[0][1], color='red', marker='o', label = 'Zn-Pc (Acceptor)')
    ax[0].plot(exp_data[1][0],exp_data[1][1], color='black', marker='o', label = 'Pt-Pc (Donor)')
    ax[0].set_ylim(-0.25, 2.75)  
    ax[0].set_yticks([0.0,0.5,1.0,1.5,2.0,2.5])
    ax[0].set_xlim(1.35, 3.3)  
    ax[0].set_xticks([1.5,1.8,2.1,2.4,2.7,3.0,3.3])
    ax[0].set_xlabel('d (nm)', fontsize=fontsize_labels, labelpad=10.0)
    ax[0].set_ylabel('STML Intensity (counts per pC)', fontsize=fontsize_labels, labelpad=20.0)


    # For simulated data, check global normalization value to match experimental data
    norm_sim = max(acceptor.fluor_int_total.max(), donor.fluor_int_total.max())
    norm_sim = norm_sim / exp_global_max

    # Normalize fluorescence of donor and acceptor
    distances_values = np.array([float(d.split('-')[1]) for d in distances])
    for n in range(n_dist):
        acceptor.fluor_int_total[n] = acceptor.fluor_int_total[n] / norm_sim
        donor.fluor_int_total[n]   = donor.fluor_int_total[n]   / norm_sim

    # Plot
    #ax[1].set_title('Simulation',fontsize=fontsize_titles)
    ax[1].plot(distances_values, acceptor.fluor_int_total, color='red', marker='o', label='Zn-Pc (Acceptor)')
    ax[1].plot(distances_values, donor.fluor_int_total, color='black', marker='o', label='Pt-Pc (Donor)')
    ax[1].set_ylim(-0.25, 2.75)  
    ax[1].set_yticks([0.0,0.5,1.0,1.5,2.0,2.5])
    ax[1].set_xlim(1.35, 3.3)  
    ax[1].set_xticks([1.5,1.8,2.1,2.4,2.7,3.0,3.3])
    ax[1].set_xlabel('d (nm)', fontsize=fontsize_labels, labelpad=10.0)
    ax[1].set_ylabel('Fluorescence Intensity (arb. units)', fontsize=fontsize_labels, labelpad=20.0)


   
    plt.show()
    #plt.savefig('/home/pablo/Desktop/plot.png')
