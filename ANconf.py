import logging
import io
from os import linesep
from typing import Union
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Common(dict):
    _meta = {}
    _meta_child = {}

    def __init__(self, defaults):
        super().__init__(defaults)
        self.name = ""

    def __setitem__(self, key, value):
        if key not in self._meta.keys():
            logger.error(f"error in {type(self).__name__}")
            raise KeyError(key)
        super().__setitem__(key, value)

    def _set(self, prefix, parameter):
        # used by Load class
        if type(self._meta[prefix]) == str:
            self[prefix] = parameter
            return
        if type(self._meta[prefix]) == list:
            newObj = self._meta_child[prefix](parameter)
            if self.get(prefix) is None:
                self[prefix] = []
            self[prefix].append(newObj)
            return newObj

    def __str__(self):
        return self.name


class BP(Common):
    _meta = {"rating-group": []}

    def __init__(self, name: str):
        super().__init__({})
        self.prefix = "services charging billing-plan"
        self.name = name

    class RG(Common):
        _meta = {"fraud-charging": ""}
        _meta_child = {"fraud-charging": str, }

        def __init__(self, name):
            super().__init__({})
            self.prefix = "rating-group"
            self.name = name

    _meta_child = {"rating-group": RG, }


class SR(Common):
    _meta = {"admin-state": "",
             "priority": "",
             "service-data-flow-id": "",
             "http-rule-group": "",
             "application-rule-group": "",
             "tcp-filter": "",
             "service-activation": "",
             "pcc-rule-name": "",
             "install-default-bearer-packet-filters-on-ue": "",
             "packet-filter": [], }

    _meta_child = {"packet-filter": str, }

    def __init__(self, name: str):
        super().__init__({})
        self.prefix = "service-construct service-rule"
        self.name = name


class RG(Common):
    _meta = {"charging-method": "",
             "quota-id": "",
             "priority": "",
             "admin-state": "",
             "multiplier": "",
             "measurement-method": "",
             "volume-measurement-count": "",
             "volume-measurement-layer": "",
             "tcp-retransmission": "",
             "quota-hold-time": "",
             "reporting-level": "",
             "volume-threshold": "",
             "credit-authorization-event": "",
             "quota-black-list-timer": "",
             "service-type": "",
             "home-subscriber-charging": "",
             "roamer-subscriber-charging": "",
             "cdr-interim-time": "",
             "enable-cdr": "",
             "ocs-response-grace-period": "",
             "service-activation": "",
             "monitor-key-string": "",
             "one-time-redirection": "",
             "requested-unit-value": "",
             "service-rule": [], }

    _meta_child = {"service-rule": str, }

    def __init__(self, name: str):
        super().__init__({})
        self.prefix = "services charging rating-group"
        self.name = name


class MI(Common):
    _meta = {"admin-state": "",
             "rating-group": []}
    _meta_child = {"rating-group": str, }

    def __init__(self, name: str):
        super().__init__({})
        self.prefix = "services metering metering-instance"
        self.name = name


class QF(Common):
    _meta = {"admin-state": "",
             "rate-measurement-units": "",
             "uplink-mbr": "",
             "downlink-mbr": "",
             "uplink-gbr": "",
             "downlink-gbr": "",
             "uplink-max-burst": "",
             "uplink-guaranteed-burst": "",
             "downlink-max-burst": "",
             "downlink-guaranteed-burst": "",
             "gate": "",
             "priority": "",
             "bearer-control": "",
             "service-activation": "",
             "aggregate-qos-flow": "",
             "service-rule": []}

    _meta_child = {"service-rule": str, }

    def __init__(self, name: str):
        super().__init__({})
        self.prefix = "services quality-of-service qos-flow"
        self.name = name

class Config(Common):
    _meta = {"services charging billing-plan": [],
             "services charging rating-group": [],
             "service-construct service-rule": [],
             "services metering metering-instance": [],
             "services quality-of-service qos-flow": []}

    _meta_child = {"services charging billing-plan": BP,
                   "services charging rating-group": RG,
                   "service-construct service-rule": SR,
                   "services metering metering-instance": MI,
                   "services quality-of-service qos-flow": QF}

    def __init__(self, name):
        super().__init__({})

        self.name = name

    def __iadd__(self, other):
        for key in other.keys():
            if self.get(key) is None:
                self[key] = copy.copy(other[key])
            else:
                self[key] += copy.copy(other[key])
        return self

    def __add__(self, other):
        self.__iadd__(other)
        return copy.copy(self)


