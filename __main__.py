
import numpy as np
import os
import sys

from classes import donor, aceptor, eet, parameters
from functions import read_outputs, output, calcs

# ---------------------------------------------------- #
# ---------------------- INPUTS ---------------------- #
results_folder = '/home/pablo/Dropbox/posdoc/fret/tip-transfer/kong/tip-parabola-mols/fig-2d/calc/freq-2.5_ev/tip-d5.0_angs/results'
#
distances_list = ['d-1.72', 'd-1.81', 'd-1.90', 'd-2.06', 'd-2.10', 'd-2.28','d-2.42', 'd-2.67', 'd-2.61','d-2.78', 'd-3.00', 'd-3.05', 'd-3.16']
#
n_states_donor   = 2
n_states_aceptor = 2
#
# ---------------------------------------------------- #
#
# ==================================================== #
# ===================== PROGRAM ====================== #
#
# -------------------- Initialize -------------------- #
param = parameters.parameters()
#
donor   = donor.donor(len(distances_list),n_states_donor)
aceptor = aceptor.aceptor(len(distances_list),n_states_aceptor,n_states_donor)
#
eet = eet.eet(len(distances_list),n_states_donor,n_states_aceptor)
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
# -- Read aceptor TDDFT characteristics (modified A-D position)
n_dist = 0
for distance in distances_list:
    #
    for a_state in range(n_states_aceptor):
        #
        results_folder_aceptor = results_folder + '/tddft/zn-pc_' + distance + '/state-' + str(a_state+1) + '/zn-pc_cam-b3lyp_tzp.log'
        #
        aceptor.abs[n_dist,a_state], aceptor.rad[n_dist,a_state], aceptor.nonrad[n_dist,a_state] = read_outputs.extract_tddft(results_folder_aceptor,labs=True,lrad=True,lnonrad=True)
        #
        aceptor.fluorescence_quantum_yield(n_dist,a_state)
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
        for a_state in range(n_states_aceptor):
            #
            results_folder_eet = results_folder + '/fret/D_state-' + str(d_state+1) + '_to_A_state-' + str(a_state+1) + '/' + distance + '/input.log'
            #
            # EET quantities
            eet.Gamma_EET[n_dist,d_state,a_state] = read_outputs.extract_eet(results_folder_eet)
            eet.eta_EET[n_dist,d_state,a_state] = calcs.eta_EET(n_dist,d_state,a_state,eet,donor,aceptor)
            #
            gamma_eet_sum = gamma_eet_sum + eet.Gamma_EET[n_dist,d_state,a_state]
            eet_times_fqy_sum = eet_times_fqy_sum + eet.eta_EET[n_dist,d_state,a_state] * aceptor.FQY[n_dist,a_state]
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

        aceptor.fluor_int[n_dist,d_state] = donor.abs[d_state] * eet_times_fqy_sum
        #

# -----------> OK

    #
    # Total donor/aceptor intensity as sum of all intensities of
    # degenerated excited states for each distance
    donor.fluor_int_total[n_dist] = np.sum(donor.fluor_int[n_dist,:])
    aceptor.fluor_int_total[n_dist] = np.sum(aceptor.fluor_int[n_dist,:])
    #
    n_dist += 1
#
#
# -- Plot fluorescence Aceptor-Donor intensities
output.plot_fluor_intensities(donor,aceptor,len(distances_list),distances_list)


# Print the results to plot as single points
# Normalize maximum to experimental value of 2.2182539682539684

print(aceptor.fluor_int_total)

#max_aceptor = np.max(aceptor.fluor_int_total)
#with open('intensities.csv', 'w') as out:
#   out.write('# Distance    Acceptor    Donor\n')
#   for n_dist, distance_str in enumerate(distances_list):
#      distance = distance_str[2:]
#      out.write(distance + '  ' + str((aceptor.fluor_int_total[n_dist]/max_aceptor)*2.2182539682539684) + '   ' + str((donor.fluor_int_total[n_dist]/max_aceptor)*2.2182539682539684) + '\n')
   



