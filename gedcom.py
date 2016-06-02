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
        [d.update({"children_line_numbers":self.get_children_ln(d["line_number"])}) for d in self.lines]

    def __iter__(self):
        return iter(self.lines)
    
    def __getitem__(self, key):
        return self.list[key]

    def __open(self,filename):
        f = open(filename)
        self.lines = [Line(line) for line in f]

    def get_children_ln(self,ln):
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

    @property
    def text(self):
        return "\n".join(line.text for line in self.lines)


if __name__ == "__main__":
    """ Parse and print each line of of the GEDCOM.ged file in the same folder as this script """
    g = File("GEDCOM.ged")
    print " ------------ Print Text ------------ "
    print g.text
    print 
    print

    print " ------------ Print Lines Individually ------------ "
    for line in g:
        print line
    print 
    print
    print " ------------ Print Lines Dictionary ------------ "
    import json
    print g.lines == list(g)
    print json.dumps(list(g), sort_keys=True, indent=4, separators=(',', ': '))

    
