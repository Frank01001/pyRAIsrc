from pyraisrc.information_block import InformationBlock
from pyraisrc import demodulator, coder_decoder

examples_folder_path = ''
filename = 'noise_2.wav'

full_path = examples_folder_path + '/' + filename

demodulator.print_file_info(full_path)
binary_sequence = demodulator.get_sequence_from_file(full_path, perfect_generation=False)
print(binary_sequence)
demodulator.plot_from_file(full_path)

info_block = coder_decoder.decode(binary_sequence)
info_block.print_info()