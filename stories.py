"""
Story Functions
"""

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"

import tools
from datetime import datetime


def dates_before_current_date(gedcom_file, find_cases_that_are):
    """ Dates before current date

    Description: Dates (birth, marriage, divorce, death) should not be after the current date
    story_id: US01
    author: Constantine Davantzis
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    :Example:
        print list(dates_before_current_date(g, True))
        print list(dates_before_current_date(g, False))

    """
    for date in gedcom_file.find("tag", "DATE"):
        value = date.get('line_value')
        if (tools.parse_date(value) < datetime.now()) == find_cases_that_are:
            yield {"xref_ID": date.parent.parent.get("xref_ID"), "tag": date.parent.get("tag"), "date": value}


def birth_before_marriage(gedcom_file, find_cases_that_are):
    """ Birth before marriage
    Description: Birth should occur before marriage of an individual
    story_id: US02
    author: Constantine Davantzis
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    :Example:
        print list(birth_before_marriage(g, True))
        print list(birth_before_marriage(g, False))

    """
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        marr_date = tools.get_marriage_date(individual)
        if birt_date and marr_date:
            birt_value = birt_date.get("line_value")
            marr_value = marr_date.get("line_value")
            if (tools.parse_date(birt_value) < tools.parse_date(marr_value)) == find_cases_that_are:
                yield {"xref_ID": individual.get("xref_ID"), "birt_value": birt_value, "marr_value": marr_value}


def birth_before_death(gedcom_file, find_cases_that_are):
    """ Birth before death
    Description: Birth should occur before death of an individual
    story_id: US03
    author: vibharavi
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    """
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        deat_date = tools.get_death_date(individual)
        if birt_date and deat_date:
            birt_value = birt_date.get("line_value")
            deat_value = deat_date.get("line_value")
            if (tools.parse_date(birt_value) < tools.parse_date(deat_value)) == find_cases_that_are:
                yield {"xref_ID": individual.get("xref_ID"), "birt_value": birt_value, "deat_value":deat_value}


def marriage_before_divorce(gedcom_file, find_cases_that_are):
    """ Marriage before divorce
    Description: Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    story_id: US04
    author: vibharavi
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    """
    for individual in gedcom_file.find("tag", "INDI"):
        div_date = tools.get_divorce_date(individual)
        marr_date = tools.get_marriage_date(individual)
        if div_date and marr_date:
            div_value = div_date.get("line_value")
            marr_value = marr_date.get("line_value")
            if (tools.parse_date(marr_value) < tools.parse_date(div_value)) == find_cases_that_are:
                yield {"xref_ID": individual.get("xref_ID"), "div_value": div_value, "marr_value": marr_value}


def marriage_before_death(gedcom_file, find_cases_that_are):
    """ Marriage before death
    Description: Marriage should occur before death of either spouse
    story_id: US05
    author: Adam Burbidge
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    """
    for individual in gedcom_file.find("tag", "INDI"):
        marr_date = tools.get_marriage_date(individual)
        deat_date = tools.get_death_date(individual)
        if marr_date and deat_date:
            marr_value = marr_date.get("line_value")
            deat_value = deat_date.get("line_value")
            if (tools.parse_date(marr_value) < tools.parse_date(deat_value)) == find_cases_that_are:
                yield {"xref_ID": individual.get("xref_ID"), "Marriage: ": marr_value, "Death:    ": deat_value}


def divorce_before_death(gedcom_file, find_cases_that_are):
    """ Divorce before death
    Description: Divorce can only occur before death of both spouses
    story_id: US06
    author: Adam Burbidge
    sprint: 1

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    :param find_cases_that_are: Specify which cases to return.
    :type find_cases_that_are: bool

    """
    for individual in gedcom_file.find("tag", "INDI"):
        div_date = tools.get_divorce_date(individual)
        deat_date = tools.get_death_date(individual)
        if div_date and deat_date:
            div_value = div_date.get("line_value")
            deat_value = deat_date.get("line_value")
            if (tools.parse_date(div_value) < tools.parse_date(deat_value)) == find_cases_that_are:
                yield {"xref_ID": individual.get("xref_ID"), "Divorce: ": div_value, "Death:     ": deat_value}


def less_then_150_years_old():
    """ Less then 150 years old
    Description: Death should be less than 150 years after birth for dead people, and current date should be less than 150 years after birth for all living people
    story_id: US07
    author: cd
    sprint: 2
    """
    pass


def birth_before_marriage_of_parents():
    """ Birth before marriage of parents
    Description: Child should be born after marriage of parents (and before their divorce)
    story_id: US08
    author: cd
    sprint: 2
    """
    pass


def birth_before_death_of_parents():
    """ Birth before death of parents
    Description: Child should be born before death of mother and before 9 months after death of father
    story_id: US09
    author: vr
    sprint: 2
    """
    pass


def marriage_after_14():
    """ Marriage after 14
    Description: Marriage should be at least 14 years after birth of both spouses
    story_id: US10
    author: vr
    sprint: 2
    """
    pass


def no_bigamy():
    """ No bigamy
    Description: Marriage should not occur during marriage to another spouse
    story_id: US11
    author: ab
    sprint: 2
    """
    pass


def parents_not_too_old():
    """ Parents not too old
    Description: Mother should be less than 60 years older than her children and father should be less than 80 years older than his children
    story_id: US12
    author: ab
    sprint: 2
    """
    pass


def siblings_spacing():
    """ Siblings spacing
    Description: Birth dates of siblings should be more than 8 months apart or less than 2 days apart
    story_id: US13
    author: cd
    sprint: 3
    """
    pass


