import visa

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM1', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502785::INSTR')
AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', address="10.21.64.117")
