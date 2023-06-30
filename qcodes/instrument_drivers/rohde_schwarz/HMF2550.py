from time import sleep, time
import numpy as np
import pyvisa
import logging
import ctypes  # only for DLL-based instrument
import qcodes as qc
from typing import Any, Callable, TypeVar, Union
from qcodes.utils.validators import Bool, Enum, Ints, MultiType, Numbers

from qcodes.instrument import (
    Instrument,
    VisaInstrument,
    ManualParameter,
    MultiParameter,
    InstrumentChannel,
    InstrumentModule,
)
from qcodes.utils import validators as vals

from qcodes.instrument.parameter import Parameter

class HMF2550(VisaInstrument):
    """
    QCoDeS driver for the function generator HMF2550
    """

    def __init__(self, name: str, address: str, **kwargs: Any):       
        # supplying the terminator means you don't need to remove it from every response
        super().__init__(name, address, terminator='\n', **kwargs)

    # The following parameters include all those described in section 2.4 of the manual
    # and are sufficient to drive the instrument at a basic level.
    # System related commands or more complicated commands for arbitrary waveforms are not implemented here.
    
    # Driver parameter to decide function type:
    
        self._function_map = {'sine': 'SIN', 'square': 'SQU', 'ramp': 'RAMP',
                          'pulse': 'PULS', 'arbitrary': 'ARB'}
        
        
        self.add_parameter("function",
                           label="Function Type",
                           get_cmd="FUNC?",
                           set_cmd="FUNC {}",
                           val_mapping=self._function_map,
                           )

    # Driver parameter to set the output on or off:
        
        self._output_map = {'ON': 'ON', 'OFF':'OFF'}
        
        self.add_parameter("output",
                           label="Output Status",
                           get_cmd="OUTP?",
                           set_cmd="OUTP {}",
                           val_mapping=self._output_map,
                           )
        
    # Driver parameter to set the output load to 50 Ohm or Infinity:
        
        self._output_load_map = {'terminated': 'TERM', 'infinity':'INF'}
        
        self.add_parameter("output_load",
                           label="Output Load",
                           get_cmd="OUTP:LOAD?",
                           set_cmd="OUTP:LOAD {}",
                           val_mapping=self._output_load_map,
                           )
        
    # Driver parameter to set the output polarity to normal or inverted:
        
        self._output_pol_map = {'normal': 'NORM', 'inverted':'INV'}
        
        self.add_parameter("output_polarity",
                           label="Output Polarity",
                           get_cmd="OUTP:POL?",
                           set_cmd="OUTP:POL {}",
                           val_mapping=self._output_pol_map,
                           )       
        
     # Driver parameter to decide function frequency:
         
        self.add_parameter("frequency",
                           label="Frequency",
                           unit="Hz",
                           get_cmd="FREQ?",
                           set_cmd="FREQ {}",
                           vals=Numbers(min_value=1e-5, max_value=1e7),
                           get_parser=float
                           )
     # Driver parameter to decide function period:
         
        self.add_parameter("period",
                           label="Period",
                           unit="s",
                           get_cmd="PER?",
                           set_cmd="PER {}",
                           vals=Numbers(min_value=2e-8, max_value=1e5),
                           get_parser=float
                           )  
        
    # Driver parameter to decide voltage setting units:
        
        self._voltageunit_map = {'dBm': 'DBM', 'V':'VOLT'}
        
        self.add_parameter("voltage_unit",
                           label="Voltage Unit",
                           get_cmd="VOLT:UNIT?",
                           set_cmd="VOLT:UNIT {}",
                           val_mapping=self._voltageunit_map,
                           )
    # Driver parameter to decide function voltage:
         
        self.add_parameter("voltage",
                           label="Voltage",
                           unit="V",
                           get_cmd="VOLT?",
                           set_cmd="VOLT {}",
                           vals=Numbers(min_value=1e-2, max_value=2e1),
                           get_parser=float
                           )

    # Driver parameter to define the high level voltage depending on the amplitude settings:
         
        self.add_parameter("voltage_high",
                           label="Voltage High",
                           unit="V",
                           get_cmd="VOLT:HIGH?",
                           set_cmd="VOLT:HIGH {}",
                           vals=Numbers(min_value=-1e1, max_value=1e1),
                           get_parser=float
                           )
     
    # Driver parameter to define the low level voltage depending on the amplitude settings:
         
        self.add_parameter("voltage_low",
                           label="Voltage Low",
                           unit="V",
                           get_cmd="VOLT:LOW?",
                           set_cmd="VOLT:LOW {}",
                           vals=Numbers(min_value=-1e1, max_value=1e1),
                           get_parser=float
                           )
        
    # Driver parameter to define the offset level voltage depending on the amplitude settings:
         
        self.add_parameter("voltage_offset",
                           label="Voltage Offset",
                           unit="V",
                           get_cmd="VOLT:OFFS?",
                           set_cmd="VOLT:OFFS {}",
                           vals=Numbers(min_value=-1e1, max_value=1e1),
                           get_parser=float
                           )
        
    # Driver parameter to set the duty cycle of the square wave function:
         
        self.add_parameter("square_duty_cycle",
                           label="Square Duty Cycle",
                           unit="%",
                           get_cmd="FUNC:SQU:DCYC?",
                           set_cmd="FUNC:SQU:DCYC {}",
                           vals=Numbers(min_value=20, max_value=80),
                           get_parser=float
                           )

    # Driver parameter to define the high width of the square wave function depending on the frequency settings:
         
        self.add_parameter("square_width_high",
                           label="Square Width High",
                           unit="s",
                           get_cmd="FUNC:SQU:WIDT:HIGH?",
                           set_cmd="FUNC:SQU:WIDT:HIGH {}",
                           vals=Numbers(min_value=1e-8, max_value=8e4),
                           get_parser=float
                           )
        
    # Driver parameter to define the high width of the square wave function depending on the frequency settings:
         
        self.add_parameter("square_width_low",
                           label="Square Width Low",
                           unit="s",
                           get_cmd="FUNC:SQU:WIDT:LOW?",
                           set_cmd="FUNC:SQU:WIDT:LOW {}",
                           vals=Numbers(min_value=1e-8, max_value=8e4),
                           get_parser=float
                           )
        
    # Driver parameter to define the rise time of the ramp function depending on the frequency settings:
         
        self.add_parameter("ramp_time_rise",
                           label="Ramp Rise Time",
                           unit="%",
                           get_cmd="FUNC:RAMP:TIME:RISE?",
                           set_cmd="FUNC:RAMP:TIME:RISE {}",
                           vals=Numbers(min_value=8e-9, max_value=1e5),
                           get_parser=float
                           )

    # Driver parameter to define the fall time of the ramp function depending on the frequency settings:
         
        self.add_parameter("ramp_time_fall",
                           label="Ramp Fall Time",
                           unit="%",
                           get_cmd="FUNC:RAMP:TIME:FALL?",
                           set_cmd="FUNC:RAMP:TIME:FALL {}",
                           vals=Numbers(min_value=8e-9, max_value=1e5),
                           get_parser=float
                           )

    # Driver parameter to set the duty cycle of a pulse function:
         
        self.add_parameter("pulse_duty_cycle",
                           label="Pulse Duty Cycle",
                           unit="%",
                           get_cmd="FUNC:PULS:DCYC?",
                           set_cmd="FUNC:PULS:DCYC {}",
                           vals=Numbers(min_value=1e-1, max_value=9.99e1),
                           get_parser=float
                           )

    # Driver parameter to define the high width of a pulse function depending on the frequency settings:
         
        self.add_parameter("pulse_width_high",
                           label="Pulse Width High",
                           unit="s",
                           get_cmd="FUNC:PULS:WIDT:HIGH?",
                           set_cmd="FUNC:PULS:WIDT:HIGH {}",
                           vals=Numbers(min_value=2e-8, max_value=1e5),
                           get_parser=float
                           )
        
    # Driver parameter to define the high width of a pulse function depending on the frequency settings:
         
        self.add_parameter("pulse_width_low",
                           label="Pulse Width Low",
                           unit="s",
                           get_cmd="FUNC:PULS:WIDT:LOW?",
                           set_cmd="FUNC:PULS:WIDT:LOW {}",
                           vals=Numbers(min_value=2e-8, max_value=1e5),
                           get_parser=float
                           )

    # Driver parameter to define the edge time of the pulse function depending on the frequency settings:
         
        self.add_parameter("pulse_edge_time",
                           label="Pulse Edge Time",
                           unit="s",
                           get_cmd="FUNC:PULS:ETIM?",
                           set_cmd="FUNC:PULS:ETIM {}",
                           vals=Numbers(min_value=8e-9, max_value=5e-7),
                           get_parser=float
                           )


    # Driver parameter to decide a waveform type:
    
        self._waveform_map = {'sine': 'SIN', 'square': 'SQU', 'pramp': 'PRAM', 'nramp': 'NRAM', 'triangle': 'TRI',
                              'wnoise': 'WNO', 'pnoise': 'PNO', 'cardinal': 'CARD', 'exprise': 'EXPR',
                              'expfall': 'EXPF', 'ram': 'RAM'}
        
        self.add_parameter("waveform",
                           label="Waveform Type",
                           get_cmd="FUNC:ARB?",
                           set_cmd="FUNC:ARB {}",
                           val_mapping=self._waveform_map,
                           )
    
    # Here a lot of parameters related to this latest waveforms are missing and should be implemented.
        
        self.connect_message()    
