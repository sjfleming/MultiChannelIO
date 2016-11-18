import numpy

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *

class MultiChannelAnalogIO():
    """Class to create a multi-channel analog input and output
    
    Usage: daq = MultiChannelAnalogIO(inputChanels, outputChannels)
        physicalChannel: a string or a list of strings
    optional parameter: scalings: list of doubles, conversion factors
                        limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        read(name), return the value of the input name
        readAll(), return a dictionary name:value
        write(val), write the value to the analog output
    
    Modified from website example, Stephen Fleming, 9/4/16
    """
    def __init__(self, inputChannels, outputChannels, scalings = None, limit = None, reset = True):
        # Handle inputs and construct class
        if type(inputChannels) == type(""):
            self.inputChannels = [inputChannels]
        else:
            self.inputChannels = inputChannels
        self.numberOfInputChannels = inputChannels.__len__()
        
        if type(outputChannels) == type(""):
            self.outputChannels = [outputChannels]
        else:
            self.outputChannels = outputChannels
        self.numberOfOutputChannels = outputChannels.__len__()
        
        chans = self.inputChannels + self.outputChannels
        if limit is None:
            self.limit = dict([(name, (-10.0,10.0)) for name in chans])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in chans])
        else:
            self.limit = dict([(name, limit[i]) for  i,name in enumerate(chans)])
        
        if scalings is None:
            self.scalings = dict([(name, 0.1) for name in inputChannels])
            self.scalings.update(dict([(name, 0.05) for name in outputChannels]))
        else:
            self.scalings = dict([(name, scalings[i]) for  i,name in enumerate(chans)])
        
        if reset:
            DAQmxResetDevice(inputChannels[0].split('/')[0])
            DAQmxResetDevice(outputChannels[0].split('/')[0])
        
    def configure(self):
        # Create one task handle per channel
        inputTaskHandles = dict([(name,TaskHandle(0)) for name in self.inputChannels])
        for name in self.inputChannels:
            DAQmxCreateTask("",byref(inputTaskHandles[name]))
            DAQmxCreateAIVoltageChan(inputTaskHandles[name],name,"",DAQmx_Val_RSE,
                                     self.limit[name][0],self.limit[name][1],
                                     DAQmx_Val_Volts,None)
        outputTaskHandles = dict([(name,TaskHandle(0)) for name in self.outputChannels])
        for name in self.outputChannels:
            DAQmxCreateTask("",byref(outputTaskHandles[name]))
            DAQmxCreateAOVoltageChan(outputTaskHandles[name],name,"",
                                     self.limit[name][0],self.limit[name][1],
                                     DAQmx_Val_Volts,None)
        self.inputTaskHandles = inputTaskHandles
        self.outputTaskHandles = outputTaskHandles
        
    def readAll(self):
        return dict([(name,self.read(name)) for name in self.inputChannels])
    
    def read(self, name = None):
        if name is None:
            name = self.inputChannels[0]
        taskHandle = self.inputTaskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((1,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,1,10.0,DAQmx_Val_GroupByChannel,data,1,byref(read),None)
        DAQmxStopTask(taskHandle)
        return data[0]*self.scalings[name]
    
    def write(self, val, name = None):
        if name is None:
            name = self.outputChannels[0]
        taskHandle = self.outputTaskHandles[name]
        DAQmxStartTask(taskHandle)
        scaledVal = val*self.scalings[name]
        DAQmxWriteAnalogScalarF64(taskHandle, 1, 10.0, scaledVal, None)
        DAQmxStopTask(taskHandle)
        return True
    
    def reset(self):
        DAQmxResetDevice(self.inputChannels[0].split('/')[0])
        DAQmxResetDevice(self.outputChannels[0].split('/')[0])