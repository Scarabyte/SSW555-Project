"""
Gedcom classes and functions 

"""

import re

# Pre-Compile Regex for GEDCOM Line.
match_line = re.compile(
    r"(?P<level>[0-9]|[1-9][0-9])\s(?P<xref_ID>@\S+@)?\s?(?P<tag>\S+)\s*(?P<line_value>(.+))?").match

# Declare valid line tags for our project
SUPPORTED_TAGS = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV",
                  "DATE", "HEAD", "TRLR", "NOTE"]


def parse_line(s):
    """Parse GEDCOM line into dictionary

    :param s: The GEDCOM line string to parse.
    :type s: str

    :returns: GEDCOM line dictionary
    :rtype: dict

    """
    m = match_line(s)
    if not m:
        # Raise exception of regex could not match line.
        raise SyntaxError('gedcom_line does not have syntax: "level + delim + [optional_xref_ID] + tag + [optional_line_value] + terminator"')
    d = m.groupdict()
    d["isTagSupported"] = d["tag"] in SUPPORTED_TAGS
    d["level"] = int(d["level"])
    return d


class File:
    """ Class to represent GEDCOM File
    """

    def __init__(self, filename):
        self.__open(filename)

    def __iter__(self):
        return iter(self.lines)

    def __getitem__(self, key):
        return self.lines[key]

    @property
    def text(self):
        return "\n".join(line.text for line in self.lines)

    def __open(self, filename):
        """ Open GEDCOM File """
        f = open(filename)
        # Parse Lines
        self.lines = [Line(line, self, i) for i, line in enumerate(f)]
        self.refresh()  # Must be refreshed initially.

    def refresh(self):
        """ Refresh Each Line
        """
        [d.refresh() for d in self.lines]

    def get(self, key, args):
        return filter(lambda d: d[key] == args, self.lines)


class Line(dict):
    """ Class to represent GEDCOM line. """

    def __init__(self, line_string, file_class=None, line_number=None):
        self.file = file_class
        self.__text = line_string.strip()
        self.update(**parse_line(line_string))
        self.update({"line_number": line_number})
        self.update({"children_line_numbers": [], "parent_line_numbers": []})

    @property
    def text(self):
        """Print Line Text

        :returns: GEDCOM line text
        :rtype: string

        """
        # TODO: have text string show changes made to dictionary
        return self.__text

    @property
    def children(self):
        """ gets a list of GEDCOM lines children in the file

        :returns: list of GEDCOM Lines
        :rtype: list

        """
        if self.file:
            return map(self.file.lines.__getitem__, self.get('children_line_numbers', []))
        return None

    @property
    def parent(self):
        """ gets parent

        """
        if self.file:
            return map(self.file.lines.__getitem__, self.get('parent_line_numbers', []))
        return None

    def refresh(self):
        if self.file:
            # Refresh Children Line Numbers
            self.update({"children_line_numbers": self.__find_children_line_numbers()})
            # Refresh Parent Line Numbers. (Relies on Parent Line Number Being Accurate)
            self.update({"parent_line_numbers": self.__find_parent_line_numbers()})

    def __find_children_line_numbers(self):
        """ get children line numbers """
        results = []
        lines = self.file.lines
        line_number = self.get("line_number")
        if line_number < len(lines) - 1:
            if lines[line_number + 1].get("level") > lines[line_number]["level"]:
                for u in lines[line_number + 1:]:
                    if u["level"] == lines[line_number + 1]["level"]:
                        results.append(u.get('line_number'))
                    if u["level"] > lines[line_number + 1]["level"]:
                        pass
                    if u["level"] < lines[line_number + 1]["level"]:
                        break
        return results

    def __find_parent_line_numbers(self):
        """ get parent line numbers """
        return map(lambda line: line.get("line_number"), filter(lambda line: self["line_number"] in line.get("children_line_numbers",[]), self.file.lines))


def demo():
    g = File("GEDCOM.ged")

    # - Demonstrate printing text of file -
    # print g.text
    # - or -
    # for line in g:
    #   print line.text

    # - Demonstrate printing the line dictionary -
    # print g.lines
    # - or -
    # print list(g)
    # - or -
    # for line in g:
    #    print line

    # - Demonstrate printing file as json -
    # import json
    # print json.dumps(list(g), sort_keys=True, indent=4, separators=(',', ': '))

    # - Demonstrate getting a line -
    # print g[5]
    # - or -
    # print g.lines[5]

    # - Demonstrate that a line item can access the parent file -
    # print  g is g[0].file

    # - Demonstrate getting line children "
    # print g[0]
    # print g[0].children
    # print g[0].children[3].parent

    # - Demonstrate getting a line from dictionary value "
    # print g.get('xref_ID','@I1@')

if __name__ == "__main__":
    demo()

