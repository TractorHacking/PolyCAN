class PgnParameter:
    def __init__(self, start_pos='', length='', description='', spn=0, value=0):
        self.__start_pos = start_pos
        self.__length = length
        self.__description = description
        self.__spn = spn
        self.__value = value  
    @property
    def start_pos(self):
        return self.__start_pos
    @property
    def length(self):
        return self.__length
    @property
    def description(self):
        return self.__description
    @property
    def spn(self):
        return self.__spn
    @property
    def value(self):
        return self.__value
    @start_pos.setter
    def start_pos(self, start_pos):
        self.__start_pos = start_pos
    @length.setter
    def length(self, l):
        self.__length = l
    @description.setter
    def description(self, descr):
        self.__description = descr
    @spn.setter
    def spn(self, spn):
        self.__spn = spn
    @value.setter
    def value(self, val):
        self.__value = val

    @staticmethod
    def from_dict(d):
        res = PgnParameter(d['start_pos'], d['length'], d['param_name'])
        return res
    def compute_value(self, data):
        res = 0
        
class Pgn:
    def __init__(self, pgn, data_len=0, dflt_prty=0, dp=0, edp=0, \
    pdu_format=0, pdu_specific=0, name='', descr=''):
        self.__pgn = pgn
        self.__data_length = data_len
        self.__default_priority = dflt_prty
        self.__dp = dp
        self.__edp = edp
        self.__pdu_format = pdu_format
        self.__pdu_specific = pdu_specific
        self.__name = name
        self.__description = descr
        self.__parameters = []
    @property
    def pgn(self):
        return self.__pgn
    @property
    def data_length(self):
        return self.__data_length
    @property
    def default_priority(self):
        return self.__default_priority
    @property
    def dp(self):
        return self.__dp
    @property
    def edp(self):
        return self.__edp
    @property
    def pdu_format(self):
        return self.__pdu_format
    @property
    def pdu_specific(self):
        return self.__pdu_specific
    @property
    def name(self):
        return self.__name
    @property
    def description(self):
        return self.__description
    @property
    def parameters(self):
        return self.__parameters
    @data_length.setter
    def data_length(self, data_length):
        self.__data_length = data_length
    @default_priority.setter
    def default_priority(self, default_priority):
        self.__default_priority = default_priority
    @dp.setter
    def dp(self, dp):
        self.__dp = dp
    @edp.setter
    def edp(self, edp):
        self.__edp = edp
    @pdu_format.setter
    def pdu_format(self, pdu_format):
        self.__pdu_format = pdu_format
    @pdu_specific.setter
    def pdu_specific(self, pdu_specific):
        self.__pdu_specific = pdu_specific
    @name.setter
    def name(self, name):
        self.__name = name
    @description.setter
    def description(self, description):
        self.__description = description
    @parameters.setter
    def parameters(self, parameters):
        self.__parameters = parameters
    @staticmethod
    def from_dict(d):
        res = Pgn(d['pgn'], d['data_length'], d['default_priority'], \
            d['dp'], d['edp'], d['pdu_format'], d['pdu_specific'], \
            d['name'], d['description'])
        return res
