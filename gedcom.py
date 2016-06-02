"""
Gedcom classes and functions 

"""

import re 
from datetime import datetime

#Pre-Compile Regex for GEDCOM Line.
match_line = re.compile(r"(?P<level>[0-9]|[1-9][0-9])\s(?P<xref_ID>@\S+@)?\s?(?P<tag>\S+)\s*(?P<line_value>(.+))?").match

#Declare valid line tags for our project
SUPPORTED_TAGS = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]


def parse_date(date_string):
    """
    """
    #not tested
    return datetime.strptime(date_string, '%d %b %Y')


class Line(dict):
    """ Class to represent GEDCOM line. """
    def __init__(self, line):
        self.__text = line.strip()
        self.update(**self._parse(line))

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
        return map(self.file.__getitem__, self.get('children_line_numbers',[]))

    @staticmethod
    def _parse(line):
        """Parse GEDCOM line into dictionary

        :param s: The GEDCOM line string to parse.
        :type s: str

        :returns: GEDCOM line dictionary
        :rtype: dict

        """
        m = match_line(line)
        if not m:
            # Raise exception of regex could not match line.
            raise SyntaxError('gedcom_line does not have syntax: "level + delim + [optional_xref_ID] + tag + [optional_line_value] + terminator"')
        d = m.groupdict() 
        d["isTagSupported"] = d["tag"] in SUPPORTED_TAGS
        d["level"] = int(d["level"])
        return d


class File():
    """ Class to represent GEDCOM File
    """

    def __init__(self,filename):
        self.__open(filename)
        # Add line number to dictionaries
        [d.update({"line_number":i}) for i,d in enumerate(self.lines)]
        # Add children line numbers to dictonaries
        [d.update({"children_line_numbers":self.__get_children_ln(d["line_number"])}) for d in self.lines]
        # Link back to this class
        for d in self.lines:
            d.file = self

    def __iter__(self):
        return iter(self.lines)
    
    def __getitem__(self, key):
        return self.lines[key]

    def __open(self,filename):
        """ Open GEDCOM File """
        f = open(filename)
        self.lines = [Line(line) for line in f]

    def __get_children_ln(self,ln):
        """ get children line numbers """
        results = []
        if ln < len(self.lines)-1:
            if self.lines[ln+1].get("level") > self.lines[ln]["level"]:
                for u in self.lines[ln+1:]:
                    if u["level"] == self.lines[ln+1]["level"]:
                        results.append(u.get('line_number'))
                    if u["level"] > self.lines[ln+1]["level"]:
                        pass
                    if u["level"] < self.lines[ln+1]["level"]:
                        break
        return results

    def __get_parent_ln(self,ln):
        """ get parent line numbers """
        # this method needs to be completed 
        pass
    @property
    def text(self):
        return "\n".join(line.text for line in self.lines)

    def get(self, key, args):
        return filter(lambda d: d[key] == args, self.lines)

if __name__ == "__main__":
    """ Parse GEDCOM.ged """
   
    g = File("GEDCOM.ged")

    # - Demonstrate printing text of file -
    #print g.text
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

    # - Demonstrate getting a line from dictionary value "
    # print g.get('xref_ID','@I1@')

