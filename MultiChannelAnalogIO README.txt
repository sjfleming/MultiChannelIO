README for MultiChannelAnalogIO.py
Stephen Fleming, 9/4/16

MultiChannelAnalogIO is a class written in python meant to simplify
the coding of simple read and write commands to the NI DAQ USB-6003.

It makes use of the PyDAQmx package to communicate with the 
NIDAQmx package, written in C, provided by National Instruments.




Usage:

MultiChannelAnalogIO(inputChannels, outputChannels, scalings, channelVoltageLimits, reset)

inputChannels is a list of the physical device input channels,
	e.g. ['Dev1/ai0','Dev1/ai1']
outputChannels is a list of the physical device output channels,
	e.g. ['Dev1/ao0']

optionally, you can input scalings, channelVoltageLimits, and reset
scalings is a list of values of scale factors to apply
	before writing and after reading
	e.g. [0.1,0.1,0.05]
channelVoltageLimits is a list of pairs of vales of channel range in Volts
	e.g. ((-10.0,10.0),(-10.0,10.0),(-10.0,10,0))
	note: specify the limits for all inputs and outputs if you specify any
reset is a boolean for whether the channels should be reset at instantiation




Methods:

configure()
read(inputChannel)
readAll()
write(value, outputChannel)
reset()




Example:

# setup
from MultiChannelAnalogIO import MultiChannelAnalogIO
daq = MultiChannelAnalogIO(['Dev1/ai0'],['Dev1/ao0'])
daq.configure()

# set an output voltage (remains indefinitely)
daq.write(50,'Dev1/ao0')

# alternatively
daq.write(50)

# read voltages
daq.readAll()

# read one channel's voltage
daq.read('Dev1/ai0')

# reset everything
daq.reset()


