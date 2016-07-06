"""
Story Functions
"""
import tools
import logging
import sys
from datetime import datetime
from itertools import combinations

import gedcom

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"


logging.basicConfig(format='%(story_id)-13s| %(story_name)s (%(status)s) - %(message)s', level=logging.DEBUG)


def log(func):
    """ Function decarator used by the story decorator inorder to log the results of a story """
    def func_wrapper(gedcom_file):
        r = func(gedcom_file)
        for entry in r["output"]["passed"]:
            logging.info(entry.get("message", ""), extra=dict(story_id=r["id"], status="Passed", story_name=r["name"]))
        for entry in r["output"]["failed"]:
            logging.info(entry.get("message", ""), extra=dict(story_id=r["id"], status="Failed", story_name=r["name"]))

        return r
    return func_wrapper


def story(id_):
    """ Function decarator used to find both outcomes of a story, and log and return the results """
    def story_decorator(func):
        @log
        def func_wrapper(gedcom_file):
            if type(gedcom_file) is not gedcom.File:
                raise TypeError("Story function must be provided a gedcom file object.")
            return {"id": id_, "name": func.__name__, "output":  func(gedcom_file)}
        return func_wrapper
    return story_decorator


@story("Error US01")
def dates_before_current_date(gedcom_file):
    """ Dates (birth, marriage, divorce, death) should not be after the current date
    
    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """

    r = {"passed": [], "failed": []}
    for date in gedcom_file.find("tag", "DATE"):
        now = datetime.now()
        output = {"date_type": date.parent.get("tag"),
                  "date": date.story_dict,
                  "current_date": now.strftime("%d %b %Y").upper()}
        try:
            pp = date.parent.parent
            if pp.tag == "INDI":
                output["individual_id"] = date.parent.parent.get("xref_ID")
            elif pp.tag == "FAM":
                output["family_id"] = date.parent.parent.get("xref_ID")
        except AttributeError:
            pass

        if date.datetime < now:
            r["passed"].append(output)
        else:
            r["failed"].append(output)
    return r


@story("Error US02")
def birth_before_marriage(gedcom_file):
    """ Birth should occur before marriage of an individual
    
    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    passed_message = "Individual {0} born {1} before {2} marriage ({3}) on {4}"
    failed_message = "Individual {0} born {1} after {2} marriage ({3}) on {4}"

    for indi in (i for i in gedcom_file.individuals if i.has("birth_date")):
        for fam in (fam for fam in indi.families("FAMS") if fam.has("marriage_date")):
            out = {"indi": {"xref": indi.xref, "birth_date": indi.birth_date.story_dict},
                   "fam": {"xref": fam.xref, "marr_date": fam.marriage_date.story_dict}}
            msg_out = (indi, indi.birth_date, indi.pronoun, fam.xref, fam.marriage_date)
            if indi.birth_date < fam.marriage_date:
                out["message"] = passed_message.format(*msg_out)
                r["passed"].append(out)
            else:
                out["message"] = failed_message.format(*msg_out)
                r["failed"].append(out)

    return r


@story("Error US03")
def birth_before_death(gedcom_file):
    """ Birth should occur before death of an individual

    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    passed_message = "Individual {0} born {1} before {2} death on {3}"
    failed_message = "Individual {0} born {1} after {2} death on {3}"

    for indi in (i for i in gedcom_file.individuals if (i.has("birth_date") and i.has("death_date"))):
        out = {"xref": indi.xref, "birth_date": indi.birth_date.story_dict, "death_date": indi.death_date.story_dict}
        msg_out = (indi, indi.birth_date, indi.pronoun, indi.death_date)
        if indi.birth_date < indi.death_date:
            out["message"] = passed_message.format(*msg_out)
            r["passed"].append(out)
        else:
            out["message"] = failed_message.format(*msg_out)
            r["failed"].append(out)

    return r


