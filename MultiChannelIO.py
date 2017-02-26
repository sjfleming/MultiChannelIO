import numpy
import time

from PyDAQmx.DAQmxFunctions import *
from PyDAQmx.DAQmxConstants import *

class MultiChannelIO():
    """Class to create a multi-channel input and output object
    
    Usage: daq = MultiChannelIO(inputChanels, outputChannels, digitalChannels)
        physicalChannel: a string or a list of strings
    optional parameter: scalings: list of doubles, conversion factors
                        limit: tuple or list of tuples, the AI limit values
                        reset: Boolean
    Methods:
        read(name), return the value of the input name
        readAll(), return a dictionary name:value
        write(val), write the value to the analog output
    
    Stephen Fleming, 12/8/16
    """
    def __init__(self, inputChannels, outputChannels, digitalChannels = None, scalings = None, limit = None, reset = True):
        # Handle inputs and construct class
        
        # analog inputs
        if type(inputChannels) == type(""):
            self.inputChannels = [inputChannels]
        else:
            self.inputChannels = inputChannels
        self.numberOfInputChannels = inputChannels.__len__()
        
        # analog outputs
        if type(outputChannels) == type(""):
            self.outputChannels = [outputChannels]
        else:
            self.outputChannels = outputChannels
        self.numberOfOutputChannels = outputChannels.__len__()
        
        # digital outputs (at least one auto-generated)
        if digitalChannels is None:
            digitalChannels = "/Dev1/port0/line0"
        if type(digitalChannels) == type(""):
            self.digitalChannels = [digitalChannels]
        else:
            self.digitalChannels = digitalChannels
        self.numberOfDigitalChannels = digitalChannels.__len__()
        
        # set analog channel limits
        chans = self.inputChannels + self.outputChannels
        if limit is None:
            self.limit = dict([(name, (-10.0,10.0)) for name in chans])
        elif type(limit) == tuple:
            self.limit = dict([(name, limit) for name in chans])
        else:
            self.limit = dict([(name, limit[i]) for  i,name in enumerate(chans)])
        
        # set analog scalings
        if scalings is None:
            self.scalings = dict([(name, 100.0) for name in inputChannels])
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
        digitalTaskHandles = dict([(name,TaskHandle(0)) for name in self.digitalChannels])
        for name in self.digitalChannels:
            DAQmxCreateTask("",byref(digitalTaskHandles[name]))
            DAQmxCreateDOChan(digitalTaskHandles[name],name,"",DAQmx_Val_ChanForAllLines)
        self.inputTaskHandles = inputTaskHandles
        self.outputTaskHandles = outputTaskHandles
        self.digitalTaskHandles = digitalTaskHandles
        
    def readAll(self):
        return dict([(name,self.read(name, 1)) for name in self.inputChannels])
    
    def read(self, name = None, numpts = 1):
        if name is None:
            name = self.inputChannels[0]
        taskHandle = self.inputTaskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.zeros((numpts,), dtype=numpy.float64)
        read = int32()
        DAQmxReadAnalogF64(taskHandle,numpts,10.0,DAQmx_Val_GroupByChannel,data,numpts,byref(read),None)
        DAQmxStopTask(taskHandle)
        if numpts == 1:
            return data[0]*self.scalings[name]
        return data*self.scalings[name]
    
    def readMean(self, name = None, numpts = 10):
        data = self.read(name, numpts)
        return numpy.mean(data)
    
    def write(self, name = None, val = 0):
        if name is None:
            name = self.outputChannels[0]
        taskHandle = self.outputTaskHandles[name]
        DAQmxStartTask(taskHandle)
        scaledVal = val*self.scalings[name]
        DAQmxWriteAnalogScalarF64(taskHandle, 1, 10.0, scaledVal, None)
        DAQmxStopTask(taskHandle)
        return True
    
    def digitalPulse(self, name = None):
        if name is None:
            name = self.digitalChannels[0]
        taskHandle = self.digitalTaskHandles[name]
        DAQmxStartTask(taskHandle)
        data = numpy.array([1], dtype=numpy.uint8)
        DAQmxWriteDigitalLines(taskHandle,1,1,10.0,DAQmx_Val_GroupByChannel,data,None,None)
        time.sleep(0.001)
        data = numpy.array([0], dtype=numpy.uint8)
        DAQmxWriteDigitalLines(taskHandle,1,1,10.0,DAQmx_Val_GroupByChannel,data,None,None)
        DAQmxStopTask(taskHandle)
        return True
    
    def reset(self):
        DAQmxResetDevice(self.inputChannels[0].split('/')[0])
        DAQmxResetDevice(self.outputChannels[0].split('/')[0])