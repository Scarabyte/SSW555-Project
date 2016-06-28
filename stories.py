"""
Story Functions
"""
import tools
import logging
from functools import wraps

from datetime import datetime
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
    for individual in gedcom_file.find("tag", "INDI"):
        print list(tools.iter_marr_and_div_date_pairs(individual))
        birt_date = tools.get_birth_date(individual)
        p_marr_date = tools.get_parents_marriage_date(individual)
        p_div_date = tools.get_parents_divorce_date(individual)
        if birt_date and p_marr_date and p_div_date:
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "parent_marr": p_marr_date.story_dict, "parent_div": p_div_date.story_dict}
            if (p_marr_date.datetime < birt_date.datetime) and (p_div_date.datetime > birt_date.datetime):
                r["passed"].append(output)
            else:
                r["failed"].append(output)
        if birt_date and p_marr_date:
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "parent_marr": p_marr_date.story_dict}
            if p_marr_date.datetime < birt_date.datetime:
                r["passed"].append(output)
            else:
                r["failed"].append(output)
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
    for individual in gedcom_file.find("tag", "INDI"):
        parent_list = tools.get_parents(individual)
        for parent in parent_list:
            parent_deat_date = tools.get_deat_date(parent)
            for child in tools.iter_children(individual):
                child_birt_date = tools.get_birth_date(child)
                if parent.children.find_one("tag", "SEX") == "F":
                    output = {"xref_ID": individual.get("xref_ID"), "birt": child_birt_date.story_dict,
                              "deat": parent_deat_date.story_dict}
                    r["passed"].append(output) if child_birt_date > parent_deat_date else  r["failed"].append(output)
                else:
                    father_age = parent_deat_date.datetime.days / 12
                    output = {"xref_ID": individual.get("xref_ID"), "birt": child_birt_date.story_dict,
                              "deat": parent_deat_date.story_dict}
                    r["passed"].append(output) if child_birt_date > father_age else r["failed"].append(output)
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
    for individual in gedcom_file.find("tag", "INDI"):
        marr_dates = tools.get_marriage_dates(individual)
        spouse_list = tools.get_spouses(individual)
        for spouse in spouse_list:
            birt_date = tools.get_birth_date(spouse)
            if birt_date and marr_dates:
                minimum_years = (birt_date.datetime).days / 365
                output = {"xref_ID": individual.get("xref_ID"), "marr": marr_dates.story_dict}
                r["passed"].append(output) if marr_dates < (14 + minimum_years) else r["failed"].append(output)
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
    # Do things
    # Get individual's marriage start dates
    for individual in gedcom_file.find("tag", "INDI"):
        marr_dates = tools.get_marriage_dates(individual)
        spouse_list = tools.get_spouses(individual)
        for spouse in spouse_list:
            s_div_date = tools.get_divorce_date(spouse)
            s_deat_date = tools.get_death_date(spouse)
            if div_date or deat_date:
                for marr_start in marr_dates:
                    if marr_start.datetime > div_date.datetime:
                        output = {"xref_ID": individual.get("xref_ID"), "marr": marr_start.story_dict,
                                  "spouse_div": s_div_date.story_dict}
                        r["failed"].append(output)
                    elif marr_start.datetime > deat_date.datetime:
                        output = {"xref_ID": individual.get("xref_ID"), "marr": marr_start.story_dict,
                                  "spouse_deat": s_deat_date.story_dict}
                        r["failed"].append(output)
                    else:
                        output = {"xref_ID": individual.get("xref_ID"), "marr": marr_start.story_dict)
                        r["passed"].append(output)
                                              
    # Marriage ends with either divorce or death
    # Get spouse's divorce or death dates
    # Does a second marriage start before the divorce date or death of the other spouse?
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
    # Do things
    # Get individual's birth date
    for individual in gedcom_file.find("tag", "INDI"):
        birt_date = tools.get_birth_date(individual)
        parent_list = tools.get_parents(individual)
        for parent in parent_list:
            parent_birt_date = tools.get_birth_date(parent)
            parent_age = (parent_birt_date.datetime - birt_date.datetime).days / 365
            output = {"xref_ID": individual.get("xref_ID"), "birt": birt_date.story_dict, "parent_age": parent_age}
            if parent.children.find_one("tag", "SEX") == "M":
                r["passed"].append(output) if age < 80 else r["failed"].append(output)
            else:
                r["passed"].append(output) if age < 60 else r["failed"].append(output)
    # Get father and mother's birth dates
    # Compare dates
    # Repeat for both father and mother of all individuals
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
    
    birth_before_marriage_of_parents(g)