@story("Error US04")
def marriage_before_divorce(gedcom_file):
    """ Marriage should occur before divorce of spouses, and divorce can only occur after marriage
    
    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    passed_message = "{0} with husband {1} and wife {2} has marriage on {3} before divorce on {4}"
    failed_message = "{0} with husband {1} and wife {2} has marriage on {3} after divorce on {4}"

    for fam in (f for f in gedcom_file.families if (f.has("marriage_date") and f.has("divorce_date"))):
        out = {"family_xref": fam.xref,
               "husband_xref": fam.husband.xref if fam.has("husband") else None,
               "wife_xref": fam.wife.xref if fam.has("wife") else None,
               "marriage_date": fam.marriage_date.story_dict, "divorce_date": fam.divorce_date.story_dict}
        msg_out = (fam, fam.husband, fam.wife, fam.marriage_date, fam.divorce_date)
        if fam.marriage_date < fam.divorce_date:
            out["message"] = passed_message.format(*msg_out)
            r["passed"].append(out)
        else:
            out["message"] = failed_message.format(*msg_out)
            r["failed"].append(out)

    return r


@story("Error US05")
def marriage_before_death(gedcom_file):
    """ Marriage should occur before death of either spouse

    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    pass_msg = "has {0} {1} with death {2} after marriage"
    fail_msg = "has {0} {1} with death {2} before marriage"

    for fam in (f for f in gedcom_file.families if f.has("marriage_date")):
        out = {"family_xref": fam.xref,
               "marriage_date": fam.marriage_date.story_dict,
               "husband_xref": fam.husband.xref if fam.has("husband") else None,
               "wife_xref": fam.wife.xref if fam.has("wife") else None,
               "husband_death_date": fam.husband.death_date.story_dict if fam.has("husband") and fam.husband.has("death_date") else None,
               "wife_death_date": fam.wife.death_date.story_dict if fam.has("wife") and fam.wife.has("death_date") else None}
        msg_intro = "{0} with marriage on {1} ".format(fam, fam.marriage_date)
        if fam.husband.has("death_date") and fam.wife.has("death_date"):
            if fam.marriage_date < fam.husband.death_date:
                passed, msg_husb = True, pass_msg.format("husband", fam.husband, fam.husband.death_date)
            else:
                passed, msg_husb = False, fail_msg.format("husband", fam.husband, fam.husband.death_date)
            if fam.marriage_date < fam.wife.death_date:
                passed, msg_wife = passed and True, pass_msg.format("wife", fam.wife, fam.wife.death_date)
            else:
                passed, msg_wife = passed and False, fail_msg.format("wife", fam.wife, fam.wife.death_date)
            out["message"] = msg_intro + msg_husb + " and " + msg_wife
            r["passed"].append(out) if passed else r["failed"].append(out)
        elif fam.husband.has("death_date"):
            if fam.marriage_date < fam.husband.death_date:
                out["message"] = msg_intro + pass_msg.format("husband", fam.husband, fam.husband.death_date)
                r["passed"].append(out)
            else:
                out["message"] = msg_intro + fail_msg.format("husband", fam.husband, fam.husband.death_date)
                r["failed"].append(out)
        elif fam.wife.has("death_date"):
            if fam.marriage_date < fam.wife.death_date:
                out["message"] = msg_intro + pass_msg.format("wife", fam.wife, fam.wife.death_date)
                r["passed"].append(out)
            else:
                out["message"] = msg_intro + fail_msg.format("wife", fam.wife, fam.wife.death_date)
                r["failed"].append(out)
    return r


@story("Error US06")
def divorce_before_death(gedcom_file):
    """ Divorce can only occur before death of both spouses
    
    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}

    pass_msg = "has {0} {1} with death {2} before divorce"
    fail_msg = "has {0} {1} with death {2} after divorce"

    for fam in (f for f in gedcom_file.families if f.has("divorce_date")):
        out = {"family_xref": fam.xref,
               "divorce_date": fam.divorce_date.story_dict,
               "husband_xref": fam.husband.xref if fam.has("husband") else None,
               "wife_xref": fam.wife.xref if fam.has("wife") else None,
               "husband_death_date": fam.husband.death_date.story_dict if fam.has("husband") and fam.husband.has("death_date") else None,
               "wife_death_date": fam.wife.death_date.story_dict if fam.has("husband") and fam.husband.has("death_date") else None}
        msg_intro = "{0} with divorce on {1} ".format(fam, fam.divorce_date)
        if fam.husband.has("death_date") and fam.wife.has("death_date"):
            if fam.husband.death_date < fam.divorce_date:
                passed, msg_husb = True, pass_msg.format("husband", fam.husband, fam.husband.death_date)
            else:
                passed, msg_husb = False, fail_msg.format("husband", fam.husband, fam.husband.death_date)
            if fam.wife.death_date < fam.divorce_date:
                passed, msg_wife = passed and True, pass_msg.format("wife", fam.wife, fam.wife.death_date)
            else:
                passed, msg_wife = passed and False, pass_msg.format("wife", fam.wife, fam.wife.death_date)
            out["message"] = msg_intro + msg_husb + " and " + msg_wife
            r["passed"].append(out) if passed else r["failed"].append(out)
        elif fam.husband.has("death_date"):
            if fam.husband.death_date < fam.divorce_date:
                out["message"] = msg_intro + pass_msg.format("husband", fam.husband, fam.husband.death_date)
                r["passed"].append(out)
            else:
                out["message"] = msg_intro + fail_msg.format("husband", fam.husband, fam.husband.death_date)
                r["failed"].append(out)
        elif fam.wife.has("death_date"):
            if fam.wife.death_date < fam.divorce_date:
                out["message"] = msg_intro + pass_msg.format("wife", fam.wife, fam.wife.death_date)
                r["passed"].append(out)
            else:
                out["message"] = msg_intro + fail_msg.format("wife", fam.wife, fam.wife.death_date)
                r["failed"].append(out)
    return r


@story("Error US07")
def less_then_150_years_old(gedcom_file):
    """ Death should be less than 150 years after birth for dead people, and
        current date should be less than 150 years after birth for all living people
    
    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for individual in gedcom_file.individuals_dict:
        birt_date = tools.get_birth_date(individual)
        deat_date = tools.get_death_date(individual)
        if birt_date:
            if deat_date:
                age = tools.years_between(birt_date.datetime, deat_date.datetime)
                output = {"individual_id": individual.get("xref_ID"),
                          "birth_date": birt_date.story_dict,
                          "death_date": deat_date.story_dict,
                          "age": age,
                          "name": tools.get_name(individual),
                          "sex": tools.get_sex(individual)
                          }
                r["passed"].append(output) if age < 150 else r["failed"].append(output)
            else:
                age = tools.years_between(birt_date.datetime, datetime.now())
                output = {"individual_id": individual.get("xref_ID"),
                          "birth_date": birt_date.story_dict,
                          "current_date": datetime.now().strftime("%d %b %Y").upper(),
                          "age": age,
                          "name": tools.get_name(individual),
                          "sex": tools.get_sex(individual)
                          }
                r["passed"].append(output) if age < 150 else r["failed"].append(output)
    return r


