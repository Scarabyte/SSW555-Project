""" GEDCOM Parsing and Traversing.

This module provides a way of parsing and traversing through a GEDCOM file.

"""
# Standard Library Imports
import json
import re
from itertools import ifilter, imap
import sys

# Project Imports
import tag
import tools


__author__ = "Constantine Davantzis"

gedcom_line_regex = re.compile(r"(?P<level>[0-9]|[1-9][0-9])\s(?P<xref_ID>@\S+@)?\s?(?P<tag>\S+)\s*(?P<line_value>(.+))?")
"""Regular Expression Object: Compiled regular expression object used for matching GEDCOM lines."""

SUPPORTED_TAGS = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM",
                  "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]
"""A list of tags supported by the project."""


def parse_line(gedcom_line_str):
    """ Parse GEDCOM line into dictionary

    :param gedcom_line_str: A GEDCOM line
    :type gedcom_line_str: str

    :returns: Dictionary of GEDCOM line
    :rtype: dict

    """
    gedcom_line_matches_format = gedcom_line_regex.match(gedcom_line_str)
    if not gedcom_line_matches_format:
        raise SyntaxError('gedcom_line "{0}" does not have syntax '.format(gedcom_line_str) +
                          '"level + delim + [optional_xref_ID] + tag + [optional_line_value] + terminator"')
    gedcom_line_dict = gedcom_line_matches_format.groupdict()
    gedcom_line_dict['isTagSupported'] = gedcom_line_dict['tag'] in SUPPORTED_TAGS
    gedcom_line_dict['level'] = int(gedcom_line_dict['level'])
    return gedcom_line_dict


