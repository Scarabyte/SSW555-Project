
"""
Story Functions
"""
import tools
import logging

from functools import wraps
from datetime import datetime
from itertools import combinations

import gedcom

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"

logging.basicConfig(format="%(levelname)s:%(story_outcome)s - %(story_id)s - %(story_name)-s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def log(func):
    """ Function decarator used by the story decorator inorder to log the results of a story """
    def func_wrapper(gedcom_file):
        r = func(gedcom_file)
        for entry in r["output"]["passed"]:
            logger.info(entry, extra=dict(story_outcome="PASSED", story_id=r["id"], story_name=r["name"]))
        for entry in r["output"]["failed"]:
            logger.warning(entry, extra=dict(story_outcome="FAILED", story_id=r["id"], story_name=r["name"]))
        return r
    return func_wrapper


def story(id_):
    """ Function decarator used to find both outcomes of a story, and log and return the results """
    def story_decorator(func):
        @log
        def func_wrapper(gedcom_file):
            return {"id": id_, "name": func.__name__, "output": func(gedcom_file)}
        return func_wrapper
    return story_decorator


@story("US01")
def dates_before_current_date(gedcom_file):
    """ Dates (birth, marriage, divorce, death) should not be after the current date
    
    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    # TODO: Change datetime.now() to file date?
    # TODO: provide info about current date.
    r = {"passed": [], "failed": []}
    for date in gedcom_file.find("tag", "DATE"):
        parent = date.parent
        xref_ID = parent.parent.get("xref_ID") if type(parent) is gedcom.Line else None
        output = {"xref_ID": xref_ID, "tag": parent.get("tag"), "date": date.story_dict}
        r["passed"].append(output) if date.datetime < datetime.now() else r["failed"].append(output)
    return r


@story("US02")
def birth_before_marriage(gedcom_file):
    """ Birth should occur before marriage of an individual
    
    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        marr_date = tools.get_marriage_date(individual)
        if birt_date and marr_date:
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "marr": marr_date.story_dict}
            r["passed"].append(output) if birt_date.datetime < marr_date.datetime else r["failed"].append(output)
    return r


@story("US03")
def birth_before_death(gedcom_file):
    """ Birth should occur before death of an individual

    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        deat_date = tools.get_death_date(individual)
        if birt_date and deat_date:
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "deat": deat_date.story_dict}
            r["passed"].append(output) if birt_date.datetime < deat_date.datetime else r["failed"].append(output)
    return r


@story("US04")
def marriage_before_divorce(gedcom_file):
    """ Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    
    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        div_date = tools.get_divorce_date(individual)
        marr_date = tools.get_marriage_date(individual)
        if div_date and marr_date:
            output = {"xref_ID": individual.get("xref_ID"), "div": div_date.story_dict, "marr": marr_date.story_dict}
            r["passed"].append(output) if marr_date.datetime < div_date.datetime else r["failed"].append(output)
    return r


@story("US05")
def marriage_before_death(gedcom_file):
    """ Marriage should occur before death of either spouse

    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        marr_date = tools.get_marriage_date(individual)
        deat_date = tools.get_death_date(individual)
        if marr_date and deat_date:
            output = {"xref_ID": individual.get("xref_ID"), "marr": marr_date.story_dict, "deat": deat_date.story_dict}
            r["passed"].append(output) if marr_date.datetime < deat_date.datetime else r["failed"].append(output)
    return r


@story("US06")
def divorce_before_death(gedcom_file):
    """ Divorce can only occur before death of both spouses
    
    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        div_date = tools.get_divorce_date(individual)
        deat_date = tools.get_death_date(individual)
        if div_date and deat_date:
            output = {"xref_ID": individual.get("xref_ID"), "div": div_date.story_dict, "deat": deat_date.story_dict}
            r["passed"].append(output) if div_date.datetime < deat_date.datetime else r["failed"].append(output)
    return r


@story("US07")
def less_then_150_years_old(gedcom_file):
    """ Death should be less than 150 years after birth for dead people, and current date should be less than 150 years after birth for all living people
    
    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    # TODO: Change datetime.now() to file date?
    # TODO: provide info about current date.
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        deat_date = tools.get_death_date(individual)
        if birt_date and deat_date:
            age = (deat_date.datetime - birt_date.datetime).days / 365
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "deat": deat_date.story_dict, "age": age}
            r["passed"].append(output) if age < 150 else r["failed"].append(output)
        elif birt_date:
            age = (datetime.now() - birt_date.datetime).days / 365
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "age": age}
            r["passed"].append(output) if age < 150 else r["failed"].append(output)
    return r


@story("US08")
def birth_before_marriage_of_parents(gedcom_file):
    """ Child should be born after marriage of parents (and before their divorce)
    
    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for family in (tools.family_dict(line) for line in gedcom_file.find("tag", "FAM")):
        for child in family["children"]:
            child_birt_date = tools.get_birth_date(child)
            if child_birt_date and family["marr_date"]:
                output = {"xref_ID": child.get("xref_ID"), "birt": child_birt_date.story_dict, "marr": family["marr_date"].story_dict}
                passed = (family["marr_date"].datetime < child_birt_date.datetime)
                if family["div_date"]:
                    output["div"] = family["div_date"].story_dict
                    passed = passed and (family["div_date"].datetime > child_birt_date.datetime)
                r["passed"].append(output) if passed else r["failed"].append(output)
    return r


