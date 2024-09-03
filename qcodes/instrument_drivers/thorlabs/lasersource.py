from time import sleep, time
import numpy as np
import pyvisa
import logging

from serial.tools import list_ports, list_ports_common
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



class MCLS(VisaInstrument):
        
    MAX_CURRENTS = {
        1: 38.3,
        2: 97.8,
        3: 51.5,
        4: 21.6,
    }

    def __init__(self, name: str, address: str, baud_rate: int = 115200, timeout: int = 5000, data_bits: int = 8, StopBits: int = 1, Parity: str = 'none', **kwargs: Any):
        super().__init__(name, address, terminator='\r', **kwargs)

        self.visa_handle.baud_rate = baud_rate
        self.visa_handle.data_bits = data_bits
        self.visa_handle.StopBits = StopBits
        self.visa_handle.Parity = Parity
        self.visa_handle.timeout = timeout
        self.flush()
    
    
    # Driver parameter to ask identity:
        
        self.add_parameter("identity",
                            label="Identity",
                            get_cmd=self._identity_getter                          
                            )
                        
    # Driver parameter to ask channel:
        
        self.add_parameter("channel",
                           label="Channel",
                           get_cmd=self._channel_getter,
                           set_cmd=self._channel_setter,
                           vals=vals.Numbers(min_value=1, max_value=4),
                           get_parser=int
                           )
    
    # Driver parameter to ask target:
        
        self.add_parameter("target",
                            label="Target",
                            get_cmd=self._target_getter,
                            set_cmd="target={}",                            
                            vals=vals.Numbers(min_value=20,max_value=30),
                            get_parser=str
                            )
    
    # Driver parameter to ask temp:
        
        self.add_parameter("temp",
                            label="Temp",
                            get_cmd=self._temp_getter,                          
                            vals=vals.Numbers(min_value=20,max_value=30),
                            get_parser=str
                            )

    # Driver parameter to ask current:
    
        self.add_parameter("current",
                           label="Current",
                           get_cmd=self._current_getter,
                           #set_cmd="current={}",
                           set_cmd=self._current_setter,
                           vals=vals.Numbers(min_value=0, max_value=max(self.MAX_CURRENTS.values())),
                           get_parser=float
                           )
     
    # Driver parameter to ask power:
    
        self.add_parameter("power",
                           label="Power",
                           get_cmd=self._power_getter,
                           get_parser=float
                           )
                
    # Driver parameter to ask enable state:
        
        self.add_parameter("enable",
                           label="Enable",
                           get_cmd=self._enable_getter,
                           set_cmd=self._enable_setter,
                           vals=Enum(0, 1),  # Only allow 0 or 1
                           get_parser=int
                           )

    # Driver parameter to ask system state:
    
        self.add_parameter("system",
                           label="System",
                           get_cmd=self._system_getter,
                           set_cmd=self._system_setter,
                           vals=Enum(0, 1),  # Only allow 0 or 1
                           get_parser=int
                           )

    # Driver parameter to ask specifications:
    
        self.add_parameter("specs",
                           label="Specs",
                           get_cmd=self._specs_getter,
                           get_parser=str
                           )

    # Driver parameter to ask step size:
    
        self.add_parameter("step",
                           label="Step",
                           get_cmd=self._step_getter,
                           set_cmd=self._step_setter,
                           get_parser=float
                           )

    # Save settings:
        
        self.add_parameter("save",
                           label="Save",
                           set_cmd="save"
                           )

    # Get status word:
        
        self.add_parameter("statword",
                           label="Status Word",
                           get_cmd=self._statword_getter,
                           get_parser=str
                           )
                           
                           
    def _identity_getter(self) -> str:      
        self.flush()
        cmd = "id?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)        
        return resp
        
    def _channel_getter(self) -> str:      
        self.flush()
        cmd = "channel?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return resp
        self.flush()

    def _channel_setter(self, value: str) -> None:        
        self.flush()
        cmd = f"channel={value}"
        self.write(cmd)
        self.flush()        
        
    def _target_getter(self) -> str:      
        self.flush()
        cmd = "target?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)         
        return resp  
    
    def _temp_getter(self) -> str:       
        self.flush()
        cmd = "temp?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)         
        return resp
    
    def _current_getter(self) -> float:   
        self.flush()
        cmd = "current?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return resp
        self.flush()
     
    def _current_setter(self, value:float) -> int:   
        self.flush()
        try:
            current_channel = int(self.channel.get())
            max_current = self.MAX_CURRENTS[current_channel]
            if value > max_current:
                raise ValueError(f"Current {value} exceeds maximum allowable current for channel {current_channel}.")
            cmd = f"current={value}"
            self.write(cmd)
        except ValueError:
            pass  # it was a string, not an int.
        self.flush()
    
    def _power_getter(self) -> float:  
        self.flush()
        cmd = "power?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return resp
        self.flush()

    def _enable_getter(self) -> int:    
        self.flush()
        cmd = "enable?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return int(resp)

    def _enable_setter(self, value: int) -> None:   
        self.flush()
        cmd = f"enable={value}"
        self.write(cmd)

    def _system_getter(self) -> int:   
        self.flush()
        cmd = "system?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return int(resp)

    def _system_setter(self, value: int) -> None:
        self.flush()
        cmd = f"system={value}"
        self.write(cmd)

    def _specs_getter(self) -> str:
        self.flush()
        cmd = "specs?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return resp

    def _step_getter(self) -> float:
        self.flush()
        cmd = "step?"
        answer = self.ask(cmd)
        resp = self.ask(cmd)
        return resp

    def _step_setter(self, value: float) -> None:
        self.flush()
        cmd = f"step={value}"
        self.write(cmd)

    def _save_settings(self) -> None:
        self.flush()
        cmd = "save"
        self.write(cmd)

    def _statword_getter(self) -> str:
        self.flush()
        cmd = "statword"
        resp = self.ask(cmd)
        return resp

    def flush(self) -> None:
        self.visa_handle.flush(pyvisa.constants.VI_READ_BUF_DISCARD | pyvisa.constants.VI_WRITE_BUF_DISCARD)