Low-Level Commissioning:

I'm definining "low-level" commissioning as:

1. Dead Channel scans
2. Baseline characterization (per channnel)
3. Environmental noise studies

Scripts used during the 2x2 Run 2 for these purposes will be saved in this directory, and the
procedures governing their use/the acquisition of related data will be described. 

Check_Dead_vs_Alive.ipynb:

	This script should be run over several files with self-triggering data or any other type of data where
	some amount of signal is expected on all channels. In-notebook, it produces no plots. 
	
	It will produce a PDF with the waveform, per channel, with the highest amplitude across N files.

	It will also produce a .csv file with:
		9 rows: the first 8 are a mask for dead/alive channels.
				the last counts channel #s to help with manual changes.
		
	This notebook is primarily useful for checking cable connections and channel status. 


Check_B_and_DC.ipynb:

	This script should be run over a file with self-triggering data or any other type of data where
	some amount of signal is expected on all channels. In-notebook, it can produce plots validating the
	baselines on all channels. 
	
	It also produces a PDF with:
		Optionally: one waveform plotted for each channel to confirm whether a given
					channel is dead or operational. 
		Optionally: the maximum amplitude seen on each channel in the file. 
		
		Always: the average baseline for each channel across the file. 
	
	It produces a .csv file with:
		9 rows: the first 8 are a mask for good/bad baselines.
				the last counts channel #s to help with manual changes.
		
	This notebook is primarily useful for checking baselines quickly. 

