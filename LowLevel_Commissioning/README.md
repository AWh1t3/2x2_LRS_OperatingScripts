Low-Level Commissioning:

I'm definining "low-level" commissioning as:

1. Dead Channel scans
2. Baseline characterization (per channnel)
3. Environmental noise studies

Scripts used during the 2x2 Run 2 for these purposes will be saved in this directory, and the
procedures governing their use/the acquisition of related data will be described. 

Check_B_and_DC.ipynb:

This script should be run over a file with self-triggering data or any other type of data where
some amount of signal is expected on all channels. In-notebook, it produces plots validating the
baselines on all channels. 

It will also produce 8 PDFs with one waveform plotted for each channel to confirm whether a given
channel is dead or operational. This notebook is primarily useful for checking baselines quickly, 
however, as signal can be dependent on file length and triggering configurations.
