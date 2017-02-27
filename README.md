MultiChannelIO
=======

## What

MultiChannelIO is a class written in python meant to simplify the coding of read and write commands to the National Instruments DAQ USB-6003.  It makes use of the PyDAQmx package to communicate with the NIDAQmx package, written in C, provided by National Instruments.

![](http://s7d5.scene7.com/is/image/ni/04231404?$ni-card-md$)


## Usage

```python
daq = MultiChannelIO(inputChannels, outputChannels, digitalChannels, scalings, channelVoltageLimits, reset)
```

```inputChannels``` is a list of the physical device input channels,
	e.g. ```['Dev1/ai0','Dev1/ai1']```

```outputChannels``` is a list of the physical device output channels,
	e.g. ```['Dev1/ao0']```

```digitalChannels``` is a list of the physical device digital output channels,
	e.g. ```['Dev1/port0/line1']```

optionally, you can input scalings, channelVoltageLimits, and reset

```scalings``` is a list of values of scale factors to apply
	before writing and after reading, 
	e.g. [100,0.05,1]
	note: specify the scalings for all inputs and outputs if you specify any

```channelVoltageLimits``` is a list of pairs of vales of channel range in Volts
	e.g. ((-10.0,10.0),(-10.0,10.0),(-10.0,10.0))
	note: specify the limits for all inputs and outputs if you specify any

```reset``` is a boolean for whether the channels should be reset at instantiation


## Methods

### configure()

Configure the device for reading and writing.  Create “tasks” within the NIDAQmx framework.

### readAll()

Read one value from all input channels.  Returns a python dict referenced by the input channel name.

### read(input_channel, [optional] number_of_points)

Read one value (or number_of_points values) from the specified input channel (defaults to first input channel).  Returns an numpy array of values.

### write(output_channel, value)

Write a persistent value to the specified analog output channel (defaults to first analog output channel).

### readMean(input_channel, [optional] number_of_points)

Read ten points (or the number of points specified, should be less than 2000) from the specified input channel, and return the mean value.

### digitalPulse(digital_output_channel)

Write a 1ms digital high pulse to the output channel specified (defaults to first digital channel).  Function returns after the 1ms pulse is completed.

### reset()

Resets the device.  All outputs return to zero.

## Example Usage

```python
# setup

from MultiChannelIO import MultiChannelIO

daq = MultiChannelIO(['Dev1/ai0'],['Dev1/ao0'],['Dev1/port0/line1'],scalings=[100.0,0.05])

daq.configure()

# set an output voltage (remains indefinitely)

daq.write('Dev1/ao0’,50)

# read voltages

daq.readAll()

# read one channel's voltage

daq.read('Dev1/ai0')

# read 1000 samples and take the mean

daq.readMean('Dev1/ai0',1000)

# send a digital high pulse to port0 line1

daq.digitalPulse()

# reset everything

daq.reset()
```

## Who

Stephen Fleming, PhD candidate at the Golovchenko Lab in the physics department at Harvard University.
