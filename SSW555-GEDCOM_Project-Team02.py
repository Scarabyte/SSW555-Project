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


def run(gedcom_file, show_passed=False):
    """ Check Gedcom File For Errors

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: gedcom.File

    """
    # TODO: Write better docstring
    # TODO: Work on output structure
    # Todo: Move to gedcom class?

    stories.console_output.setLevel(logging.DEBUG) if show_passed else stories.console_output.setLevel(logging.INFO)

    return {
        "individuals": stories.individual_summary(gedcom_file),
        "families": stories.family_summary(gedcom_file),
        "stories": [
            {
                "sprint_number": 1,
                "results": [stories.dates_before_current_date(gedcom_file),
                            stories.birth_before_marriage(gedcom_file),
                            stories.birth_before_death(gedcom_file),
                            stories.marriage_before_divorce(gedcom_file),
                            stories.marriage_before_death(gedcom_file),
                            stories.divorce_before_death(gedcom_file)]
            },
            {
                "sprint_number": 2,
                "results": [stories.less_then_150_years_old(gedcom_file),
                            stories.birth_before_marriage_of_parents(gedcom_file),
                            stories.birth_before_death_of_parents(gedcom_file),
                            stories.marriage_after_14(gedcom_file),
                            stories.no_bigamy(gedcom_file),
                            stories.parents_not_too_old(gedcom_file)]
            },
            {
                "sprint_number": 3,
                "results": [stories.siblings_spacing(gedcom_file),
                            stories.less_than_5_multiple_births(gedcom_file),
                            stories.fewer_than_15_siblings(gedcom_file),
                            stories.male_last_names(gedcom_file),
                            stories.no_marriages_to_descendants(gedcom_file),
                            stories.siblings_should_not_marry(gedcom_file)]
            }

        ]
    }


if __name__ == "__main__":
    # Uncomment to show passed cases aswell

    g = gedcom.File()

    # Request file name from user
    #fname = raw_input('Enter the file name to open: ')
    fname = "Test_Files/My-Family-20-May-2016-697-Simplified-WithErrors-Sprint03.ged"
    try:
        g.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))

    # Todo: include input filename in output filename

    try:
        fname_out = 'Test_Results/log.json'
        with open(fname_out, 'w') as outfile:
            json.dump(run(g, show_passed=False), outfile, sort_keys=True, indent=4, separators=(',', ': '))
    except IOError as e:
        sys.exit("Error Saving Results - {0}: '{1}'".format(e.strerror, e.filename))
    else:
        print "Successfully saved results to Test_Results/log.json"
