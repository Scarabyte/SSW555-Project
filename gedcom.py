""" GEDCOM Parsing and Traversing.

This module provides a way of parsing and traversing through a GEDCOM file.

"""
# Standard Library Imports
import re
import json
from collections import OrderedDict
from itertools import ifilter
# Project Imports
import tools

__author__ = "Constantine Davantzis"

regex_line = re.compile(r"(?P<level>[0-9]|[1-9][0-9])\s(?P<xref_ID>@\S+@)?\s?(?P<tag>\S+)\s*(?P<line_value>(.+))?")
"""Regular Expression Object: Compiled regular expression object used for matching GEDCOM lines."""

SUPPORTED_TAGS = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM",
                  "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]
"""A list of tags supported by the project."""


def parse_line(s):
    """ Parse GEDCOM line into dictionary

    :param s: A GEDCOM line
    :type s: str

    :returns: Dictionary of GEDCOM line
    :rtype: dict

    """
    m = regex_line.match(s)
    if not m:
        raise SyntaxError('gedcom_line does not have syntax:'
                          '"level + delim + [optional_xref_ID] + tag + [optional_line_value] + terminator"')
    d = m.groupdict()
    d['isTagSupported'] = d['tag'] in SUPPORTED_TAGS
    d['level'] = int(d['level'])
    return d


