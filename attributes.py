import logging
from typing import IO, AnyStr, Union
from pathlib import Path
from os import linesep

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SR_commands = ["admin-state",
               "priority",
               "service-data-flow-id",
               "tcp-filter",
               "service-activation",
               "pcc-rule-name",
               "install-default-bearer-packet-filters-on-ue",
               "http-rule-group"
               ]
SR_multiple_comands = ["packet-filter"]
SR_attrs = {k: k.replace("-", "_") for k in SR_commands}
SR_lists = {k: k.replace("-", "_") for k in SR_multiple_comands}
# SR_attrsR = {v: k for k, v in SR_attrs.items()}
# SR_listsR = {v: k for k, v in SR_lists.items()}



# class SR:
#     def __init__(self, name):
#         self.name = name
#         self.section = True
#         self.keywords = SR_attrs
#
#     def set_param(self, line):
#         self.parameter = line.split(" ")[-1:]
#         self.prefixes = line.strip().strip().split(" ")[:-1]
#         self.prefix = " ".join(self.prefixes).strip()
#         print("keys=", self.keywords)
#         if self.prefix not in self.keywords.keys():
#             logger.warning(f"unknown in SR command= '{self.prefix}'")
#             return None
#         setattr(self, self.keywords[self.prefix], self.parameter)
#         return self
#
# #     TODO: put inside list of commands
# # TODO: set parameters via method





# roots = {"service-construct service-rule": SR}



class GenObj:
    def __init__(self, topObj = None):
        self.name = ""
        self.keywords = {}
        self.tree_keywords = {"service-construct service-rule": SR}
        self.list_keywords = {}
        self.allKeys = [*self.keywords, *self.tree_keywords, *self.list_keywords]
        # self.keywordsR = {}
        # self.tree_keywordsR = {SR: "service-construct service-rule"}
        # self.list_keywordsR = {}
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
        if self.prefix in self.keywords.keys():
            setattr(self, self.keywords[self.prefix], self.parameter)
            return self
        if self.prefix in self.tree_keywords.keys():
            newObj = self.tree_keywords[self.prefix](self)
            newObj.name = self.parameter
            setattr(self, type(newObj).__name__, newObj)
            return newObj

    def _end(self, line):
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


FilePathOrBuffer = Union[str, Path, IO[AnyStr]]

class Parser:
    def __init__(self, file: FilePathOrBuffer):
        self.sr = {}
        self.rg = {}
        self.pf = {}
        self._parser(file)



    def _parser(self, file: FilePathOrBuffer):
        obj = GenObj()
        for line in file.split('\n'):
            if not obj.end:
                obj = obj.set_param(line)
            else:
                t = type(obj).__name__
                if t == "SR":
                    self.sr[obj.name] = obj
                else:
                    raise KeyError(f'unknow type {type(obj).__name__}')
                obj = GenObj()



