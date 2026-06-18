#!/usr/bin/env bash

# By default, run on the host's venv
module unload python 2>/dev/null
module load python/3.11
#pip install ascii
#pip install ruptures

echo "Starting Attempt"
python light_dqm.py     --input_path /global/cfs/cdirs/dune/www/data/2x2/nearline_run2/flowed_light/source_dtg_bin1/two_trig_40us_period_500tick/intensity_scan/hv_60kV_beamC_20uA/decays/ \
                        --file_syntax mpd_run_data_rctl_967_p \
                        --channel_status_file /global/cfs/cdirs/dune/www/data/2x2/people/LRS_run2_team/2x2_LRS_OperatingScripts/Run3_Nearline_Development/channel_status.csv \
                        --output_dir /global/cfs/cdirs/dune/www/data/2x2/people/LRS_run2_team/2x2_LRS_OperatingScripts/Run3_Nearline_Development/Output_Files/Test_061726/ \
                        --tmp_dir /global/cfs/cdirs/dune/www/data/2x2/people/LRS_run2_team/2x2_LRS_OperatingScripts/Run3_Nearline_Development/Output_Files/Test_061726/tmp/ \
                        --start_run 10
echo "Ending Attempt"
