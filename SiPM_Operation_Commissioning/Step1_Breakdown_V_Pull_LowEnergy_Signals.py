import pandas as pd
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import os
import h5py
import glob
import numpy as np
import yaml
import argparse
from scipy.ndimage import uniform_filter1d

def thd_correct(array):

    # Define start and end indices
    indices = np.arange(0, 25) * 25  # (39,)
    start_indices, end_indices = indices[:-1], indices[1:]  # (39,)

    segment_range = np.arange(25)  # Shape: (25,)
    index_array = start_indices[:, None] + segment_range  # Shape: (39, 25)

    # Extract data using advanced indexing
    sliced_data = array[..., index_array]

    ranges = np.abs(np.ptp(sliced_data, axis=-1))
    #ranges = np.ptp(sliced_data, axis=-1)  # Compute range (n, 8, 64, 39)
    means = np.mean(sliced_data, axis=-1)  # Compute mean (n, 8, 64, 39)

    # Find ordering based on the smallest range
    smallest_ordering = np.argsort(ranges, axis=-1)  # Shape (n, 8, 64, 39)
    # Mask zero ranges
    mask_zero = (ranges != 0)
    ranges = np.where(mask_zero, ranges, np.nan)
    means = np.where(mask_zero, means, np.nan)

    # Sort means using the ordering
    sorted_means = np.take_along_axis(means, smallest_ordering, axis=-1)  # Shape (n, 8, 64, 39)
    sorted_range = np.take_along_axis(ranges, smallest_ordering, axis=-1)
    # Compute average of 2nd, 3rd, and 4th smallest means
    average_mean = np.mean(sorted_means[..., 1:3], axis=-1)  # Shape (n, 8, 64)
    expanded_mean = average_mean[..., None] 
    broadcasted_mean = np.tile(expanded_mean, (1, 600))  
    filtered_wvfm = array - broadcasted_mean

    return filtered_wvfm

def pedestal(array):

    # Define start and end indices
    indices = np.arange(0, 13) * 50  # (39,)
    start_indices, end_indices = indices[:-1], indices[1:]  # (39,)

    segment_range = np.arange(50)  # Shape: (25,)
    index_array = start_indices[:, None] + segment_range  # Shape: (39, 25)

    # Extract data using advanced indexing
    sliced_data = array[..., index_array]
    
    ranges = np.ptp(sliced_data, axis=-1)  # Compute range (n, 8, 64, 39)

    # Find ordering based on the smallest range
    smallest_region = np.argmin(ranges, axis=-1) * 50 # Shape (n, 8, 64, 39)
    pedestal_region = array[smallest_region:smallest_region+50]

    return pedestal_region

def kill_weirdos(array):
    #good_mask = (array[:,:,:,-1] > (array[:,:,:,0] - 120))
    absolute_mean = np.mean(np.abs(array[:,:,:,:] - (np.mean(array[:,:,:,:50],axis=-1))[:, :, :, np.newaxis]), axis=-1)
    normal_mean = np.mean(array[:,:,:,:50], axis=-1)
    #mean_abs_array = np.mean(absolute_array, axis=-1)
    #mean_norm_array = np.mean(array, axis=-1)
    #print(absolute_mean - normal_mean)
    good_mask = ((absolute_mean - normal_mean) < 50)
    print("Good Mask Shape:", np.shape(good_mask))
    print("Good Mask:", np.sum(good_mask, axis=0))
    #broadcasted_mask = np.tile(good_mask, (1, 1000)) 
    filtered_array = array * good_mask[:, :, :, np.newaxis]

    return filtered_array

