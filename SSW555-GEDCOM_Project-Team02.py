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

def project_04(gedcom_file):
    """ Function to perform the Project04 Tasks: Print the results of Sprint 1

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    :Examples:
        myfile = gedcom.File("Test_Files/GEDCOM.ged")
        project_04(myfile)

    """
    pass

if __name__ == "__main__":
    g = gedcom.File()

    # Request file name from user
    fname = raw_input('Enter the file name to open: ')
    try:
        g.read_file(fname)
    except:
        print 'Invalid file name: ', fname
        exit()

    # project_03(g)
    # project_04(g)

