Data Quality Monitoring: 

Data taken by the LRS is fed through a nearline, which processes binary files and produces
hdf5 files containing raw waveforms. 

The nearline also sends these hdf5 files through a plotting script intended to monitor the system and
provide feedback to shifters and experts during the detector's operation. 

Following the operating period, these plots can be used to quickly evaluate datasets and provide 
guidance to analyzers looking to target or avoid specific data features.

This directory will document the Run 2 DQM script and attempt to adjust it, to better address  the needs 
observed at the end of Run 2 (sparking identification and characterization). 
