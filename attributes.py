import logging
from pathlib import Path
import io
from os import linesep
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SR_commands = ["admin-state",
               "priority",
               "service-data-flow-id",
               "tcp-filter",
               "service-activation",
               "pcc-rule-name",
               "install-default-bearer-packet-filters-on-ue",
               "http-rule-group",
               "application-rule-group"
               ]
SR_multiple_comands = ["packet-filter"]
SR_ignored_comands = []
RG_commands = ["charging-method",
               "quota-id",
               "priority",
               "admin-state",
               "multiplier",
               "measurement-method",
               "volume-measurement-count",
               "volume-measurement-layer",
               "tcp-retransmission",
               "quota-hold-time",
               "reporting-level",
               "volume-threshold",
               "credit-authorization-event",
               "quota-black-list-timer",
               "service-type",
               "home-subscriber-charging",
               "roamer-subscriber-charging",
               "enable-cdr",
               "ocs-response-grace-period",
               "service-activation",
               "requested-unit-value",
               "cdr-interim-time",
               "monitor-key-string",
               "one-time-redirection"
               ]
RG_multiple_comands = ["service-rule"]
RG_ignored_comands = []
BP_commands = []
BP_multiple_comands = ["rating-group"]
BR_ignored_comands = ["fraud-charging"]

# ---------------- Generators ----------------
SR_attrs = {k: k.replace("-", "_") for k in SR_commands}
SR_lists = {k: k.replace("-", "_") for k in SR_multiple_comands}
SR_ignors = {k: k.replace("-", "_") for k in SR_ignored_comands}
# SR_attrsR = {v: k for k, v in SR_attrs.items()}
# SR_listsR = {v: k for k, v in SR_lists.items()}
RG_attrs = {k: k.replace("-", "_") for k in RG_commands}
RG_lists = {k: k.replace("-", "_") for k in RG_multiple_comands}
RG_ignors = {k: k.replace("-", "_") for k in RG_ignored_comands}
BP_attrs = {k: k.replace("-", "_") for k in BP_commands}
BP_lists = {k: k.replace("-", "_") for k in BP_multiple_comands}
BP_ignors = {k: k.replace("-", "_") for k in BR_ignored_comands}


class GenObj:
    def __init__(self, topObj=None):
        self.name = ""
        self.keywords = {}
        self.tree_keywords = {"service-construct service-rule": SR,
                              "services charging rating-group": RG,
                              "services charging billing-plan": BP}
        self.list_keywords = {}
        self.ignors_keywords = {}
        self.allKeys = [*self.keywords, *self.tree_keywords, *self.list_keywords, *self.ignors_keywords]
        self.topObj = topObj
        self.closeObj = "!"
        self.end = False

    def __getitem__(self, item):
        if item in self.keywords:
            return getattr(self, self.keywords[item])
        if item in self.tree_keywords:
            return getattr(self, self.tree_keywords[item])
        if item in self.list_keywords:
            return getattr(self, self.list_keywords[item])

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
            newObj.name = self.parameter
            setattr(self, type(newObj).__name__, newObj)
            return newObj

    def _end(self, line):
        line = line.rstrip()
        if line == "!":
            self.end = True


class TopObj(GenObj):
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


class SR(TopObj):
    def __init__(self, topObj):
        super().__init__(topObj)
        self.keywords = SR_attrs
        self.tree_keywords = {}
        self.list_keywords = SR_lists
        self.allKeys = [*self.keywords, *self.tree_keywords, *self.list_keywords]
        # self.keywordsR = SR_attrsR
        # self.list_keywordsR = SR_listsR
        # self.tree_keywordsR = {}


class RG(TopObj):
    def __init__(self, topObj):
        super().__init__(topObj)
        self.keywords = RG_attrs
        self.tree_keywords = {}
        self.list_keywords = RG_lists
        self.allKeys = [*self.keywords, *self.tree_keywords, *self.list_keywords]

class BP(TopObj):
    def __init__(self, topObj):
        super().__init__(topObj)
        self.keywords = {}
        self.tree_keywords = {}
        self.list_keywords = BP_lists
        self.ignors_keywords = BP_ignors
        self.allKeys = [*self.keywords, *self.tree_keywords, *self.list_keywords, *self.ignors_keywords]



class dump:
    def __init__(self, fORstr):
        self.bp = {}
        self.rg = {}
        self.sr = {}
        self.pf = {}
        data = self._fileORstr(fORstr)
        self._parser(data)

    def _fileORstr(self, fORstr):
        if "\n" in fORstr:
            # there is string with "\n", so it's not filePath
            return io.StringIO(fORstr)
        else:
            return io.open(fORstr, "r", encoding="utf-8")

    def _parser(self, data):
        obj = GenObj()
        for line in data:
            # if line in ["\n", "\r\n", "\r"]:
            #     print("conti")
            #     continue
            # print("line", line)
            # if not obj.end:
            obj = obj.set_param(line)
            # print("obj=", obj)
            if not obj.end:
                continue

            if type(obj) == SR:
                self.sr[obj.name] = obj
            elif type(obj) == RG:
                self.rg[obj.name] = obj
            elif type(obj) == BP:
                self.bp[obj.name] = obj
            else:
                raise KeyError(f'unknow type {type(obj).__name__}')
            obj = GenObj()
            # print("obj2=", obj)

        data.close()


