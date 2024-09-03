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




class MC2000B(VisaInstrument):
    """
    QCoDeS driver for the dual channel sourcemeter Keysight B2902B
    """

    def __init__(self, name: str, address: str, baud_rate: int = 115200, timeout: int = 5000, data_bits: int = 8, StopBits: int = 1, Parity: str = 'none', terminator: str = '\r', **kwargs: Any):    
        # supplying the terminator means you don't need to remove it from every response
        super().__init__(name, address, **kwargs)
        
        self.visa_handle.baud_rate = baud_rate
        self.visa_handle.data_bits = data_bits
        self.visa_handle.StopBits = StopBits
        self.visa_handle.Parity = Parity
        self.visa_handle.timeout = timeout

        self.flush()
        

    # The following parameters include all those described in section 2.5 of the manual
    # and are sufficient to drive the instrument at a basic level.
    # System related commands or more complicated commands for arbitrary waveforms are not implemented here.
 
    # Driver parameter to ask identity:
        
        self.add_parameter("identity",
                            label="Identity",
                            get_cmd=self._identity_getter                            
                            )

    # Driver parameter to set the internal frequency:
        
        self.add_parameter("frequency",
                            label="Frequency",                            
                            get_cmd=self._frequency_getter,
                            set_cmd="\rfreq={}",
                            vals=vals.Numbers(min_value=20,max_value=1000),
                            get_parser=str
                            )
        
    # Driver parameter to ask list the available commands
    
        self.add_parameter("commands",
                            label="Commands",
                            get_cmd=self._commands_getter
                            )
    # Driver parameter to set enable
        
        self._enable_map = {'ON': '1', 'OFF':'0'}
                    
        self.add_parameter("enable",
                            label="Enable",
                            get_cmd=self._enable_getter,
                            set_cmd="\renable={}",
                            val_mapping=self._enable_map
                            )
        
    # Driver parameter to set the blade type
    
        self._blade_map = {'MC1F2':'1', 'MC1F10':'2', 'MC1F30':'3', 'MC1F60':'4', 'MC1F100':'5', 'MC1F10HP':'6', 'MC1F2P1o':'7', 'MC1F6P10':'8', 'MC1F10A':'9', 'MC2F330':'10', 'MC2F47':'11', 'MC2F57F':'12', 'MC2F860':'13', 'MC2F5360':'14'}
        
        self.add_parameter("blade",
                           get_cmd =self._blade_getter,
                           set_cmd ="\rblade={}",
                           val_mapping=self._blade_map
                           )
    # Driver parameter to set phase
        
        self.add_parameter("phase",
                           get_cmd=self._phase_getter,
                           set_cmd="\rphase={}",
                           vals=vals.Numbers(min_value=0,max_value=360),
                           get_parser=str
                           )
    # Driver parameter to set reference
        
        self._refinput_map = {'int-outer':'0', 'int-inner':'1', 'ext-outer':'2', 'ext-inner':'3'}
        
        self.add_parameter("refin",
                           get_cmd=self._refin_getter,
                           set_cmd="\rref={}",
                           val_mapping = self._refinput_map
                            )
        
    def _blade_getter(self) -> str:
        """
        get_cmd for blade
        """
        self.flush()
        cmd = "\rblade?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        if resp =='0':
            blade='0'
        elif resp =='1':
            blade='1'
        elif resp =='2':
            blade='2'
        elif resp =='3':
            blade='3'
        elif resp =='4':
            blade='4'
        elif resp =='5':
            blade='5'
        elif resp =='6':
            blade='6'
        elif resp =='7':
            blade='7'
        elif resp =='8':
            blade='8'
        elif resp =='9':
            blade='9'
        elif resp =='10':
            blade='10'
        elif resp =='11':
            blade='11'
        elif resp =='12':
            blade='12'
        elif resp =='13':
            blade='13'
        elif resp =='14':
            blade='14'
        return blade                    

    def _enable_getter(self) -> str:
        """
        get_cmd for enable
        """
        self.flush()
        cmd = "\renable?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        if resp =='1':
            enable='1'
        elif resp=='0':
            enable='0'
        return enable
    
    def _frequency_getter(self) -> str:
        
        self.flush()
        cmd = "\rfreq?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m        
        resp = resp[k:-4]
        return resp
    
    def _identity_getter(self) -> str:
        
        self.flush()
        cmd = "\rid?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        return resp
    def _commands_getter(self) -> str:
        
        self.flush()
        cmd = "\r?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        return resp
    
    def _phase_getter(self) -> str:
        
        self.flush()
        cmd = "\rphase?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        return resp
    
    def _refin_getter(self) -> str:
        
        self.flush()
        cmd = "\rref?"
        resp = self.ask(cmd)
        m = len(cmd)
        k = 34 + m
        resp = resp[k:-4]
        if resp == '0':
            refin = '0'
        elif resp == '1':
            refin = '1'
        elif resp == '2':
            refin = '2'
        elif resp == '3':
            refin = '3'
        return refin
        
    def flush(self) -> None:
        self.visa_handle.flush(pyvisa.constants.VI_READ_BUF_DISCARD | pyvisa.constants.VI_WRITE_BUF_DISCARD)

    # # Driver parameter to set the output of channel A on or off:
        
        # self._outputAchan_map = {'ON': 'ON', 'OFF':'OFF'}
        
        # self.add_parameter("output_A",
                           # label="OutputAChannel",
                           # get_cmd=self._output_Achan_getter,
                           # set_cmd=":OUTP1 {}",
                           # val_mapping=self._outputAchan_map,
                           # )

    # # Driver parameter to set the output of channel B on or off:
    
        # self._outputBchan_map = {'ON': 'ON', 'OFF':'OFF'}
        
        # self.add_parameter("output_B",
                           # label="OutputBChannel",
                           # get_cmd=self._output_Bchan_getter,
                           # set_cmd=":OUTP2 {}",
                           # val_mapping=self._outputBchan_map,
                           # )
    
    # # Driver parameter to set the output mode (current or voltage):
        
        # self._outputmode_map = {'CURR': 'CURR', 'VOLT':'VOLT'}
        
        # self.add_parameter("output_mode",
                           # label="OutputMode",
                           # get_cmd=":OUTP:FUNC:MODE?",
                           # set_cmd=":OUTP:FUNC:MODE {}",
                           # val_mapping=self._outputmode_map,
                           # )
                           
    # # Driver parameter to set the source waiting time ON or OFF (0s):
    
        # self._waittime_map = {'ON': 'ON', 'OFF':'OFF'}
        
        # self.add_parameter("waittime_status",
                           # label="WaitTimeStatus",
                           # get_cmd=self._waittime_getter,
                           # set_cmd=":SOUR:WAIT {}",
                           # val_mapping=self._waittime_map,
                           # )
                           
    # # Driver parameter to set the source waiting time:
    
        # self.add_parameter("waittime",
                            # label="WaitTime",
                            # unit="s",
                            # get_cmd="SOUR:WAIT:OFFS?",
                            # set_cmd="SOUR:WAIT:OFFS {}",
                            # vals=vals.Numbers(min_value=1e-3,max_value=10),
                            # get_parser=float
                            # )
                           
    # # THE BELOW SECTIONS ARE DEDICATED TO VOLTAGE SOURCING AND SENSING
    
    # # Driver parameter to set the enable or disable the auto range:
        
        # self._autorange_map = {'ON': 'ON', 'OFF':'OFF'}
        
        # self.add_parameter("autorange",
                           # label="AutoRange",
                           # get_cmd=self._autorange_getter,
                           # set_cmd=":SOUR:VOLT:RANG:AUTO {}",
                           # val_mapping=self._autorange_map,
                           # )
                           
    # # Driver parameter to set a voltage range to channel A:
        
        # self.add_parameter("voltage_range_A",
                            # label="VoltageRangeA",
                            # unit="V",
                            # get_cmd="SOUR1:VOLT:RANG?",
                            # set_cmd="SOUR1:VOLT:RANG {}",
                            # vals=vals.Numbers(min_value=2e-1,max_value=2e2),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage range to channel B:
        
        # self.add_parameter("voltage_range_B",
                            # label="VoltageRangeB",
                            # unit="V",
                            # get_cmd="SOUR2:VOLT:RANG?",
                            # set_cmd="SOUR2:VOLT:RANG {}",
                            # vals=vals.Numbers(min_value=2e-1,max_value=2e2),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage immediately to channel A:
        
        # self.add_parameter("voltage_source_A",
                            # label="VoltageA",
                            # unit="V",
                            # get_cmd="SOUR1:VOLT?",
                            # set_cmd="SOUR1:VOLT {}",
                            # vals=vals.Numbers(min_value=-2e1,max_value=2e1),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage immediately to channel B:
        
        # self.add_parameter("voltage_source_B",
                            # label="VoltageB",
                            # unit="V",
                            # get_cmd="SOUR2:VOLT?",
                            # set_cmd="SOUR2:VOLT {}",
                            # vals=vals.Numbers(min_value=-2e1,max_value=2e1),
                            # get_parser=float
                            # )
    
    # # Driver parameter to set a voltage limit to channel A (requires auto range ON):
    
        # self.add_parameter("voltage_limit_A",
                            # label="VoltageLimitA",
                            # unit="V",
                            # get_cmd="SENS1:VOLT:RANG:AUTO:LLIM?",
                            # set_cmd="SENS1:VOLT:RANG:AUTO:LLIM {}",
                            # vals=vals.Numbers(min_value=2e-1,max_value=2e2),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage limit to channel B (requires auto range ON):
    
        # self.add_parameter("voltage_limit_B",
                            # label="VoltageLimitB",
                            # unit="V",
                            # get_cmd="SENS2:VOLT:RANG:AUTO:LLIM?",
                            # set_cmd="SENS2:VOLT:RANG:AUTO:LLIM {}",
                            # vals=vals.Numbers(min_value=2e-1,max_value=2e2),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage compliance to channel A:
    
        # self.add_parameter("voltage_compliance_A",
                            # label="VoltageComplianceA",
                            # unit="V",
                            # get_cmd="SENS1:VOLT:PROT?",
                            # set_cmd="SENS1:VOLT:PROT {}",
                            # vals=vals.Numbers(min_value=1e-6,max_value=2e0),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a voltage compliance to channel B:
    
        # self.add_parameter("voltage_compliance_B",
                            # label="VoltageComplianceB",
                            # unit="V",
                            # get_cmd="SENS2:VOLT:PROT?",
                            # set_cmd="SENS2:VOLT:PROT {}",
                            # vals=vals.Numbers(min_value=1e-6,max_value=2e0),
                            # get_parser=float
                            # )
                            
    # # THE BELOW SECTIONS ARE DEDICATED TO VOLTAGE SOURCING AND SENSING
    
    # # Driver parameter to set a current range to channel A:
        
        # self.add_parameter("current_range_A",
                            # label="CurrentRangeA",
                            # unit="A",
                            # get_cmd="SOUR1:CURR:RANG?",
                            # set_cmd="SOUR1:CURR:RANG {}",
                            # vals=vals.Numbers(min_value=1e-9,max_value=3e0),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a current range to channel B:
        
        # self.add_parameter("current_range_B",
                            # label="CurrentRangeB",
                            # unit="A",
                            # get_cmd="SOUR2:CURR:RANG?",
                            # set_cmd="SOUR2:CURR:RANG {}",
                            # vals=vals.Numbers(min_value=1e-9,max_value=3e0),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a current immediately to channel A:
        
        # self.add_parameter("current_source_A",
                            # label="CurrentA",
                            # unit="A",
                            # get_cmd="SOUR1:CURR?",
                            # set_cmd="SOUR1:CURR {}",
                            # vals=vals.Numbers(min_value=-3e0,max_value=3e0),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a current immediately to channel B:
        
        # self.add_parameter("current_source_B",
                            # label="CurrentB",
                            # unit="A",
                            # get_cmd="SOUR2:CURR?",
                            # set_cmd="SOUR2:CURR {}",
                            # vals=vals.Numbers(min_value=-3e1,max_value=3e0),
                            # get_parser=float
                            # )

    # # Driver parameter to set a current limit to the A channel (requires auto range ON):
    
        # self.add_parameter("current_limit_A",
                            # label="CurrentLimitA",
                            # unit="A",
                            # get_cmd="SENS1:CURR:RANG:AUTO:LLIM?",
                            # set_cmd="SENS1:CURR:RANG:AUTO:LLIM {}",
                            # vals=vals.Numbers(min_value=1e-6,max_value=2e0),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a current limit to the A channel (requires auto range ON):
    
        # self.add_parameter("current_limit_B",
                            # label="CurrentLimitB",
                            # unit="A",
                            # get_cmd="SENS2:CURR:RANG:AUTO:LLIM?",
                            # set_cmd="SENS2:CURR:RANG:AUTO:LLIM {}",
                            # vals=vals.Numbers(min_value=1e-6,max_value=2e0),
                            # get_parser=float
                            # )

    # # Driver parameter to set a current compliance to the A channel:
    
        # self.add_parameter("current_compliance_A",
                            # label="CurrentComplianceA",
                            # unit="A",
                            # get_cmd="SENS1:CURR:PROT?",
                            # set_cmd="SENS1:CURR:PROT {}",
                            # vals=vals.Numbers(min_value=1e-8,max_value=1),
                            # get_parser=float
                            # )
                            
    # # Driver parameter to set a current compliance to the A channel:
    
        # self.add_parameter("current_compliance_B",
                            # label="CurrentComplianceB",
                            # unit="A",
                            # get_cmd="SENS2:CURR:PROT?",
                            # set_cmd="SENS2:CURR:PROT {}",
                            # vals=vals.Numbers(min_value=1e-8,max_value=1),
                            # get_parser=float
                            # )
    
    # # Driver parameter to measure current on the A channel:
    
        # self.add_parameter("current_measure_A",
                            # label="CurrentA",
                            # unit="A",
                            # get_cmd="MEAS:CURR? (@1)",
                            # get_parser=float
                            # )

    # # Driver parameter to measure current on the B channel:
    
        # self.add_parameter("current_measure_B",
                            # label="CurrentB",
                            # unit="A",
                            # get_cmd="MEAS:CURR? (@2)",
                            # get_parser=float
                            # )  

    # # Driver parameter to measure voltage on the A channel:
    
        # self.add_parameter("voltage_measure_A",
                            # label="VoltageA",
                            # unit="V",
                            # get_cmd="MEAS:VOLT? (@1)",
                            # get_parser=float
                            # )

    # # Driver parameter to measure voltage on the B channel:
    
        # self.add_parameter("voltage_measure_B",
                            # label="VoltageB",
                            # unit="V",
                            # get_cmd="MEAS:VOLT? (@2)",
                            # get_parser=float
                            # )
    # # Driver parameter to enable or disable the over voltage/current protection on the channel A
    
        # self._protection_map = {'ON': 'ON', 'OFF':'OFF'}
        
        # self.add_parameter("protection_A",
                           # label="ProtectionA",
                           # get_cmd=self._protection_getter,
                           # set_cmd=":OUTP1:PROT {}",
                           # val_mapping=self._protection_map,
                           # )

    # # Driver parameter to enable or disable the over voltage/current protection on the channel A
            
        # self.add_parameter("protection_B",
                           # label="ProtectionB",
                           # get_cmd=self._protection_getter,
                           # set_cmd=":OUTP2:PROT {}",
                           # val_mapping=self._protection_map,
                           # )
                           
    # def _autorange_getter(self) -> str:
        # """
        # get_cmd for the auto range
        # """
        # resp = self.ask("SOUR:VOLT:RANG:AUTO?")
        # if resp =='1':
            # autorange='ON'
        # elif resp=='0':
            # autorange='OFF'

        # return autorange
        
    # def _waittime_getter(self) -> str:
        # """
        # get_cmd for the auto range
        # """
        # resp = self.ask("SOUR:WAIT?")
        # if resp =='1':
            # waittime_status='ON'
        # elif resp=='0':
            # waittime_status='OFF'

        # return waittime_status
    
    # def _output_Achan_getter(self) -> str:
        # """
        # get_cmd for the A output channel
        # """
        # resp = self.ask("OUTP1?")
        # if resp =='1':
            # outputAchan='ON'
        # elif resp=='0':
            # outputAchan='OFF'

        # return outputAchan
        
    # def _output_Bchan_getter(self) -> str:
        # """
        # get_cmd for the B output channel
        # """
        # resp = self.ask("OUTP2?")
        # if resp =='1':
            # outputBchan='ON'
        # elif resp=='0':
            # outputBchan='OFF'

        # return outputBchan

    # def _protectionA_getter(self) -> str:
        # """
        # get_cmd for enable or disable the over voltage/current on the channel A
        # """
        # resp = self.ask("OUTP1:PROT:STAT?")
        # if resp =='1':
            # protectionA ='ON'
        # elif resp=='0':
            # protectionA ='OFF'

        # return protectionA
        
    # def _protectionB_getter(self) -> str:
        # """
        # get_cmd for enable or disable the over voltage/current on the channel B
        # """
        # resp = self.ask("OUTP2:PROT:STAT?")
        # if resp =='1':
            # protectionB ='ON'
        # elif resp=='0':
            # protectionB ='OFF'

        # return protectionB