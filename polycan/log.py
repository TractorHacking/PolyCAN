import collections
from tqdm import tqdm
from tabulate import tabulate

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
    def compute_value(self):
        res = 0
        return res

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

class LogEntry:

    def __init__(self, time=0, pgn=0, priority=0, source=0, \
    dest=0, data=''):
        self.__time = time
        self.__pgn = pgn
        self.__prty = priority
        self.__src = source
        self.__dest = dest
        self.__data = data
        self.__filtered = False
    @property
    def time(self):
        return self.__time
    @property
    def pgn(self):
        return self.__pgn
    @property
    def prty(self):
        return self.__prty
    @property
    def src(self):
        return self.__src
    @property
    def dest(self):
        return self.__dest
    @property
    def data(self):
        return self.__data
    @property
    def filtered(self):
        return self.__filtered

    @time.setter
    def time(self, time):
        self.__time = time
    @pgn.setter
    def pgn(self, pgn):
        self.__pgn = pgn
    @prty.setter
    def prty(self, prty):
        self.__prty = prty
    @src.setter
    def src(self, src):
        self.__src = src
    @dest.setter
    def dest(self, dest):
        self.__dest = dest
    @data.setter
    def data(self, data):
        self.__data = data
    @filtered.setter
    def filtered(self, b):
        self.__filtered = b

    def __str__(self):
        return "T: {0.time!r} PGN: {0.pgn!r} Priority: {0.priority!r} \
        Src: {0.source!r} Dest: {0.dest!r} Data: {0.data!r}" \
        .format(self)

    def __eq__(self, other):
        assert isinstance(other, LogEntry)
        return self.pgn == other.pgn and self.prty == other.prty \
            and self.src == other.src and self.dest== \
                other.dest and self.data == other.data

    def to_dict(self):
        res = {}
        res['time'] = self.time
        res['pgn'] = self.pgn
        res['priority'] = self.prty
        res['source'] = self.src
        res['destination'] = self.dest
        res['data'] = self.data
        return res

    @staticmethod
    def from_dict(source):
        e = LogEntry(source['time'], source['pgn'], source['priority'], \
        source['source'], source['destination'], source['data'])
        return e

class Log:
    def __init__(self, name, model, data=None, sortkey=None, filterkey=None):
        self.__sortkey = sortkey
        self.__filtkey = filterkey

        self.name = name
        self.model = model
        self.size = 0
        if data is None:
            self.__data = []
        elif ((isinstance(data, list)) and (len(data) > 0)) and \
            (isinstance(data[0], LogEntry)):
            self.__data = data
        else:
            self.__data = []
        self.__filtered_data = []

    @property
    def sortkey(self):
        return self.__sortkey

    @property
    def filtkey(self):
        return self.__filtkey
    @property
    def name(self):
        return self.__name
    @property
    def model(self):
        return self.__model
    @property
    def data(self):
        return self.__data
    @property
    def filtered_data(self):
        return self.__filtered_data
 
    @sortkey.setter 
    def sortkey(self, key):
        assert hasattr(key, "__call__")
        self.__sortkey = key

    @filtkey.setter 
    def filtkey(self, filt):
        assert hasattr(filt, "__call__")
        self.__filtkey = filt

    @name.setter
    def name(self, x):
        self.__name = x
    @model.setter
    def model(self, m):
        self.__model = m

    def __getitem__(self, entry):
        assert entry < len(self.__data), "Number out of bounds"
        return self.__data[entry]

    def __len__(self):
        return len(self.__data)

    def __contains__(self, x):
        return

    def __iter__(self):
        return iter(self.__data)

    def __reversed__(self):
        return reversed(self.__data)

    def add(self, value):
        assert isinstance(value, LogEntry)
        self.__data.append(value)

    def sort_by(self):
        res = {}
        for e in self:
            if not self.sortkey(e) in res:
                res[self.sortkey(e)] = []
            res[self.sortkey(e)].append(e)
        res = sorted(res.items())
        self.__data = []
        for x in res:
            self.__data = self.__data + x[1]

    def sort(self, sortkey):
        self.sortkey = sortkey
        self.sort_by()

    def apply_filter(self, filterkey):
        self.filtkey = filterkey
        for x in self:
            if not filterkey(x):
                x.filtered = True
                if not (x in self.filtered_data):
                    self.filtered_data.append(x);                

    def filter_by_pgn(self, pgn):
        self.apply_filter(lambda x: x.pgn == pgn)
    def filter_by_time(self, start, end):
        self.apply_filter(lambda x: x.time >= start and x.time <= end)
    def filter_by_src(self, src):
        self.apply_filter(lambda x: x.src ==src)
    def filter_by_dest(self, dest):
        self.apply_filter(lambda x: x.dest == dest)
    def filter_unique_entries(self):
        uniq_dict = {}
        for e in self:
            if not e.filtered:
                if not e.pgn in uniq_dict:
                    uniq_dict[e.pgn] = []
                    uniq_dict[e.pgn].append(e)
                elif not e in uniq_dict[e.pgn]:
                    uniq_dict[e.pgn].append(e)  
                else:
                    e.filtered = True
                    self.filtered_data.append(e);                

    def remove_filters(self):
        for x in self.__filtered_data:
            x.filtered = False
        self.__filtered_data = []

    def display(self, known):
        table = []
        for e in self:
            if not e.filtered:
                table_entry = [e.time, e.pgn, e.prty, e.src, e.dest]
                if e.pgn in known:
                    table_entry.append(known[e.pgn].name)
                else:
                    table_entry.append("Unknown")
                table_entry.append(e.data)
                table.append(table_entry)
        print("")
        print(tabulate(table, 
            headers= ["time","pgn", "prty", "src", "dest", "description", "data" ], \
            showindex = True, 
            tablefmt = "pipe"))
        print("")  
