from pyraisrc.information_block import InformationBlock
import datetime
from pyraisrc import demodulator, modulator, coder_decoder

info_block = InformationBlock.from_datetime(datetime.datetime.now(), time_zone='CET')
frame1, frame2 = coder_decoder.encode(info_block)

waveform = modulator.generate_waveform(frame1, frame2, 44100, amplitude=1.0)
modulator.save_waveform_to_file(waveform, 'examples/output_test.wav', sampling_rate=44100)

demodulator.plot_from_file('examples/output_test.wav')
