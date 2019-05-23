import logging
import io
from os import linesep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# top_sections = ("BP", "MI", "RG", "QF", "SR" )
# top_sec = {"BP" : {}, "MI": {}, "RG": {}, "QF": {}, "SR": {}}
top_keywords = {"service-construct service-rule": "SR",
                "services charging rating-group": "RG",
                "services charging billing-plan": "BP",
                "services quality-of-service qos-flow": "QF",
                "services metering metering-instance": "MI",
                }

#  should be in strict order, for correct dump working
MI_commands_meta = [("admin-state", "m"), ]
MI_multiple_comands = ["rating-group", ]
MI_ignored_comands = []

QF_commands_meta = [("admin-state", "m"),
                    ("rate-measurement-units", "m"),
                    ("uplink-mbr", "m"),
                    ("downlink-mbr", "m"),
                    ("uplink-gbr", "m"),
                    ("downlink-gbr", "m"),
                    ("uplink-max-burst", "m"),
                    ("uplink-guaranteed-burst", "m"),
                    ("downlink-max-burst", "m"),
                    ("downlink-guaranteed-burst", "m"),
                    ("gate", "m"),
                    ("priority", "m"),
                    ("bearer-control", "m"),
                    ("service-activation", "m"),
                    ("aggregate-qos-flow", "m"),
                    ]
QF_multiple_comands = ["service-rule", ]
QF_ignored_comands = []

SR_commands_meta = [("admin-state", "m"),
                    ("priority", "m"),
                    ("service-data-flow-id", "m"),
                    ("http-rule-group", "o"),
                    ("application-rule-group", "o"),
                    ("tcp-filter", "m"),
                    ("service-activation", "m"),
                    ("pcc-rule-name", "pcc"),
                    ("install-default-bearer-packet-filters-on-ue", "m"),
                    ]
SR_multiple_comands = ["packet-filter"]
SR_ignored_comands = []

RG_commands_meta = [("charging-method", "m"),
                    ("quota-id", "m"),
                    ("priority", "m"),
                    ("admin-state", "m"),
                    ("multiplier", "m"),
                    ("measurement-method", "m"),
                    ("volume-measurement-count", "m"),
                    ("volume-measurement-layer", "m"),
                    ("tcp-retransmission", "m"),
                    ("quota-hold-time", "m"),
                    ("reporting-level", "m"),
                    ("volume-threshold", "m"),
                    ("credit-authorization-event", "m"),
                    ("quota-black-list-timer", "m"),
                    ("service-type", "m"),
                    ("home-subscriber-charging", "m"),
                    ("roamer-subscriber-charging", "m"),
                    ("cdr-interim-time", "o"),
                    ("enable-cdr", "m"),
                    ("ocs-response-grace-period", "m"),
                    ("service-activation", "m"),
                    ("monitor-key-string", "pcc"),
                    ("one-time-redirection", "o"),
                    ("requested-unit-value", "m"),
                    ]
RG_multiple_comands = ["service-rule", ]
RG_ignored_comands = []

BP_multiple_comands = ["rating-group", ]
BR_ignored_comands = ["fraud-charging", ]

# ---------------- Generators ----------------

MI_commands = [i[0] for i in MI_commands_meta]
MI_attrs = {k: k.replace("-", "_") for k in MI_commands}
MI_lists = {k: k.replace("-", "_") for k in MI_multiple_comands}
MI_ignors = {k: k.replace("-", "_") for k in MI_ignored_comands}

SR_commands = [i[0] for i in SR_commands_meta]
SR_attrs = {k: k.replace("-", "_") for k in SR_commands}
SR_lists = {k: k.replace("-", "_") for k in SR_multiple_comands}
SR_ignors = {k: k.replace("-", "_") for k in SR_ignored_comands}
# SR_attrsR = {v: k for k, v in SR_attrs.items()}
# SR_listsR = {v: k for k, v in SR_lists.items()}
RG_commands = [i[0] for i in RG_commands_meta]
RG_attrs = {k: k.replace("-", "_") for k in RG_commands}
RG_lists = {k: k.replace("-", "_") for k in RG_multiple_comands}
RG_ignors = {k: k.replace("-", "_") for k in RG_ignored_comands}