class Load:
    def __init__(self, fORstr):
        self.config = Config("")

        if type(fORstr) == list:
            # decide that multiple files provided
            for file in fORstr:
                data = self.__fileORstr(file)
                self.config += self._parser(data)
        else:
            data = self.__fileORstr(fORstr)
            self.config = self._parser(data)

    def __fileORstr(self, fORstr):
        if "\n" in fORstr:
            # there is string with "\n", so it's not filePath
            return io.StringIO(fORstr)
        else:
            return io.open(fORstr, "r", encoding="utf-8")

    def __get_level(self, line: str):
        level = 0
        while line[level] == " ":
            level += 1
        return level

    def __get_prefix(self, line: str):
        parameter = line.split()[-1:][0]
        prefixes = line.split()[:-1]
        prefix = " ".join(prefixes)
        return prefix, parameter

    def _parser(self, data):
        config = Config("")
        stack = []
        stack.append(config)
        for line in data:
            level = self.__get_level(line)
            prefix, parameter = self.__get_prefix(line)

            if level > len(stack) - 2:
                newObj = stack[-1]._set(prefix, parameter)
                stack.append(newObj)
                continue

            if level == len(stack) - 2:
                if parameter == "!":
                    continue
                parent = stack[level]
                newObj = parent._set(prefix, parameter)
                stack.pop()
                stack.append(newObj)
                continue

            if level < len(stack) - 2:
                if parameter == "!":
                    stack = stack[:level + 1]
                    continue
        data.close()
        return stack[0]


load = Load


class Dump:
    def __init__(self, obj: Union[object, list, Load], file=False, file_append=False):
        self.output = ""
        if type(obj) in Config("")._meta_child.values():
            self.output += self._printOneObj(obj)
        elif type(obj) == list:
            for i in obj:
                self.output += self._printOneObj(i)
        elif type(obj) == Load:
            lists = [k for k, v in obj.config.items() if type(v) == list]
            for prefix in lists:
                for o in obj.config[prefix]:
                    self.output += self._printOneObj(o)
        else:
            raise ValueError(f"expected input: {Union[object, list, Load]}")

        if file:
            self._dumpToFile(file, file_append)

    def __str__(self):
        return self.output

    def _printOneObj(self, obj, level=0):
        if self.output != "" and level == 0:
            output = linesep
        else:
            output = ""
        output += f"{' ' * level}{obj.prefix} {obj.name}{linesep}"
        # parameters = [p for p, v in obj.items() if v != "" and type(v) != list]
        parameters = [k for k in type(obj)._meta.keys() if obj.get(k) is not None and type(type(obj)._meta[k]) != list]
        if len(parameters) > 0:
            max_param = max([len(param) for param in parameters])
            for param in parameters:
                output += f"{' ' * (level + 1)}{param:{max_param}} {obj[param]}{linesep}"
        list_param = [p for p, v in obj.items() if type(v) == list]
        if len(list_param) > 0:  # recursion protection
            list_param = list_param[0]
            if len(obj[list_param]) != 0:
                list_params = obj[list_param]
                for param in list_params:
                    if type(param) == str:  # recursion exit
                        output += f"{' ' * (level + 1)}{list_param} {param}{linesep}"
                        output += f"{' ' * (level + 1)}!{linesep}"
                    elif hasattr(param, '__dict__'):
                        output += self._printOneObj(param, level + 1)  # recursion
                        output += linesep

        output += f"{' ' * level}!"
        return output

    def _dumpToFile(self, fileName, file_append):
        if file_append:
            with open(fileName, "a", newline="") as f:
                f.write(linesep)
                f.write(self.output)
        else:
            with open(fileName, "w", newline="") as f:
                f.write(self.output)


dump = Dump
show = Dump
