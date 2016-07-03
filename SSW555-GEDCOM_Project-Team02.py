"""
SSW555 GEDCOM Parsing Project - Team02
This is the main file for the project
"""
import json
import logging

import gedcom
import stories
import sys
__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"
__status__ = "Development"


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
    return {"Individuals": gedcom_file.p3_individuals,
            "Families": gedcom_file.p3_families}


def project_04(gedcom_file):
    """ Function to perform the Project04 Tasks: Print the results of Sprint 1

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    :Examples:
        myfile = gedcom.File("Test_Files/GEDCOM.ged")
        print project_04(myfile)

    """
    return {
        "Sprint Number": 1,
        "Stories": [stories.dates_before_current_date(gedcom_file),
                    stories.birth_before_marriage(gedcom_file),
                    stories.birth_before_death(gedcom_file),
                    stories.marriage_before_divorce(gedcom_file),
                    stories.marriage_before_death(gedcom_file),
                    stories.divorce_before_death(gedcom_file)
                    ]
    }


def project_06(gedcom_file):
    """ Function to perform the Project06 Tasks: Print the results of Sprint 2

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    :Examples:
        myfile = gedcom.File("Test_Files/GEDCOM.ged")
        print project_06(myfile)

    """
    return {
        "Sprint Number": 2,
        "Stories": [stories.less_then_150_years_old(gedcom_file),
                    stories.birth_before_marriage_of_parents(gedcom_file),
                    stories.birth_before_death_of_parents(gedcom_file),
                    stories.marriage_after_14(gedcom_file),
                    stories.no_bigamy(gedcom_file),
                    stories.parents_not_too_old(gedcom_file)
                    ]
    }


if __name__ == "__main__":
    g = gedcom.File()

    # Request file name from user
    fname = raw_input('Enter the file name to open: ')
    # fname = "Test_Files/try.ged"
    try:
        g.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))

    try:
        with open('project_03_results.json', 'w') as outfile:
            json.dump(project_03(g), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    except IOError as e:
        sys.exit("Project 03: Error Saving Results - {0}: '{1}'".format(e.strerror, e.filename))
    except TypeError as e:
        sys.exit("Project 03: Error Saving Type Of Results To File - {0}: '{1}'".format(e.strerror, e.filename))
    else:
        print "Project 03: Successfully saved results to project_03_results.json"

    try:
        with open('project_04_results.json', 'w') as outfile:
            json.dump(project_04(g), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    except IOError as e:
        sys.exit("Project 04: Error Saving Results - {0}: '{1}'".format(e.strerror, e.filename))
    except TypeError as e:
        sys.exit("Project 04: Error Saving Type Of Results To File - {0}: '{1}'".format(e.strerror, e.filename))
    else:
        print "Project 04: Successfully saved results to project_04_results.json"

    try:
        with open('project_06_results.json', 'w') as outfile:
            json.dump(project_06(g), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    except IOError as e:
        sys.exit("Project 06: Error Saving Results - {0}: '{1}'".format(e.strerror, e.filename))
    except TypeError as e:
        sys.exit("Project 06: Error Saving Type Of Results To File - {0}: '{1}'".format(e.strerror, e.filename))
    else:
        print "Project 06: Successfully saved results to project_06_results.json"
