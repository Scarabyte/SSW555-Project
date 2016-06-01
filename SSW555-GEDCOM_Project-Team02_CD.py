"""
Author: Constantine Davantzis
Class: SSW-555
Assignment Number: Project 02

Assignment Description:
Write a program that asks the user for a quiz score and converts that numeric score to a letter grade.

"""
#Import regular expression operations
import re 

#Pre-Compile Regex for GEDCOM Line.
parseLineRegEx = re.compile(r"(?P<level>[0-9]|[1-9][0-9])\s(?P<xref_ID>@\S+@)?\s?(?P<tag>\S+)\s*(?P<line_value>(.+))?")

#Declare valid line tags for our project
VALID_TAGS = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]


def parse_line(s):
    """Parse GEDCOM line into dictionary

    :param s: The GEDCOM line string to parse.
    :type s: str

    :returns: GEDCOM line dictionary
    :rtype: dict

    """
    m = parseLineRegEx.match(s)
    if not m:
        # Raise exception of regex could not match line.
        raise SyntaxError('gedcom_line does not have syntax: "level + delim + [optional_xref_ID] + tag + [optional_line_value] + terminator"')
    d = m.groupdict() 
    d["isTagValid"] = d["tag"] in VALID_TAGS
    return d


def print_line(d):
    """Prints the GEDCOM line dictionary nicely. 

    :param d: The GEDCOM line dictionary to print
    :type d: dict

    :returns: None
    :rtype: None

    """
    d["indent"] = int(d["level"])*"    "
    string = "{indent}level: {level}\n{indent}xref_ID: {xref_ID}\n{indent}tag: {tag}\n{indent}line_value: {line_value}"
    formatted_string = string.format(**d)
    print formatted_string
    if not d["isTagValid"]:
        print "{0}Warning: Invalid tag!".format(d["indent"])
    print 

if __name__ == "__main__":
    """ Parse and print each line of of the GEDCOM.ged file in the same folder as this script """
    f = open('GEDCOM.ged')
    for line in f:
        print_line(parse_line(line))

