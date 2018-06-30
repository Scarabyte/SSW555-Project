"""
SSW555 GEDCOM Parsing Project - Team02
This is the main file for the project
"""
import json
import logging
import sys

from gedcom.parser import File
import stories

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"
__status__ = "Development"


def run(gedcom_file, show_passed=False):
    """ Check Gedcom File For Errors

    :param gedcom_file: The GEDCOM File object to perform assignment on
    :type gedcom_file: parser.File

    """

    # Log only failed cases to console if show_passed is False else show passed and failed cases
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG) if show_passed else stream_handler.setLevel(logging.INFO)
    stories.logger.addHandler(stream_handler)

    # Log only failed cases to file "output.md"
    user_output = logging.FileHandler(filename='Test_Results/output.md', mode="w")
    user_output.setLevel(logging.INFO)
    stories.logger.addHandler(user_output)

    # Log only passed cases to file "output.debug.md"
    debug_output = logging.FileHandler(filename='Test_Results/output.debug.md', mode="w")
    debug_output.setLevel(logging.DEBUG)
    stories.logger.addHandler(debug_output)

    log = {
        "individuals": stories.individual_summary(gedcom_file),
        "families": stories.family_summary(gedcom_file),
        "stories": [
            stories.dates_before_current_date(gedcom_file),
            stories.birth_before_marriage(gedcom_file),
            stories.birth_before_death(gedcom_file),
            stories.marriage_before_divorce(gedcom_file),
            stories.marriage_before_death(gedcom_file),
            stories.divorce_before_death(gedcom_file),
            stories.less_then_150_years_old(gedcom_file),
            stories.birth_before_marriage_of_parents(gedcom_file),
            stories.birth_before_death_of_parents(gedcom_file),
            stories.marriage_after_14(gedcom_file),
            stories.no_bigamy(gedcom_file),
            stories.parents_not_too_old(gedcom_file),
            stories.siblings_spacing(gedcom_file),
            stories.less_than_5_multiple_births(gedcom_file),
            stories.fewer_than_15_siblings(gedcom_file),
            stories.male_last_names(gedcom_file),
            stories.no_marriages_to_descendants(gedcom_file),
            stories.siblings_should_not_marry(gedcom_file),
            stories.first_cousins_should_not_marry(gedcom_file),
            stories.aunts_and_uncles(gedcom_file),
            stories.correct_gender_for_role(gedcom_file),
            stories.unique_ids(gedcom_file),
            stories.unique_name_and_birth_date(gedcom_file),
            stories.unique_families_by_spouses(gedcom_file)
        ]
    }

    # attempt to save log to json file
    try:
        fname_out = 'Test_Results/log.json'
        with open(fname_out, 'w') as outfile:
            json.dump(log, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    except IOError as e:
        sys.exit("Error Saving Results - {0}: '{1}'".format(e.strerror, e.filename))


if __name__ == "__main__":
    gedcom_file = File()
    # Request file name from user
    fname = raw_input('Enter the file name to open: ')
    #fname = "Test_Files/My-Family-20-May-2016-697-Simplified-WithErrors-Sprint04.ged"

    try:
        gedcom_file.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))

    run(gedcom_file, show_passed=False)

    print "Successfully saved output to {0}".format('Test_Results/output.md')
    print "Successfully saved debug output to {0}".format('Test_Results/output.debug.md')
    print "Successfully saved log to {0}".format('Test_Results/log.json')