@story("Anomaly US08")
def birth_before_marriage_of_parents(gedcom_file):
    """ Child should be born after marriage of parents (and before their divorce)
    
    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for family in gedcom_file.families_dict:
        for child in family["children"]:
            child_birt_date = tools.get_birth_date(child)
            if child_birt_date and family["marr_date"]:
                output = {"family_id": family["xref"],
                          "mother_id": family["wife"].get("xref_ID"),
                          "father_id": family["husb"].get("xref_ID"),
                          "child_id": child.get("xref_ID"),
                          "child_birth_date": child_birt_date.story_dict,
                          "marriage_date": family["marr_date"].story_dict,
                          "father_name": tools.get_name(family["husb"]),
                          "mother_name": tools.get_name(family["wife"]),
                          "child_name": tools.get_name(child)
                          }
                passed = (family["marr_date"].datetime < child_birt_date.datetime)
                if family["div_date"]:
                    output["div"] = family["div_date"].story_dict
                    passed = passed and (family["div_date"].datetime > child_birt_date.datetime)
                r["passed"].append(output) if passed else r["failed"].append(output)
    return r


@story("Error US09")
def birth_before_death_of_parents(gedcom_file):
    """ Child should be born before death of mother and before 9 months after death of father
    
    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for family in gedcom_file.families_dict:
        mother_deat_date = tools.get_death_date(family["wife"])
        father_deat_date = tools.get_death_date(family["husb"])
        for child in family["children"]:
            output = {"family_id": family["xref"],
                      "mother_id": family["wife"].get("xref_ID"),
                      "father_id": family["husb"].get("xref_ID"),
                      "child_id": child.get("xref_ID"),
                      "father_name": tools.get_name(family["husb"]),
                      "mother_name": tools.get_name(family["wife"])
                      }
            child_birt_date = tools.get_birth_date(child)
            if child_birt_date:
                output["child_birth_date"] = child_birt_date.story_dict
                b4_moms_death = None
                b4_9_months_after_dads_death = None
                if mother_deat_date:
                    b4_moms_death = child_birt_date.datetime < mother_deat_date.datetime
                    output["mother_death_date"] = mother_deat_date.story_dict
                if father_deat_date:
                    b4_9_months_after_dads_death = ((father_deat_date.datetime - child_birt_date.datetime).days / 30) > 9
                    output["husband_death_date"] = father_deat_date.story_dict
                if ((b4_moms_death is True) or (b4_moms_death is None)) and (
                            (b4_9_months_after_dads_death is True) or (b4_9_months_after_dads_death is None)):
                    r["passed"].append(output)
                else:
                    r["failed"].append(output)
    return r


