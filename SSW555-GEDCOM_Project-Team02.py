"""
SSW555 GEDCOM Parsing Project - Team02
This is the main file for the project
"""

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"
__status__ = "Development"

import gedcom
import stories  # Will be used once we start completing stories.


def project_03(gedcom_file):
    """ function to perform point 5 of the Project03 Assignment

    Print the unique identifiers and names of each of the individuals in
    order by their unique identifiers. Then, for each family, print the
    unique identifiers and names of the husbands and wives, in order by
    unique family identifiers.

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    :Examples:
        g = gedcom.File("Test_Files/GEDCOM.ged")
        project_03(g)

    """
    print " - Individuals - "
    for individual in gedcom_file.individuals.iteritems():
        print individual
    print
    print " - Families - "
    for family in gedcom_file.families.iteritems():
        print family

if __name__ == "__main__":
    g = gedcom.File()

    # For testing purposes only
    # print "TESTING FIRST FILE:"
    # g.read_file("Test_Files/GEDCOM.ged")
    # project_03(g)
    # print
    # print "TESTING SECOND FILE:"
    # g.read_file("Test_Files/My-Family-20-May-2016-697-Simplified.ged")
    # project_03(g)
    # print

    # Request file name from user
    fname = raw_input('Enter the file name to open: ')
    try:
        g.read_file(fname)
    except:
        print 'Invalid file name: ', fname
        exit()

    # project_03(g)
    
    stories.marriage_before_death(g, True)
