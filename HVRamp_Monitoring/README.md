HV Ramp Monitoring:

When ramping high voltage up or down, LRS experts must monitor self-trigger rates for evidence of 
instabilities (like electrical breakdown) in the detector. If the self-trigger rate spikes, the time
period in question must be rigorously inspected before the high voltage can continue being changed. 

During Run 2, the DQM scripts were insufficient for this purpose. In general, I think, it's better to
be mobile during a HV ramp rather than tied to an unchangeable monitoring script. 

Scripts for ramp monitoring used during Run 2 will be saved in this directory, and improved on in anticipation 
of later runs. 

Ramp_monitoring.ipynb: 

This script takes nearline flow files with raw waveforms and looks at irregularities in trigger rates.
It provides the opportunity to quickly pinpoint regions of instability and inspect individual or sum waveoforms.