def multiple_births_less_than_5():
    """ Multiple births less than 5
    Description: No more than five siblings should be born at the same time
    story_id: US14
    author: cd
    sprint: 3
    """
    pass


def fewer_than_15_siblings():
    """ Fewer than 15 siblings
    Description: There should be fewer than 15 siblings in a family
    story_id: US15
    author: vr
    sprint: 3
    """
    pass


def male_last_names():
    """ Male last names
    Description: All male members of a family should have the same last name
    story_id: US16
    author: vr
    sprint: 3
    """
    pass


def no_marriages_to_descendants():
    """ No marriages to descendants
    Description: Parents should not marry any of their descendants
    story_id: US17
    author: ab
    sprint: 3
    """
    pass


def siblings_should_not_marry():
    """ Siblings should not marry
    Description: Siblings should not marry one another
    story_id: US18
    author: ab
    sprint: 3
    """
    pass


def first_cousins_should_not_marry():
    """ First cousins should not marry
    Description: First cousins should not marry one another
    story_id: US19
    author: cd
    sprint: 4
    """
    pass


def aunts_and_uncles():
    """ Aunts and uncles
    Description: Aunts and uncles should not marry their nieces or nephews
    story_id: US20
    author: cd
    sprint: 4
    """
    pass


def correct_gender_for_role():
    """ Correct gender for role
    Description: Husband in family should be male and wife in family should be female
    story_id: US21
    author: vr
    sprint: 4
    """
    pass


def unique_ids():
    """ Unique IDs
    Description: All individual IDs should be unique and all family IDs should be unique
    story_id: US22
    author: vr
    sprint: 4
    """
    pass


def unique_name_and_birth_date():
    """ Unique name and birth date
    Description: No more than one individual with the same name and birth date should appear in a GEDCOM file
    story_id: US23
    author: ab
    sprint: 4
    """
    pass


def unique_families_by_spouses():
    """ Unique families by spouses
    Description: No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file
    story_id: US24
    author: ab
    sprint: 4
    """
    pass


def unique_first_names_in_families():
    """ Unique first names in families
    Description: No more than one child with the same name and birth date should appear in a family
    story_id: US25
    author: TBD
    sprint: TBD
    """
    pass


def corresponding_entries():
    """ Corresponding entries
    Description: All family roles (spouse, child) specified in an individual record should have corresponding entries in those family records, and all individual roles (spouse, child) specified in family records should have corresponding entries in those individual's records
    story_id: US26
    author: TBD
    sprint: TBD
    """
    pass


def include_individual_ages():
    """ Include individual ages
    Description: Include person's current age when listing individuals
    story_id: US27
    author: TBD
    sprint: TBD
    """
    pass


def order_siblings_by_age():
    """ Order siblings by age
    Description: List siblings in families by age
    story_id: US28
    author: TBD
    sprint: TBD
    """
    pass


def list_deceased():
    """ List deceased
    Description: List all deceased individuals in a GEDCOM file
    story_id: US29
    author: TBD
    sprint: TBD
    """
    pass


def list_living_married():
    """ List living married
    Description: List all living married people in a GEDCOM file
    story_id: US30
    author: TBD
    sprint: TBD
    """
    pass


def list_living_single():
    """ List living single
    Description: List all living people over 30 who have never been married in a GEDCOM file
    story_id: US31
    author: TBD
    sprint: TBD
    """
    pass


def list_multiple_births():
    """ List multiple births
    Description: List all multiple births in a GEDCOM file
    story_id: US32
    author: TBD
    sprint: TBD
    """
    pass


def list_orphans():
    """ List orphans
    Description: List all orphaned children (both parents dead and child < 18 years old) in a GEDCOM file
    story_id: US33
    author: TBD
    sprint: TBD
    """
    pass


def list_large_age_differences():
    """ List large age differences
    Description: List all couples who were married when the older spouse was more than twice as old as the younger spouse
    story_id: US34
    author: TBD
    sprint: TBD
    """
    pass


def list_recent_births():
    """ List recent births
    Description: List all people in a GEDCOM file who were born in the last 30 days
    story_id: US35
    author: TBD
    sprint: TBD
    """
    pass


def list_recent_deaths():
    """ List recent deaths
    Description: List all people in a GEDCOM file who died in the last 30 days
    story_id: US36
    author: TBD
    sprint: TBD
    """
    pass


def list_recent_survivors():
    """ List recent survivors
    Description: List all living spouses and descendants of people in a GEDCOM file who died in the last 30 days
    story_id: US37
    author: TBD
    sprint: TBD
    """
    pass


def list_upcoming_birthdays():
    """ List upcoming birthdays
    Description: List all living people in a GEDCOM file whose birthdays occur in the next 30 days
    story_id: US38
    author: TBD
    sprint: TBD
    """
    pass


def list_upcoming_anniversaries():
    """ List upcoming anniversaries
    Description: List all living couples in a GEDCOM file whose marriage anniversaries occur in the next 30 days
    story_id: US39
    author: TBD
    sprint: TBD
    """
    pass


def include_input_line_numbers():
    """ Include input line numbers
    Description: List line numbers from GEDCOM source file when reporting errors
    story_id: US40
    author: TBD
    sprint: TBD
    """
    pass


def include_partial_dates():
    """ Include partial dates
    Description: Accept and use dates without days or without days and months
    story_id: US41
    author: TBD
    sprint: TBD
    """
    pass


def reject_illegitimate_dates():
    """ Reject illegitimate dates
    Description: All dates should be legitimate dates for the months specified (e.g., 2/30/2015 is not legitimate)
    story_id: US42
    author: TBD
    sprint: TBD
    """
    pass
