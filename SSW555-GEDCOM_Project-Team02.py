"""
SSW555 GEDCOM Parsing Project - Team02
This is the main file for the project
"""
import json
import logging

import gedcom
import stories

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
        print project_04(myfile)

    """
    r = {
        "Sprint Number": 1,
        "Stories": {
            "US01": {"1. title": "dates_before_current_date",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.dates_before_current_date(gedcom_file, True)),
                                  False: list(stories.dates_before_current_date(gedcom_file, False))}},
            "US02": {"1. title": "birth_before_marriage",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.birth_before_marriage(gedcom_file, True)),
                                  False: list(stories.birth_before_marriage(gedcom_file, False))}},
            "US03": {"1. title": "birth_before_death",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.birth_before_death(gedcom_file, True)),
                                  False: list(stories.birth_before_death(gedcom_file, False))}},
            "US04": {"1. title": "marriage_before_divorce",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.marriage_before_divorce(gedcom_file, True)),
                                  False: list(stories.marriage_before_divorce(gedcom_file, False))}},
            "US05": {"1. title": "marriage_before_death",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.marriage_before_death(gedcom_file, True)),
                                  False: list(stories.marriage_before_death(gedcom_file, False))}},
            "US06": {"1. title": "divorce_before_death",
                     "2. desired_case": True,
                     "3. cases": {True: list(stories.divorce_before_death(gedcom_file, True)),
                                  False: list(stories.divorce_before_death(gedcom_file, False))}},
        }
    }

    logger = logging.getLogger("simple_example")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    for story, info in r["Stories"].iteritems():
        desired_case = info["2. desired_case"]
        undesired_case = not desired_case
        desired_cases = info["3. cases"][desired_case]
        undesired_cases = info["3. cases"][undesired_case]
        for case in desired_cases:
            logger.info("".join(
                    [story, " - ", info["1. title"], " - DESIRED_CASE(", str(undesired_case), ") - ",
                     str(case)]))
        for case in undesired_cases:
            logger.warn("".join(
                    [story, " - ", info["1. title"], " - UNDESIRED_CASE(", str(undesired_case), ") - ",
                     str(case)]))
    return r

if __name__ == "__main__":
    g = gedcom.File()

    # Request file name from user
    fname = raw_input('Enter the file name to open: ')
    try:
        g.read_file(fname)
    except:
        print 'Invalid file name: ', fname
        exit()

    # Save Project04 results to file
    with open('project_04_results.json', 'w') as outfile:
        json.dump(project_04(g), outfile, sort_keys=True, indent=4, separators=(',', ': '))
