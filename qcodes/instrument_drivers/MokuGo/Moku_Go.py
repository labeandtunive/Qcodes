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

class Moku_go(VisaInstrument):
   def __init__(self, name: str, address: str, **kwargs: Any):
        super().__init__(name, address, terminator='\n', **kwargs)
        self.add_parameter("identity",
                            label="Identity",
                            get_cmd="*IDN?"
                           )
        self.add_parameter("reset",
                            label="Reset",
                            set_cmd="*RST"
                            )
        self.add_parameter("clear",
                            label="Clear",
                            set_cmd="*CLS"
                            )
        self.add_parameter("Oscilloscope_range",
                            label="range",
                            get_cmd="OSC:TIMEBASE:RANGE?",
                            set_cmd="OSC:TIMEBASE:RANGE {}",
                            vals=vals.Numbers(min_value=1e-3, max_value=1e9),
                            get_parser=float
                            )
        self._mode_map = {'AUTO': 'AUTO', 'NORMAL': 'NORMAL', 'SINGLE':'SINGLE'}
        
        self.add_parameter("Oscilloscope_data",
                            label="Trigger",
                            get_cmd="OSC:DATA?",
                            vals=vals.Numbers(min_value=1e-3, max_value=1e9),
                            get_parser=float
                            )
        self.add_parameter("ch1_scale",
                            label="ch1_scale",
                            get_cmd="OSC:CH1:SCAL?",
                            set_cmd="OSC:CH1:SCAL {}",
                            vals=vals.Numbers(min_value=1e-3, max_value=1e9),
                            get_parser=float
                            )
        self.add_parameter("Oscilloscope_mode",
                            label="Trigger",
                            get_cmd="OSC:TRIG:MODE?",
                            set_cmd="OSC:TRIG:MODE {}",
                            val_mapping=self._mode_map,
                            )                            


                            
# OSC:CH1:SCAL <value> - Set the vertical scale for channel 1.
# OSC:CH1:SCAL? - Query the vertical scale for channel 1.
# OSC:DATA? - Query the oscilloscope data.
# Waveform Generator Commands
# WGEN:FUNC <function> - Set the waveform type (e.g., SINE, SQUARE).
# WGEN:FUNC? - Query the waveform type.
# WGEN:FREQ <value> - Set the frequency of the waveform.
# WGEN:FREQ? - Query the frequency of the waveform.
# WGEN:VOLT <value> - Set the output voltage.
# WGEN:VOLT? - Query the output voltage.
# WGEN:OUTP <state> - Enable or disable the waveform output.
# Spectrum Analyzer Commands
# SPEC:FREQ:SPAN <value> - Set the frequency span.
# SPEC:FREQ:SPAN? - Query the frequency span.
# SPEC:FREQ:CENT <value> - Set the center frequency.
# SPEC:FREQ:CENT? - Query the center frequency.
# SPEC:AMPL:SCAL <value> - Set the amplitude scale.
# SPEC:AMPL:SCAL? - Query the amplitude scale.
# SPEC:DATA? - Query the spectrum analyzer data.
# Data Acquisition Commands
# DATA:ACQ:START - Start data acquisition.
# DATA:ACQ:STOP - Stop data acquisition.
# DATA:ACQ:STAT? - Query the status of data acquisition.
# DATA:TRANSFER? - Transfer the acquired data.
# Example Usage
# TRIG:MODE <mode> - Imposta la modalità di trigger (es. AUTO, NORMAL, SINGLE).

# AUTO - L'oscilloscopio acquisisce continuamente senza attendere un evento di trigger.
# NORMAL - L'oscilloscopio acquisisce solo quando si verifica un evento di trigger.
# SINGLE - L'oscilloscopio acquisisce un singolo evento di trigger e poi si ferma.
# TRIG:MODE AUTO
# TRIG:MODE? - Interroga la modalità di trigger.

# TRIG:MODE?
# TRIG:SOURCE <source> - Imposta la sorgente di trigger (es. CH1, CH2, EXT).

# CH1 - Il trigger è basato sul segnale del canale 1.
# CH2 - Il trigger è basato sul segnale del canale 2.
# EXT - Il trigger è basato su un segnale esterno.
# TRIG:SOURCE CH1
# TRIG:SOURCE? - Interroga la sorgente di trigger.

# TRIG:SOURCE?
# TRIG:LEVEL <value> - Imposta il livello di trigger (es. in volt).

# TRIG:LEVEL 0.5
# TRIG:LEVEL? - Interroga il livello di trigger.

# TRIG:LEVEL?
# TRIG:SLOPE <slope> - Imposta la pendenza del trigger (es. RISE, FALL).

# RISE - Il trigger avviene su un fronte di salita.
# FALL - Il trigger avviene su un fronte di discesa.
# TRIG:SLOPE RISE
# TRIG:SLOPE? - Interroga la pendenza del trigger.

# TRIG:SLOPE?