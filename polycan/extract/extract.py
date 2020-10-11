## This program creates a signal abstraction layer which allows the user to
## read CAN signals from many different sources
## Written by Morgan Swanson

from extract import interfaces
import can
import traceback
import pandas as pd
from contextlib import AbstractContextManager

class SignalExtractor(AbstractContextManager):

    def __init__(self, signals=[]):
        self.signals = signals

    def add(self, signal):
        self.signals.append(signal)

    def remove(self, signal):
        self.signals.remove(signal)


class CanSignalExtractor(SignalExtractor):
    """
    This class interfaces with the can python library.
    It still needs to be properly integrated.
    It must return a pandas dataframe in the same format
    as the CSVSignalExtractor.
    """
    def __init__(self, signals=[]):
        super().__init__(signals)

    def __enter__(self):
        self._config = interfaces.slcan_config()
        self._bus = interfaces.can_int(self._config)
        self._update_filters()
        self._listener = can.Logger('log.log')
        return self

    def _update_filters(self):
        self._bus.set_filters(
            [{"can_id": int(s), "can_mask": 0x7FF, "extended": False}
             for s in self.signals]
        )

    def add(self, signal):
        super().add(signal)
        self._update_filters()

    def remove(self, signal):
        super().remove(signal)
        self._update_filters()

    def extract(self):
        return pd.dataframe([msg for msg in bus])

    def __exit__(self, exc_type, exc_value, tb):
        self._listener.stop()
        self._bus.shutdown()
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True

class CSVFileExtractor(SignalExtractor):

    def __init__(self, path):
        super().__init__([])
        self._path = path

    def __enter__(self):
        self._data = pd.read_csv(self._path, dtype=str)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True

    def extract(self):
        return self._data

    def __str__(self):
        return str(self._data)
