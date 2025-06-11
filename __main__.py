
import numpy as np
import os
import sys

from classes import donor, acceptor, eet, parameters
from functions import read_outputs, output, calcs

# ---------------------------------------------------- #
# ---------------------- INPUTS ---------------------- #
#
# Number of states considered
n_states_donor   = 2
n_states_acceptor = 2
# ---------------------------------------------------- #
#
# ==================================================== #
# ===================== PROGRAM ====================== #
#
# -------------------- Initialize -------------------- #
# List of distances, the folders for the acceptor must be named with the format zn-pc_d-1.72
distances_list = ['d-1.72', 'd-1.81', 'd-1.90', 'd-2.06', 'd-2.10', 'd-2.28','d-2.42', 'd-2.67', 'd-2.61','d-2.78', 'd-3.00', 'd-3.05', 'd-3.16']
#
# Get directory of the scirpt to extract simulation results
base_dir = os.path.dirname(__file__)
results_folder = os.path.join(base_dir, 'data/simulation')
#
param = parameters.parameters()
#
donor   = donor.donor(len(distances_list),n_states_donor)
acceptor = acceptor.acceptor(len(distances_list),n_states_acceptor,n_states_donor)
#
eet = eet.eet(len(distances_list),n_states_donor,n_states_acceptor)
# ---------------------------------------------------- #
#
# -- Read donor TDDFT characteristics (fixed position)
for d_state in range(n_states_donor):
    #
    results_folder_donor = results_folder + '/tddft/pt-pc/state-' + str(d_state+1) + '/pt-pc_cam-b3lyp_tzp.log'
    #
    donor.abs[d_state], donor.rad[d_state], donor.nonrad[d_state] = read_outputs.extract_tddft(results_folder_donor,labs=True,lrad=True,lnonrad=True)
    #
#
# -- Read acceptor TDDFT characteristics (modified A-D position)
n_dist = 0
for distance in distances_list:
    #
    for a_state in range(n_states_acceptor):
        #
        results_folder_acceptor = results_folder + '/tddft/zn-pc_' + distance + '/state-' + str(a_state+1) + '/zn-pc_cam-b3lyp_tzp.log'
        #
        acceptor.abs[n_dist,a_state], acceptor.rad[n_dist,a_state], acceptor.nonrad[n_dist,a_state] = read_outputs.extract_tddft(results_folder_acceptor,labs=True,lrad=True,lnonrad=True)
        #
        acceptor.fluorescence_quantum_yield(n_dist,a_state)
        #
    n_dist += 1
    #
#
# --- Read EET and calculate accumulative values for
#     each state-D to state-A combination at each A-D position
n_dist = 0
#
for distance in distances_list:
    #
    for d_state in range(n_states_donor):
        #
        eta_sum = 0.0
        gamma_eet_sum = 0.0
        eet_times_fqy_sum = 0.0
        for a_state in range(n_states_acceptor):
            #
            results_folder_eet = results_folder + '/fret/D_state-' + str(d_state+1) + '_to_A_state-' + str(a_state+1) + '/' + distance + '/input.log'
            #
            # EET quantities
            eet.Gamma_EET[n_dist,d_state,a_state] = read_outputs.extract_eet(results_folder_eet)
            eet.eta_EET[n_dist,d_state,a_state] = calcs.eta_EET(n_dist,d_state,a_state,eet,donor,acceptor)
            #
            gamma_eet_sum = gamma_eet_sum + eet.Gamma_EET[n_dist,d_state,a_state]
            eet_times_fqy_sum = eet_times_fqy_sum + eet.eta_EET[n_dist,d_state,a_state] * acceptor.FQY[n_dist,a_state]
            #
            # This is to check we don't have RET efficiency > 100%
            eta_sum = eta_sum + eet.eta_EET[n_dist,d_state,a_state]
            #
            if (eta_sum > 1.0): sys.exit() # Avoid sum of eta bigger than 1
            #
            #
        # Fluorescence intensities
        #
        #
        donor.fluor_int[n_dist,d_state] = donor.abs[d_state] * (donor.rad[d_state] /
                                                                    (gamma_eet_sum +
                                                                     donor.nonrad[d_state] +
                                                                     donor.rad[d_state] +
                                                                     donor.nonrad_0))

        acceptor.fluor_int[n_dist,d_state] = donor.abs[d_state] * eet_times_fqy_sum
        #

# -----------> OK

    #
    # Total donor/acceptor intensity as sum of all intensities of
    # degenerated excited states for each distance
    donor.fluor_int_total[n_dist] = np.sum(donor.fluor_int[n_dist,:])
    acceptor.fluor_int_total[n_dist] = np.sum(acceptor.fluor_int[n_dist,:])
    #
    n_dist += 1
#
#
# -- Plot fluorescence acceptor-Donor intensities
output.plot_fluor_intensities(donor,acceptor,len(distances_list),distances_list)


# Print the results to plot as single points
# Normalize maximum to experimental value of 2.2182539682539684

print(acceptor.fluor_int_total)

#max_acceptor = np.max(acceptor.fluor_int_total)
#with open('intensities.csv', 'w') as out:
#   out.write('# Distance    Acceptor    Donor\n')
#   for n_dist, distance_str in enumerate(distances_list):
#      distance = distance_str[2:]
#      out.write(distance + '  ' + str((acceptor.fluor_int_total[n_dist]/max_acceptor)*2.2182539682539684) + '   ' + str((donor.fluor_int_total[n_dist]/max_acceptor)*2.2182539682539684) + '\n')
   