@story("Anomaly US10")
def marriage_after_14(gedcom_file):
    """ Marriage should be at least 14 years after birth of both spouses
    
    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for family in gedcom_file.families_dict:
        if family["marr_date"] is not None:
            w_birt_date = tools.get_birth_date(family["wife"])
            h_birt_date = tools.get_birth_date(family["husb"])
            w_marr_age = tools.years_between(family["marr_date"].datetime, w_birt_date.datetime) if w_birt_date else None
            h_marr_age = tools.years_between(family["marr_date"].datetime, h_birt_date.datetime) if h_birt_date else None
            output = {"family_id": family["xref"],
                      "wife_id": family["wife"].get("xref_ID"),
                      "husband_id": family["husb"].get("xref_ID"),
                      "wife_birth_date": w_birt_date.story_dict if w_birt_date else None,
                      "husband_birth_date": h_birt_date.story_dict if h_birt_date else None,
                      "wife_marriage_age": w_marr_age,
                      "husband_marriage_age": h_marr_age,
                      "wife_name": tools.get_name(family["wife"]),
                      "husband_name": tools.get_name(family["husb"])
                      }
            r["passed"].append(output) if ((w_marr_age is None) or (w_marr_age > 14)) and (
                (h_marr_age is None) or (h_marr_age > 14)) else r["failed"].append(output)
    return r


@story("Anomaly US11")
def no_bigamy(gedcom_file):
    """ Marriage should not occur during marriage to another spouse

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for individual in gedcom_file.find("tag", "INDI"):
        # Get all combinations of marriages this individual is or has been in
        for marr_1, marr_2 in combinations(tools.iter_marriage_timeframe_dict(individual), 2):
            # marriages start with marr_date
            # marriages end with div_date, or (if no div_date) the first deat_date of either spouse
            # check if datetime of these marriages overlap
            failed = (marr_1["start"]["dt"] <= marr_2["end"]["dt"]) and (marr_1["end"]["dt"] >= marr_2["start"]["dt"])
            # Don't include dt in user story
            marr_1["start"].pop("dt"), marr_1["end"].pop("dt"), marr_2["start"].pop("dt"), marr_2["end"].pop("dt")
            output = {"marr_1": marr_1, "marr_2": marr_2,
                      "name": tools.get_name(individual),
                      "sex": tools.get_sex(individual)
                      }
            r["failed"].append(output) if failed else r["passed"].append(output)
    return r


@story("Anomaly US12")
def parents_not_too_old(gedcom_file):
    """ Mother should be less than 60 years older than her children and
        father should be less than 80 years older than his children

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": [], "user_output": []}
    for family in gedcom_file.families_dict:
        m_birt_date = tools.get_birth_date(family["wife"])
        f_birt_date = tools.get_birth_date(family["husb"])
        for child in family["children"]:
            c_birt_date = tools.get_birth_date(child)
            if c_birt_date:
                m_yrs_older = tools.years_between(c_birt_date.datetime, m_birt_date.datetime) if m_birt_date else None
                f_yrs_older = tools.years_between(c_birt_date.datetime, f_birt_date.datetime) if f_birt_date else None
                output = {"family_id": family["xref"],
                          "child_id": child.get("xref_ID"),
                          "father_id": family["husb"].get("xref_ID"),
                          "mother_id": family["wife"].get("xref_ID"),
                          "child_birt_date": c_birt_date.story_dict,
                          "father_birt_date": f_birt_date.story_dict if f_birt_date else None,
                          "mother_birt_date": m_birt_date.story_dict if m_birt_date else None,
                          "father_years_older": f_yrs_older,
                          "mother_years_older": m_yrs_older,
                          "father_name": tools.get_name(family["husb"]),
                          "mother_name": tools.get_name(family["wife"])
                          }
            try:  # Python 2.7 | (None < 60) and (None < 80) is True
                r["passed"].append(output) if (m_yrs_older < 60) and (f_yrs_older < 80) else r["failed"].append(output)
            except TypeError:  # Python 3.0l | (None < 60) and (None < 80) raises TypeError
                r["passed"].append(output) if ((m_yrs_older is None) or (m_yrs_older < 60)) and (
                    (f_yrs_older is None) or (f_yrs_older < 80)) else r["failed"].append(output)
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

    fname = "Test_Files/My-Family-20-May-2016-697-Simplified-WithErrors.ged"
    try:
        g.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))


    #Sprint 1
    #dates_before_current_date(g)
    birth_before_marriage(g)
    birth_before_death(g)
    marriage_before_divorce(g)
    marriage_before_death(g)
    divorce_before_death(g)

    # Sprint 2
    #less_then_150_years_old(g)
    #birth_before_marriage_of_parents(g)
    #birth_before_death_of_parents(g)
    #marriage_after_14(g)
    #no_bigamy(g)
    #parents_not_too_old(g)