class File:

    """GEDCOM File Class

    This class allows a GEDCOM file to be easily traversed.

    :note: this is not a FileHandler, it is an Object representing the GEDCOM file.

    """

    def __init__(self, filename):
        """Initiate GEDCOM File Class

        Initiating the GEDCOM File Class will open the provided filename or file path

        :param filename: A GEDCOM filename or file path.
        :type filename: str

        """
        self.lines = []
        self.__open(filename)

    def __iter__(self):
        """ Return iterator for GEDCOM File Lines.

        This is useful for using the GEDCOM file class with for loops.

        :return: Iterator for self.lines
        :rtype: iterator

        :Example:
            For line in gedcom_file:
                print line

        """
        return iter(self.lines)

    def __getitem__(self, line_number):
        """ Return line based on line number

        This is useful for obtaining a specific line of the gedcom file.

        :note: The first line starts at 0

        :param line_number: The gedcom line number to get
        :type line_number: int

        :return: Line subclass of dictionary defined in this module.
        :rtype: Line

        :Example:
            print gedcom_file[4]

        """
        return self.lines[line_number]

    def __str__(self):
        """ Human representation of the class as a list of dictionaries.

        :note: Although the object returned looks like a list, it is a string.

        :return: String of a list of line dictionaries.
        :rtype: str

        :Examples:
            print str(gedcom_file)  #  This returns a string

            print gedcom_file       #  This returns an instance of the object

        """
        return str(self.lines)

    def __open(self, filename):
        """ Private method to open the GEDCOM File.

        This method is called by __class__.__init__()

        :note: this is used when the class is initiated and should not be used after initiation.

        """
        f = open(filename)
        # Create a list of "Line" objects.
        # The text of the line, the instance of this class, and the line number are passed into each "Line" Object.
        # The instance of this class is passed in so that the line class can make calls to this class.
        self.lines = [Line(line.strip(), self, i) for i, line in enumerate(f)]
        # Refresh the file. Currently this determines which lines are parents and children of one another.
        self.__refresh()
        # Close the file here because we no longer need to read from the file.
        f.close()
    
    def __refresh(self):
        """ Refresh Each Line

        Currently this determines which lines are parents and children of one another.

        :note: Currently this only needs to be called when the class is initiated, however if we want to support adding
        and removing line, this class will need to be called again.

        """
        [d.refresh() for d in self.lines]

    def find(self, key, value):
        """ Finds ALL lines in file that have a matching key and value

        :param key: The key to match
        :type key: str

        :param value: The value to match
        :type value: any object that can be in a dictionary.

        :return: A list of matched lines, as a SubFile
        :rtype: SubFile

        :note: This method returns a SubFile object so that the returned object can continue to use methods defined
        in the File class.

        :Examples:
            print g.find('xref_ID', '@I1@')
            print g.find('tag', 'HUSB')
            print g.find('tag', 'a_value_that_will_never_be_found')

        """
        list_of_matching_lines = filter(lambda d: d.get(key) == value, self.lines)
        # Return a SubFile object so that the returned object can continue to use methods defined in the File class
        return SubFile(list_of_matching_lines)

    def find_one(self, key, value):
        """ Finds FIRST line in file that have a matching key and value

        :param key: The key to match
        :type key: str

        :param value: The value to match
        :type value: any object that can be in a dictionary.

        :return: Line subclass of dictionary defined in this module.
        :rtype: Line

        :note: If a matching line is never found an empty dictionary will be return instead.
        This allows the user to preform __dict__.get("value") on the results (which will return None),
        as apposed to None.get("value") which would cause an exception.
            :return: An empty dictionary
            :rtype: dict

        :Examples:
            print g.find_one('xref_ID', '@I1@')
            print g.find_one('tag', 'HUSB')
            print g.find_one('tag', 'a_value_that_will_never_be_found')

        """
        return next(ifilter(lambda d: d.get(key) == value, self.lines), {})

    @property
    def text(self):
        """ returns the contents of the GEDCOM file as plain text.

        :return: GEDCOM file plain text
        :rtype: str

        :Example:
            print gedcom_file.text

        """
        return "\n".join(line.text for line in self.lines)

    @property
    def individuals(self):
        """ Unique identifiers and names of each of the individuals in order by their unique identifiers.

        :return: An ordered dictionary of individuals
        :rtype: OrderedDict

        :Example:
            print gedcom_file.individuals

        """
        results = []
        for line in self.find("tag", "INDI"):
            xref = line.get("xref_ID")
            name = line.children.find_one("tag", "NAME").get('line_value')
            if xref and name:
                results.append((xref, name.replace("/", "")))
        return OrderedDict(sorted(results, key=lambda x: tools.human_sort(x[0])))

    @property
    def families(self):
        """ unique identifiers and names of the husbands and wives, in order by unique family identifiers.

        :return: An ordered dictionary of families
        :rtype: OrderedDict

        :Example:
            print gedcom_file.families

        """
        results = []
        individuals = self.individuals
        for FAM in self.find("tag", "FAM"):
            fam_xref = FAM.get("xref_ID")
            husb_xref = FAM.children.find_one("tag", "HUSB").get('line_value')
            husb_name = individuals.get(husb_xref)
            wife_xref = FAM.children.find_one("tag", "WIFE").get('line_value')
            wife_name = individuals.get(wife_xref)
            results.append((fam_xref, {"husband": {"xref": husb_xref, "name": husb_name},
                                       "wife": {"xref": wife_xref, "name": wife_name}}))
        return OrderedDict(sorted(results, key=lambda x: tools.human_sort(x[0])))

    @property
    def json(self):
        """ Return pretty print formatted string representing the GEDCOM lines in JSON format.

        :return: Formatted JSON String
        :rtype: str

        :Example:
            print gedcom_file.json

        """
        return json.dumps(self.lines, sort_keys=True, indent=4, separators=(',', ': '))


class SubFile(File):
    """ Class to represent GEDCOM File
    """

    def __init__(self, lines):
        self.lines = lines


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
            return SubFile(map(self.file.lines.__getitem__, self.get('children_line_numbers', [])))
        return None

    @property
    def parent(self):
        """ gets parent

        """
        if self.file:
            return SubFile(map(self.file.lines.__getitem__, self.get('parent_line_numbers', [])))
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


def demo(g):

    # - Demonstrate printing text of file -
    print g.text
    print

    # - Demonstrate printing the line dictionary -
    for line in g:
        print line
    print

    # - Demonstrate printing file as json -
    print g.json
    print
    # - Demonstrate getting a line -
    print g[5]  # - or - g.lines[5]
    print

    # - Demonstrate getting line children and parents "
    print g[0]
    print g[0].children
    print g[0].children[3]
    print g[0].children[3].parent
    print

    # - Demonstrate filtering the list of lines from dictionary value "
    print g.find('xref_ID', '@I1@')

if __name__ == "__main__":
    g = File("Test_Files/GEDCOM.ged")
    #demo(g)
    ##print str(g)
    print type(g.json)

