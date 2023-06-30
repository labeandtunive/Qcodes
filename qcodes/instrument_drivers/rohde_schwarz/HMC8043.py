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

class HMC8043(VisaInstrument):
    """
    QCoDeS driver for the power supply HMC8043
    """

    def __init__(self, name: str, address: str, **kwargs: Any):       
        # supplying the terminator means you don't need to remove it from every response
        super().__init__(name, address, terminator='\n', **kwargs)

    # The following parameters include all those described in section 2.5 of the manual
    # and are sufficient to drive the instrument at a basic level.
    # System related commands or more complicated commands for arbitrary waveforms are not implemented here.
 
    # Driver parameter to ask identity:
        
        self.add_parameter("identity",
                            label="Identity",
                            get_cmd="*IDN?"
                            )

    # Driver parameter to reset the instrument:
        
        self.add_parameter("reset",
                            label="Reset",
                            set_cmd="*RST"
                            )
           
    # Driver parameter to select the output:
    
        self._output_map = {'out1': 'OUT1', 'out2': 'OUT2', 'out3': 'OUT3'}        
        
        self.add_parameter("select_output",
                            label="Output",
                            get_cmd=self._output_parameter_getter,
                            set_cmd="INST:SEL {}",
                            val_mapping=self._output_map,
                            )

    # Driver parameter to select the channel by number.
    # This command and the command above are interchangable:
        
        self.add_parameter("select_channel",
                            label="Channel",
                            get_cmd="INST:NSEL?",
                            set_cmd="INST:NSEL {}",
                            vals=vals.Enum(1, 2, 3),
                            get_parser=int
                            )

    # Driver parameter to set a voltage amplitude:
        
        self.add_parameter("voltage",
                            label="Voltage",
                            unit="V",
                            get_cmd="VOLT?",
                            set_cmd="VOLT {}",
                            vals=vals.Numbers(min_value=0,max_value=3.205e1),
                            get_parser=float
                            )

    # Driver parameter to set the voltage step to go to the next voltage value:
        
        self.add_parameter("voltage_step",
                            label="Voltage Step",
                            unit="V",
                            get_cmd="VOLT:STEP?",
                            set_cmd="VOLT:STEP {}",
                            vals=vals.Numbers(min_value=1e-3,max_value=3.205e1),
                            get_parser=float
                            )

    # Driver parameter to set a current amplitude:
        
        self.add_parameter("current",
                            label="Current",
                            unit="A",
                            get_cmd="CURR?",
                            set_cmd="CURR {}",
                            vals=vals.Numbers(min_value=5e-4,max_value=3),
                            get_parser=float
                            )

    # Driver parameter to set the current step to go to the next current value:
        
        self.add_parameter("current_step",
                            label="Current Step",
                            unit="A",
                            get_cmd="CURR:STEP?",
                            set_cmd="CURR:STEP {}",
                            vals=vals.Numbers(min_value=5e-4,max_value=3),
                            get_parser=float
                            )
        
    # Driver parameter to set the voltage step to go to the next voltage value:
        
        self.add_function("apply",
                            call_cmd="APPL {}"+","+"{}",
                            args=[Numbers(min_value=1e-3,max_value=3.205e1),Numbers(min_value=5e-4,max_value=3)]
                            )
        
    # Driver parameter to set the output on or off (both channel and master):
        
        self._output_map = {'ON': 'ON', 'OFF':'OFF'}
        
        self.add_parameter("output",
                           label="Output Status",
                           get_cmd=self._output_status_getter,
                           set_cmd="OUTP {}",
                           val_mapping=self._output_map,
                           )
        
    # Driver parameter to set the output on or off (only channel):
        
        self._outputchan_map = {'ON': 'ON', 'OFF':'OFF'}
        
        self.add_parameter("output_channel",
                           label="Output Channel",
                           get_cmd=self._output_channel_getter,
                           set_cmd="OUTP:CHAN {}",
                           val_mapping=self._outputchan_map,
                           )

    # Driver parameter to set the output on or off (only master):
        
        self._outputmaster_map = {'ON': 'ON', 'OFF':'OFF'}
        
        self.add_parameter("output_master",
                           label="Output Master",
                           get_cmd=self._output_master_getter,
                           set_cmd="OUTP:MAST {}",
                           val_mapping=self._outputmaster_map,
                           )   
        
    # # Here a lot of parameters are missing and should be implemented.
        
        self.connect_message() 
        
    def _output_parameter_getter(self) -> str:
        """
        get_cmd for the output parameter
        """
        resp = self.ask("INST:SEL?")
        if resp in ['1', '2', '3']:
            outputresp='OUT'+resp

        return outputresp

    def _output_status_getter(self) -> str:
        """
        get_cmd for the output status
        """
        resp = self.ask("OUTP?")
        if resp =='1':
            outputstatus='ON'
        elif resp=='0':
            outputstatus='OFF'

        return outputstatus
    
    def _output_channel_getter(self) -> str:
        """
        get_cmd for the output channel
        """
        resp = self.ask("OUTP:CHAN?")
        if resp =='1':
            outputchannel='ON'
        elif resp=='0':
            outputchannel='OFF'

        return outputchannel
    
    def _output_master_getter(self) -> str:
        """
        get_cmd for the output master
        """
        resp = self.ask("OUTP:MAST?")
        if resp =='1':
            outputmaster='ON'
        elif resp=='0':
            outputmaster='OFF'

        return outputmaster
        
    def voltage_up(self) -> None:
        """
        Steps up the voltage of one voltage step
        """
        self.write('VOLT UP')  
        
    def voltage_down(self) -> None:
        """
        Steps down the voltage of one voltage step
        """
        self.write('VOLT DOWN')  

    def current_up(self) -> None:
        """
        Steps up the current of one current step
        """
        self.write('CURR UP')  
        
    def current_down(self) -> None:
        """
        Steps down the current of one current step
        """
        self.write('CURR DOWN')