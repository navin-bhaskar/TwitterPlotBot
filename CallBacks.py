

"""
This files should contain all the callback functions.
In this file you define the function that gets a data
and returns it in int or float format.
"""

import mraa
import pyupm_grove

def getTemperature():
    temp = pyupm_grove.GroveTemp(1)
    return temp.value()

def getPotVltg():
    reading = mraa.Aio(0)
    vltg = (reading.read()/1024.0)*5  # swicth is towards 5v
    return vltg


callbacks = [
    # The data item name   The callback func    The color in the plot for this item
    [   'Temperature',      getTemperature,                "#FF2050"],
    [   'Pot vltg',         getPotVltg,                    "#2F3055"],
    
    
    ]
