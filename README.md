# pyRAIsrc - Time Signal Tools

### History
Between 1979 and 2016, the italian national television and radio broadcast company (RAI) used to broadcast the exact time from the atomic clock of the INRiM, the national institute of metrologic research. After the 31st of December 2016, INRiM exact time stopped being broadcast by radio, in favour of the more efficient and precise Network Time Protocol syncronization. The time signal as of 2022 is still broadcast on Rai Radio 1 for nostalgia purposes, but isn't used to sync devices anymore.

### SRC time signal structure
What follows is a diagram explaining the structure of the coded time signal, translated from [Giorgio De Luca's personal blog](http://ricercasperimentale.blogspot.com/2016/12/addio-al-segnale-orario-rai-src.html). 
![](diagrams/signal_structure.png)

More information about the history of the SRC can be found on the [INRiM website](http://rime.inrim.it/labtf/src/)

_________________________________

### Library modules
- information_block.py
  - data structure to store relevant information from the SRC time signal
- signal_utils.py
  - utils to manipulate the signal waveform or binary sequences
- coder_decoder.py
  - used to encode or decode the binary frames
- modulator.py
  - functions to turn binary frames to waveforms
  - function to save the waveform as a wav file
- demodulator.py
  - functions to decode signals from files
  - functions to plot signals and filtered frequencies