def peak_finder(wvfm, n_noise_factor,
                    n_bins_rolled,
                    n_sqrt_rt_factor,
                    pe_weight,
                    use_rising_edge=True):
        # height = flat threshold over noise (n*sigma)
        height = n_noise_factor[..., np.newaxis, np.newaxis] * np.ones(wvfm.shape[-1]) #* noise[..., np.newaxis] * np.ones(wvfm.shape[-1])
        # dynamic_threshold = rolling threshold of previous 5 bins + n*sqrt(rolling threshold)
        wvfm_rolled = np.roll(wvfm, n_bins_rolled)
        rolling_average = uniform_filter1d(wvfm_rolled, size=n_bins_rolled)
        sqrt_rolling_average = np.sqrt(np.abs(rolling_average) * pe_weight**2)
        sqrt_rolling_average[sqrt_rolling_average == 0] = 1
        dynamic_threshold = rolling_average + n_sqrt_rt_factor*sqrt_rolling_average
        # find bins over dynamic threshold and noise floor
        bins_over_dynamic_threshold = (wvfm > dynamic_threshold) & (wvfm > height)
        # Find first bins over threshold (rising edge)
        first_bins_over = bins_over_dynamic_threshold.copy()
        first_bins_over[..., 1:] &= ~bins_over_dynamic_threshold[..., :-1]
        if use_rising_edge:
            return first_bins_over
        
