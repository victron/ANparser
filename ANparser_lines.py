import logging
from ANconf_ import SR_attrs, SR, roots


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Line:
    def __init__(self, l: str):
        self.line = l
        self.level = 0
        self.section = False


    def _get_level(self) -> int:
        """
        get level of line, means how many spaces before command
        :return: int
        """
        while self.line[self.level] == " ":
            self.level += 1
        return self.level

    def parse(self, root=None) -> object:
        level = self._get_level()
        if level > 0:
            if self.line[self.level] == "!":
                return LineEnd(self.line)
            return LineCommand(self.line).parse(root)
        if self.line[level] == "!":
            return LineEnd(self.line)
        self.section = True
        return LineRoot(self.line).parse()



class LineRoot(Line):
    def __init__(self, line):
        super().__init__(line)
        self.parameter = self.line.split(" ")[-1:]
        self.prefixes = self.line.strip().strip().split(" ")[:-1]
        self.prefix = " ".join(self.prefixes)

    def parse(self, root=None):
        # prefix_level = (self.prefix, self.level)
        prefix_level = self.prefix
        if root is None:
            if prefix_level not in roots:
                logger.warning(f"unknown command= {self.prefix}")
                return None
            return roots[prefix_level](self.parameter)          # redo
        else:
            root.set_param(self.line)
            return root




class LineCommand(Line):
    def __init__(self, line: str):
        super().__init__(line)
        self.level = self._get_level()
        self.parameter = self.line.split(" ")[-1:]
        self.prefix = self.line.split(" ")[self.level+1:-1]

    def parse(self, root) -> object:
        # line = self.line.strip()
        # lroot = LineRoot(line, root)
        # lroot.level = self.level
        # return lroot.parse(root)
        root.set_param(self.line)
        return root

    # def parse(self):
        



class LineEnd(Line):
    def __init__(self, line):
        super().__init__(line)
        self.level = self._get_level()
        self.name = "end"






commands = {("service-construct service-rule", 0): SR,}


#
# class File:
#     def __init__(self):
#
#