BP_commands = []
BP_attrs = {k: k.replace("-", "_") for k in BP_commands}
BP_lists = {k: k.replace("-", "_") for k in BP_multiple_comands}
BP_ignors = {k: k.replace("-", "_") for k in BR_ignored_comands}

QF_commands = [i[0] for i in QF_commands_meta]
QF_attrs = {k: k.replace("-", "_") for k in QF_commands}
QF_lists = {k: k.replace("-", "_") for k in QF_multiple_comands}
QF_ignors = {k: k.replace("-", "_") for k in QF_ignored_comands}

# TODO: redu in better mapping
attrs = {"BP": BP_attrs, "MI": MI_attrs, "QF": QF_attrs, "RG": RG_attrs, "SR": SR_attrs, }
lists = {"BP": BP_lists, "MI": MI_lists, "QF": QF_lists, "RG": RG_lists, "SR": SR_lists, }
# commands = {"BP": BP_commands, "MI": MI_commands, "QF": QF_commands, "RG": RG_commands, "SR": SR_commands, }
ignors = {"BP": BP_ignors, "MI": MI_ignors, "QF": QF_ignors, "RG": RG_ignors, "SR": SR_ignors, }


class Config:
    def __init__(self):
        # TODO: find better (auto) way to set empty attributes
        self.bp = {}
        self.rg = {}
        self.sr = {}
        self.pf = {}
        self.qf = {}
        self.mi = {}


class Section:
    # TODO: redu via collections.MutableMapping
    def __init__(self, topObj=None):
        self.name = "Section"
        self.keywords = {}
        # TODO: move in global scope or redu, same thing in dump class
        self.tree_keywords = {"service-construct service-rule": SR,
                              "services charging rating-group": RG,
                              "services charging billing-plan": BP,
                              "services quality-of-service qos-flow": QF,
                              "services metering metering-instance": MI,
                              }
        self.list_keywords = {}
        self.ignors_keywords = {}
        self.allKeys = {**self.keywords, **self.tree_keywords, **self.list_keywords, **self.ignors_keywords}
        self.topObj = topObj
        self.closeObj = "!"
        self.end = False
        if type(self) != Section:
            self._init_child()

    def __getitem__(self, item):
        return getattr(self, self.allKeys[item])

    def __setitem__(self, key, value):
        if key in self.allKeys:
            setattr(self, self.allKeys[key], value)

    def set_param(self, line):
        self.parameter = line.split()[-1:][0]
        prefixes = line.split()[:-1]
        self.prefix = " ".join(prefixes)
        if self.parameter == "!":
            self._end(line)
            return self
        if self.prefix not in self.allKeys:
            error = f"unknown in {type(self).__name__} command= '{self.prefix}'"
            logger.error(error)
            raise KeyError(error)
        if self.prefix in self.ignors_keywords.keys():
            return self
        if self.prefix in self.keywords.keys():
            setattr(self, self.keywords[self.prefix], self.parameter)
            return self
        if self.prefix in self.tree_keywords.keys():
            newObj = self.tree_keywords[self.prefix](self)
            newObj._init_child()
            newObj.name = self.parameter
            setattr(self, type(newObj).__name__, newObj)
            return newObj

    def _init_child(self):
        # overriding keywords based on created obj
        obj_name = type(self).__name__
        self.keywords = attrs[obj_name]
        self.tree_keywords = {}
        self.list_keywords = lists[obj_name]
        self.ignors_keywords = ignors[obj_name]
        self.allKeys = {**self.keywords, **self.tree_keywords, **self.list_keywords, **self.ignors_keywords}

    def _end(self, line):
        line = line.rstrip()
        if line == "!":
            self.end = True

    def show(self):
        dump(self, False, True)


class TopObj(Section):
    def __init__(self, topObj):
        super().__init__(topObj)
        self.listSep = 2 * " " + "!"

    def set_param(self, line):
        super().set_param(line)
        if self.prefix in self.list_keywords.keys():
            if hasattr(self, self.list_keywords[self.prefix]):
                getattr(self, self.list_keywords[self.prefix]).append(self.parameter)
            else:
                setattr(self, self.list_keywords[self.prefix], [self.parameter])
        return self

    def _end(self, line):
        super()._end(line)
        line = line.rstrip()
        if line == self.listSep:
            pass