def tag_dark_counts(N_Files, Voltage, Run, Window):

     file_num = 0
     dark_count_wvfm = np.zeros((1000,8,64,200), dtype=np.int16)
     count = np.zeros((8,64))
     sipm_channels = ([4,5,6,7,8,9] + \
                     [10,11,12,13,14,15] + \
                     [20,21,22,23,24,25] + \
                     [26,27,28,29,30,31] + \
                     [36,37,38,39,40,41] + \
                     [42,43,44,45,46,47] + \
                     [52,53,54,55,56,57] + \
                     [58,59,60,61,62,63])
     print('aaa')
    
     #file_list = glob.glob("/global/cfs/cdirs/dune/www/data/2x2/nearline/flowed_light/data_bin004/*.FLOW.hdf5")
     #file_list = glob.glob("/global/cfs/cdirs/dune/users/ajwhite/2x2_Data/2x2_Filtered/LRS_FLOW/mpd_run_hvramp_rctl_105_p1*")
     #for file in file_list:
     #start_value = 500 # for the radon injection run
     start_value = 0
     for Nf in range(N_Files):
          #file = f'/global/cfs/cdirs/dune/www/data/2x2/nearline_run2/flowed_light/cold_commission/48V_VoltScan/mpd_run_dbg_rctl_935_p{Nf}.FLOW.hdf5'
          #file = f'/global/cfs/cdirs/dune/www/data/2x2/nearline_run2/flowed_light/source_rn_bin1/injection/mpd_run_data_rctl_776_p{Nf}.FLOW.hdf5'
          file = f'/global/cfs/cdirs/dune/www/data/2x2/nearline_run2/flowed_light/postrun_status_check/first_check/mpd_run_data_rctl_{Run}_p{Nf}.FLOW.hdf5'
          if file_num < N_Files: #508:
               print('file number:', file_num)
               print(count)
               file_num += 1
               if not os.path.isfile(file):
                    continue
               else:
                    with h5py.File(file, 'r') as h5:
                         #print('bbb')
                         #light_wvfms = h5['light/wvfm/data']['samples']
                         #light_wvfms_rwm = np.max(light_wvfms[:,0,18,:], axis=-1)
                         #offbeam_mask = np.where(light_wvfms_rwm < 1e4)[0]
                         #offbeam_wvfm_v1 =  light_wvfms[offbeam_mask, :, :, :]
                         offbeam_wvfm_v1 =  h5['light/wvfm/data']['samples']
                         #print('a')
                         #del light_wvfms_rwm
                         #del light_wvfms
                         #del offbeam_mask
                         offbeam_wvfm_v2 =  thd_correct(offbeam_wvfm_v1)
                         #print('b')
                         del offbeam_wvfm_v1
                         #offbeam_wvfm_v3 = kill_weirdos(offbeam_wvfm_v2)
                         #print('c')
                         #del offbeam_wvfm_v2
                         #del offbeam_wvfm_v1
                         offbeam_wvfm_v4 =  offbeam_wvfm_v2[:, :, sipm_channels, :] #* gain_array[:, :, np.newaxis]
                         #offbeam_wvfm_v4 =  offbeam_wvfm_v3[:, :, sipm_channels, :] #* gain_array[:, :, np.newaxis]
                         #print('d')
                         #del offbeam_wvfm_v3
                         del offbeam_wvfm_v2
                         #n_noise_factor=np.array([130, 130, 210, 210, 210, 210, 210, 210]) # Decommissioning values
                         n_noise_factor=np.array([110, 110, 190, 190, 190, 190, 190, 190]) # June 2025 values
                         
                         first_bins = peak_finder(wvfm=offbeam_wvfm_v4[:, :, :, 20:], n_noise_factor=n_noise_factor, n_bins_rolled=1, n_sqrt_rt_factor=0, pe_weight=0, use_rising_edge=True)
                         #print('Shape of first_bins:', np.shape(first_bins))
                         #print(first_bins)
                         #del noise_thresholds

                         #print(np.shape(np.sum(np.sum(np.sum(first_bins, axis=-1), axis=-1), axis=-1)))
                         #print(np.sum(np.sum(np.sum(first_bins, axis=-1), axis=-1), axis=-1))
                         #per_event_hits = np.sum(np.sum(np.sum(first_bins, axis=-1), axis=-1), axis=-1)
                         #print(np.sum(per_event_hits > 0))

                         for adc in range(8):
                              for channel in range(48):
                                   adc_channel = sipm_channels[channel]
                                   tester=0
                                   for event in range(np.shape(offbeam_wvfm_v4)[0]):
                                        hit_idx = np.where(first_bins[event, adc, channel]==1)[0]
                                        if len(hit_idx) > 0:
                                             for j in range(len(hit_idx)):
                                                  cut_1 = (count[adc, adc_channel] < 999)
                                                  #cut_2 = (hit_idx[0] >=3 )
                                                  hit_value = hit_idx[j] + 20
                                                  last_tick = np.shape(offbeam_wvfm_v4)[-1] - (Window - 2)
                                                  cut_3 = (hit_value <= last_tick)
                                                  #combo_cut = cut_2*cut_3*cut_1
                                                  combo_cut = cut_3*cut_1
                                                  if combo_cut==1:

                                                       dark_count_form = offbeam_wvfm_v4[event, adc, channel, hit_value-3:hit_value+(Window-3)]
                                                       #dark_count_int = (dark_count_form / gain_array[adc, channel]).astype(np.int16)
                                                       # June 2025, used: 
                                                       #cut_4 = (dark_count_form[-1] < 90)
                                                       #cut_5 = (np.min(dark_count_form) > -90)
                                                       if adc >=2:
                                                            #cut_4 = (np.abs(dark_count_form[-1]) < 400)
                                                            #cut_5 = (dark_count_form[0] < 450)
                                                            #cut_6 = (np.min(dark_count_form[3:13]) > -500)
                                                            #cut_4 = (np.abs(dark_count_form[-1]) < 250)
                                                            cut_4 = (np.max(dark_count_form[-6:]) < 80)
                                                            cut_5 = (dark_count_form[0] < 80)
                                                            cut_6 = (np.min(dark_count_form) > -80)
                                                            #cut_7 = (np.max(dark_count_form) <=  np.max(dark_count_form[3:6]))
                                                            sequence = (dark_count_form[2] > dark_count_form[3]) + (dark_count_form[3] > dark_count_form[4]) + (dark_count_form[4] > dark_count_form[5]) + (dark_count_form[5] > dark_count_form[6])
                                                            cut_7 = (np.sum(sequence) < 2)
                                                            #difrl = np.diff(dark_count_form[2:7])
                                                            #cut_7 = (np.sum(np.diff(np.sign(difrl)) != 0) < 2)
                                                            cut_8 = np.prod(dark_count_form[3:5] > n_noise_factor[adc])
                                                            cut_9 = (np.sum(dark_count_form) < 2.5e4) and (np.sum(dark_count_form) > -1.5e3)
                                                       else: 
                                                            cut_4 = (np.max(dark_count_form[-6:]) < 100)
                                                            cut_5 = (dark_count_form[0] < 100)
                                                            cut_6 = (np.min(dark_count_form) > -100)
                                                            #cut_7 = (np.max(dark_count_form) <=  np.max(dark_count_form[3:6]))
                                                            #difrl = np.diff(dark_count_form[2:7])
                                                            sequence = (dark_count_form[2] > dark_count_form[3]) + (dark_count_form[3] > dark_count_form[4]) + (dark_count_form[4] > dark_count_form[5]) + (dark_count_form[5] > dark_count_form[6])
                                                            cut_7 = (np.sum(sequence) < 2)
                                                            #cut_7 = (np.sum(np.diff(np.sign(difrl)) != 0) < 2)
                                                            cut_8 = np.prod(dark_count_form[3:5] > n_noise_factor[adc])
                                                            cut_9 = (np.sum(dark_count_form) > -1.5e3)
                                                       combo_cut_2 = cut_4*cut_5*cut_6*cut_7*cut_8*cut_9
                                                       del cut_4, cut_5, cut_6, cut_7, cut_8, cut_9#, difrl
                                                       #print('aaa')
                                                       if combo_cut_2==1:                                                  
                                                            dark_count_int = (dark_count_form).astype(np.int16)
                                                            pedestal_int = (pedestal(offbeam_wvfm_v4[event, adc, channel, :])).astype(np.int16)
                                                            del dark_count_form
                                                            #try:
                                                            next_wvfm_idx = np.where(dark_count_wvfm[:,adc,adc_channel, 63] == 0)[0]#[0]
                                                            ped_check1 = (np.abs(np.mean(pedestal_int)) < 20)
                                                            ped_check2 = (np.min(pedestal_int) > -100)
                                                            ped_check3 = (np.max(pedestal_int) < 100)
                                                            if (ped_check1*ped_check2*ped_check3) == 1:
                                                                 dark_count_wvfm[next_wvfm_idx,adc,adc_channel, 60:(60+Window)] += dark_count_int
                                                                 dark_count_wvfm[next_wvfm_idx,adc,adc_channel, 0:50] += pedestal_int
                                                                 count[adc, adc_channel] += 1
                                                            del next_wvfm_idx
                                                            del dark_count_int

                                                       else: 
                                                            del dark_count_form
                                                       #except: 
                                                  if (cut_1+tester) == 0:
                                                       print(f'ADC {adc}, Channel {channel}, Event {event}')
                                                       tester += 1
                                        #else:
                                        #     if count[adc, adc_channel] < 500:
                                        #          dark_count_form = offbeam_wvfm_v4[event, adc, channel, 0:25]
                                        #          dark_count_int = (dark_count_form / gain_array[adc, channel]).astype(np.int16)
                                        #          del dark_count_form
                                        #          next_wvfm_idx = np.where(dark_count_wvfm[:,adc,adc_channel, 63] == 0)[0][0]
                                        #          dark_count_wvfm[next_wvfm_idx,adc,adc_channel, 60:85] += dark_count_int
                                        #          del dark_count_int
                                        #          del next_wvfm_idx
                                        #          count[adc, adc_channel] += 1
                                        del hit_idx
                                   del adc_channel
                                   del tester
                         del offbeam_wvfm_v4
                         del first_bins   
     print(count)
     del count

     return dark_count_wvfm

def main(output_file, voltage=None, run=None, window=50):
    
    new_wvfms = tag_dark_counts(N_Files=1, Voltage=voltage, Run=run, Window=window)
    np.savez(output_file, data=new_wvfms)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_file', default=None, required=True, type=str, \
                        help='''string corresponding to desired output file path and name''')
    parser.add_argument('-v', '--voltage', default=None, required=True, type=int, \
                        help='''int corresponding to operating voltage''')
    parser.add_argument('-r', '--run', default=None, required=True, type=int, \
                        help='''int corresponding to light file run number''')
    parser.add_argument('-w', '--window', default=None, required=True, type=int, \
                        help='''int corresponding to tick width of signal integration window''')
    args = parser.parse_args()
    main(**vars(args))