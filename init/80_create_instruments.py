example1 = qt.instruments.create('example1', 'example', address='GPIB::1', reset=True)
dsgen = qt.instruments.create('dsgen', 'dummy_signal_generator')
pos = qt.instruments.create('pos', 'dummy_positioner')
combined = qt.instruments.create('combined', 'virtual_composite')
combined.add_variable_scaled('magnet', example1, 'chA_output', 0.02, -0.13, units='mT')

IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')  # Initialize dmm

#combined.add_variable_combined('waveoffset', [{
#    'instrument': dmm1,
#    'parameter': 'ch2_output',
#    'scale': 1,
#    'offset': 0}, {
#    'instrument': dsgen,
#    'parameter': 'wave',
#    'scale': 0.5,
#    'offset': 0
#    }], format='%.04f')