class File(object):

    """GEDCOM File Class

    A representation of a GEDCOM file as a list of lines.
    This class allows a GEDCOM file to be easily traversed.

    :note: this is not a FileHandler, it is an Object representing the GEDCOM file.

    """

    def __init__(self):
        """Initiate GEDCOM File Class

        """
        self.lines = []

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

    def read_file(self, filename):
        """Method to read to read in file from filename or file path

            :param filename: A GEDCOM filename or file path.
            :type filename: str

        """
        f = open(filename)
        # Create a list of "Line" objects.
        # The text of the line, the instance of this class, and the line number are passed into each "Line" Object.
        # The instance of this class is passed in so that the line class can make calls to this class.
        self.lines = [Line(line.strip(), self, i) for i, line in enumerate(filter(str.strip, f))]
        # Refresh the file. Currently this determines which lines are parents and children of one another.
        self.__refresh()
        # Close the file here because we no longer need to read from the file.
        f.close()
    
    def __refresh(self):
        """ Refresh Each Line

        Currently this determines which lines are parents and children of one another.

        :note: Currently this only needs to be called when the class is initiated, however
        if we want to support adding and removing line, this class will need to be called again.

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


        :Examples:
            print g.find_one('xref_ID', '@I1@')
            print g.find_one('tag', 'HUSB')
            print g.find_one('tag', 'a_value_that_will_never_be_found')

        """
        return next(ifilter(lambda d: d.get(key) == value, self.lines), None)

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
    def json(self):
        """ returns the contents of the GEDCOM file as as pretty printed JSON structure.

        :return: Formatted JSON String
        :rtype: str

        :Example:
            print gedcom_file.json

        """
        return json.dumps(self.lines, sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def individuals(self):
        return [tag.Individual(line) for line in self.find("tag", "INDI")]

    @property
    def families(self):
        return [tag.Family(line) for line in self.find("tag", "FAM")]

    @property
    def dates(self):
        return [tag.Date(line) for line in self.find("tag", "DATE")]





class SubFile(File):
    """GEDCOM SubFile Class

    :warning: This object should only be called on a list of objects that were initiated by the File class,
    this is due to the line objects having access the the rest of the file, and there line numbers updated.

    A representation of a part of a GEDCOM file as a list of lines.
    This class is used to give a list of Line objects the same features
    of the File object.

    For example without this class we wouldn't be able to call the "find" or the "find_one" method on the results
    of the "find" or the "find_one" method, because the results would just be a normal line.

    Another example is that we can represent a list we find as text or json.

    :Example:
        print g.find('tag', 'HUSB').text
        print g.find('tag', 'HUSB').json

    This class is important for being able to continually traverse through the File object without
    going back to the original File instance.

    """

    def __init__(self, lines):
        """GEDCOM SubFile Class

        This initialization override the initialization of the File object so instead of passing in
        the location of a GEDCOM object to open a file all you need is to pass in a list of GEDCOM
        Lines.

        :warning: This object should only be called on a list of objects that were initiated by the File class,
        this is due to the line objects having access the the rest of the file, and there line numbers updated.

        """
        self.lines = lines


class Line(dict):
    """GEDCOM Line Class

    This class is a subclass of dict. This class was made to give extra
    features to dictionaries to make them more suitable for representing
    GEDCOM Lines.

    """

    def __init__(self, line_string, file_class, line_number):
        """Initiate GEDCOM Line Class

        :param line_string: The string of the gedcom line
        :type line_string: str
        :note line_string: This is a benefit of using a subclass because a dictionary can be created from a string

        :param file_class: The instance of the File object that created this line
        :type file_class: File
        :note file_class: This allows the line object to access the instance of the File that crated it.

        :param line_number: The line number of this line
        :type file_class: int
        :note file_class: Specifying line number on initiation is more useful than having to continually check where
        a line is located in a list.

        """
        self.file = file_class
        # Set the private variable __text to the string provided, stripped of white space.
        self.__text = line_string.strip()
        # Set the update the dictionary object key values based on the string provided
        # This is a benefit of using a subclass because the user doesn't have to pass in
        # a dictionary
        try:
            self.update(**parse_line(self.__text))
        except SyntaxError as e:
            sys.exit("line number {0}: {1}".format(line_number, e.msg))

        # Add line number to the dictionary. This is more useful on continuously checking
        # where this object is in a list of Line objects
        self.update({"line_number": line_number})
        # Add empty children_line_numbers and parent_line_number keys to this dictionary.
        # This will be updated if this object was generated by the File class
        self.update({"children_line_numbers": [], "parent_line_numbers": []})

    @property
    def text(self):
        """Print GEDCOM Line as Text

        :note: this method currently returns the text string that was initially
        passed to create this object. This function may need to be updated to
        represent the string based on the dictionary if we want to support alteration
        to the GEDCOM file.

        :note: this function also provides a way of preventing the user from changing self.text

        :returns: GEDCOM line as text
        :rtype: string

        """
        return self.__text

    @property
    def children(self):
        """ Returns a list of GEDCOM lines objects that are children of this line.

        :note: This class makes use of the 'children_line_numbers' value in this
        class that was updated when the GEDCOM File Class was initiated

        :return: A list of matched lines, as a SubFile
        :rtype: SubFile

        :note: This method returns a SubFile object so that the returned object can
        continue to use methods defined in the File class.

        """
        if self.file:
            return SubFile(map(self.file.lines.__getitem__, self.get('children_line_numbers', [])))
        return None

    @property
    def parent(self):
        """Returns the parent line of this line

        :note: This class makes use of the 'parent_line_numbers' value in this
        class that was updated when the GEDCOM File Class was initiated

        :return: The Line object of the parent line
        :rtype: Line

        :note: This method only returns one value because a line can only have one parent.

        :note: This method will return None if line has no parent, i.e. the line level is 0.

        """
        return next(imap(self.file.lines.__getitem__, self.get('parent_line_numbers', [])), None)

    def refresh(self):
        """ Refresh this line

        Currently this determines which lines are parents and children of one another.

        :note: Currently this only needs to be called when the class is initiated, however
        if we want to support adding and removing line, this class will need to be called again.
        The calling of this method is handled by the File class once all Line ojects are created.

        """
        # Refresh Children Line Numbers.
        self.update({"children_line_numbers": self.__find_children_line_numbers()})
        # Refresh Parent Line Numbers.
        self.update({"parent_line_numbers": self.__find_parent_line_numbers()})

    def __find_children_line_numbers(self):
        """ Determine the line numbers of the children of this line.

        :returns: list of children line numbers
        :rtype: list of integers

        """
        child_line_numbers = []
        lines = self.file.lines
        line_number = self.get("line_number")
        #  if the line of this object isn't the last line in the file.
        if line_number < len(lines) - 1:
            #  if the line right after the line of this object has a greater level.
            if lines[line_number + 1].get("level") > lines[line_number]["level"]:
                # for the lines after the line of this object.
                for next_line in lines[line_number + 1:]:
                    # If the next_line we are on is on the same level
                    # as the first line after the line of this object.
                    if next_line["level"] == lines[line_number + 1]["level"]:
                        # Add this line number to the list of child line numbers
                        child_line_numbers.append(next_line.get('line_number'))
                    # Else if the next_line we are on has a greater level
                    # as the first line after the line of this object.
                    elif next_line["level"] > lines[line_number + 1]["level"]:
                        # We will ignore it because it is further down the tree.
                        # We will continue searching through lines though because
                        # there is still a possibility of finding more children of
                        # this object.
                        pass
                    # Else if the next_line we are on has a lower level
                    # as the first line after the line of this object.
                    elif next_line["level"] < lines[line_number + 1]["level"]:
                        # We will stop looking for children because we are done
                        # searching through this branch. All additional children
                        # will not be a child of this object.
                        break
        return child_line_numbers

    def __find_parent_line_numbers(self):
        """Determine the line numbers of the children of this line.

        :note: children_line_numbers must be accurate for this method to work properly.
        This is handled by updating the children_line_numbers before the parent_line_numbers in this.refresh

        :returns: list of parent line numbers
        :rtype: list of integers

        """
        lines = filter(lambda line: self["line_number"] in line.get("children_line_numbers", []), self.file.lines)
        line_numbers = map(lambda line: line.get("line_number"), lines)
        return line_numbers

    def follow_xref(self):
        """ Search file lines with an xref_id equal to this lines line_value

        :returns: matching line
        :rtype: GEDCOM Line
        """
        return self.file.find_one('xref_ID', self.get("line_value"))

    @property
    def ln(self):
        """ Line Number Property
        :return: line number
        """
        return self.get("line_number")+1

    @property
    def tag(self):
        """ Line tag Property
        :return: line number
        """
        return self.get("tag")

    @property
    def val(self):
        """ Line value Property
        :return: line value
        """
        return self.get("line_value", "")

    @property
    def datetime(self):
        """ Line value datetime
        :return: datetime of value
        """
        if self.get("tag") == "DATE":
            return tools.parse_date(self.get("line_value"))
        return None

    @property
    def story_dict(self):
        """ return line_number and value

        """
        return {"line_number": self.ln, "line_value": self.val}

    def ged(self):
        if self.tag == "INDI":
            pass
        elif self.tag == "TEST":
            pass


def demo(gedcom_file):
    """Demonstrate the capabilities of the module

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    """
    # - Demonstrate printing text of file -
    print gedcom_file.text
    print

    # - Demonstrate printing the line dictionary -
    for line in gedcom_file:
        print line
    print

    # - Demonstrate printing file as json -
    print gedcom_file.json
    print
    # - Demonstrate getting a line -
    print gedcom_file[5]  # - or - gedcom_file.lines[5]
    print

    # - Demonstrate getting line children and parents "
    print gedcom_file[0]
    print gedcom_file[0].children
    print gedcom_file[0].children[3]
    print gedcom_file[0].children[3].parent
    print gedcom_file[0].parent
    print

    # - Demonstrate filtering the list of lines from dictionary value "
    print gedcom_file.find('xref_ID', '@I1@')
    print gedcom_file.find('tag', 'HUSB')
    print gedcom_file.find('tag', 'a_value_that_will_never_be_found')
    print gedcom_file.find('tag', 'HUSB').text
    print gedcom_file.find('tag', 'HUSB').json

    print
    print gedcom_file.find_one('xref_ID', '@I1@')
    print gedcom_file.find_one('tag', 'HUSB')
    print gedcom_file.find_one('tag', 'a_value_that_will_never_be_found')

if __name__ == "__main__":
    pass