@story("US09")
def birth_before_death_of_parents(gedcom_file):
    """ Child should be born before death of mother and before 9 months after death of father
    
    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for family in (tools.family_dict(line) for line in gedcom_file.find("tag", "FAM")):
        mother_deat_date = tools.get_death_date(family["wife"])
        father_deat_date = tools.get_death_date(family["husb"])
        for child in family["children"]:
            child_birt_date = tools.get_birth_date(child)
        
            if child_birt_date and mother_deat_date :
                output = {"xref_ID": child.get("xref_ID"), "birt": child_birt_date.story_dict, "motherdeat": mother_deat_date.story_dict}
                passed = (child_birt_date.datetime < mother_deat_date.datetime)
                if  father_deat_date :
                    output["fatherdeat"] = father_deat_date.story_dict
                    #output = {"xref_ID": child.get("xref_ID"), "birt": child_birt_date.story_dict, "fatherdeat": father_deat_date.story_dict}
                    months_since_fathers_death = (father_deat_date.datetime - child_birt_date.datetime).days / 30
                    passed = passed and (months_since_fathers_death > 9)  
                r["passed"].append(output) if passed else r["failed"].append(output)
    return r

  
        
@story("US10")
def marriage_after_14(gedcom_file):
    """ Marriage should be at least 14 years after birth of both spouses
    
    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    #For each family, check if the difference between marriage and birth dates of both spouses is more than 14 years
    for family in (tools.family_dict(line) for line in gedcom_file.find("tag", "FAM")):
        couple = []
        couple.append(family["husb"])        
        couple.append(family["wife"])
        marr_date = family["marr_date"]
        
        for person in couple:
            birth_date = tools.get_birth_date(person)
            passed = False
            output = {"xref_ID": person.get("xref_ID")}
            if marr_date and birth_date :
                output = {"xref_ID": person.get("xref_ID"), "birt": birth_date.story_dict, "marr_date": marr_date.story_dict}
                age_during_marriage = (marr_date.datetime - birth_date.datetime).days / 365
                passed = (age_during_marriage > 14)
            r["passed"].append(output) if passed else r["failed"].append(output)
    return r


@story("US11")
def no_bigamy(gedcom_file):
    """ Marriage should not occur during marriage to another spouse

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    # Get individual's marriage start dates
    # Marriage ends with either divorce or death
    # Get spouse's divorce date
    # If spouse has no divorce date, get spouse death date
    # Does a second marriage start before the divorce date or death of the other spouse?

    for individual in gedcom_file.find("tag", "INDI"):
        # Get all combinations of marriages this individual is or has been in
        for marr_1, marr_2 in combinations(tools.iter_marriage_timeframe_dict(individual), 2):
            # check if datetime of these marriages overlap
            # http://stackoverflow.com/questions/9044084/efficient-date-range-overlap-calculation-in-python
            # http://stackoverflow.com/questions/325933/determine-whether-two-date-ranges-overlap
            
            # marriages start with marr_date
            # marriages end with div_date, or (if no div_date) the first deat_date of either spouse
            # if the marriage hasen't ended then datetime.max is used as the datetime
			# (to simulate the ending being in the far future)
            failed = (marr_1["start"]["dt"] <= marr_2["end"]["dt"]) and (marr_1["end"]["dt"] >= marr_2["start"]["dt"])
            # Don't include dt in user story
            # https://docs.python.org/2/tutorial/datastructures.html
            marr_1["start"].pop("dt"), marr_1["end"].pop("dt"), marr_2["start"].pop("dt"), marr_2["end"].pop("dt")
            output =  {"marr_1":marr_1, "marr_2": marr_2}
            r["failed"].append(output) if failed else r["passed"].append(output)

    return r


@story("US12")
def parents_not_too_old(gedcom_file):
    """ Mother should be less than 60 years older than her children and
        father should be less than 80 years older than his children

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for individual in gedcom_file.find("tag", "INDI"):
        # Get individual's birth date
        child_birt_date = tools.get_birth_date(individual)
        # Get father and mother's birth dates
        mother_age, father_age = 0, 0
        mother = tools.get_mother(individual)
        father = tools.get_father(individual)
        if mother:
            mother_birt_date = tools.get_birth_date(mother)
            mother_age = (child_birt_date.datetime - mother_birt_date.datetime).days / 365
        if father:
            father_birt_date = tools.get_birth_date(father)
            father_age = (child_birt_date.datetime - father_birt_date.datetime).days / 365
        
        output = {"xref_ID": individual.get("xref_ID"), "child_birt_date": child_birt_date.story_dict,
                  "father_birt_date": father_birt_date.story_dict, "father_age": father_age,
                  "mother_birt_date": mother_birt_date.story_dict, "mother_age": mother_age}
        
        r["passed"].append(output) if (mother_age < 60) and (father_age < 80) \
                                   and (mother_age > 0) and (father_age > 0) \
                                   else r["failed"].append(output)
        
    return r


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


if __name__ == "__main__":
    import json 
    g = gedcom.File()

    fname = "Test_Files/My-Family-20-May-2016-697-Simplified.ged"
    try:
        g.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))