# creating namespaces, !!!!!!!!!! ned update, when adding new obj !!!!!!!!!!!!!!
# class SR(TopObj):
#     pass
BP = type("BP", (TopObj,), {})
QF = type("QF", (TopObj,), {})
MI = type("MI", (TopObj,), {})
RG = type("RG", (TopObj,), {})
SR = type("SR", (TopObj,), {})


# for attr in attrs.keys():
#     globals()[attr] = type(attr, (TopObj,), {})


class load(Config):
    def __init__(self, fORstr):
        super().__init__()
        if type(fORstr) == list:
            # decide that multiple files provided
            for file in fORstr:
                data = self._fileORstr(file)
                self._parser(data)
        else:
            data = self._fileORstr(fORstr)
            self._parser(data)

    def _fileORstr(self, fORstr):
        if "\n" in fORstr:
            # there is string with "\n", so it's not filePath
            return io.StringIO(fORstr)
        else:
            return io.open(fORstr, "r", encoding="utf-8")

    def _parser(self, data):
        obj = Section()
        for line in data:
            obj = obj.set_param(line)
            if not obj.end:
                continue

            # TODO: save in SR, RG, BP, QF attribute
            if isinstance(obj, Section):
                service = type(obj).__name__.lower()
                if not hasattr(self, service):
                    setattr(self, service, {})
                getattr(self, service)[obj.name] = obj
            else:
                raise KeyError(f'unknow type {type(obj).__name__}')
            obj = Section()

        data.close()


class dump:
    def __init__(self, obj: object = None, file=False, stdOut=False, file_append=False):
        # with open(file, "rw") as f:
        self.tree_keywordsR = {SR: "service-construct service-rule",
                               RG: "services charging rating-group",
                               BP: "services charging billing-plan",
                               QF: "services quality-of-service qos-flow",
                               MI: "services metering metering-instance"}
        self.output = ""

        if type(obj) in self.tree_keywordsR.keys():
            self._printOneObj(obj, stdOut)
        elif type(obj) == dict:
            for val in obj.values():
                self._printOneObj(val, stdOut)
        elif type(obj) == load:
            for attr in ["bp", "rg", "sr", "qf", "mi"]:
                data = getattr(obj, attr)
                for val in data.values():
                    self._printOneObj(val, stdOut)
        else:
            raise ValueError(f"expected input: {self.tree_keywordsR.keys()}, dict, load")

        if file:
            self._dumpToFile(file, file_append)

    def __str__(self):
        return self.output

    def __repr__(self):
        return self.output

    def _printOneObj(self, obj, stdOut):
        if self.output != "":
            self.output += linesep
        output = f"{self.tree_keywordsR[type(obj)]} {obj.name}{linesep}"
        # NOTE: !!!!!!!!!!!!!!!!!!!!!
        # starting from python3.6 dicts is ordered
        commands = [command for command in obj.keywords.keys() if hasattr(obj, obj.keywords[command])]
        if commands:
            max_keyword = max([len(command) for command in commands])  # for output justification
        else:
            max_keyword = 0
        for command in commands:
            output += f" {command:{max_keyword}} {obj[command]}{linesep}"
        for group in obj.list_keywords.keys():
            if hasattr(obj, obj.list_keywords[group]):
                members = getattr(obj, obj.list_keywords[group])
                for member in members:
                    output += f" {group} {member}{linesep}"
                    # TODO: workaround for BP, need to decide how insert inner objects in a best way
                    if type(obj) == BP and group == "rating-group":
                        output += f"  fraud-charging false{linesep}"
                    output += f" !{linesep}"
        output += f"!"

        if stdOut:
            print(output)
        self.output += output
        # return output

    def _dumpToFile(self, fileName, file_append):
        if file_append:
            with open(fileName, "a", newline="") as f:
                f.write(linesep)
                f.write(self.output)
        else:
            with open(fileName, "w", newline="") as f:
                f.write(self.output)


# alias to dump class
show = dump
