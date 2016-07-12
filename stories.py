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

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()


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
        out = {"current_date": NOW_STRING, "type": date.parent.get("tag"), "date": date.story_dict}
        #TODO: Reimplement better
        #try:
        #    pp = date.parent.parent
        #    if pp.tag == "INDI":
        #        output["individual_id"] = date.parent.parent.get("xref_ID")
        #    elif pp.tag == "FAM":
        #        output["family_id"] = date.parent.parent.get("xref_ID")
        #except AttributeError:
        #    pass
        if date.datetime < NOW:
            out["message"] = "Date {0} is before {1} (current date)".format(tools.Date(date), NOW_STRING)
            r["passed"].append(out)
        else:
            out["message"] = "Date {0} is after {1} (current date)".format(tools.Date(date), NOW_STRING)
            r["failed"].append(out)
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
    passed_msg = "Individual {0} born {1} before {2} marriage ({3}) on {4}"
    failed_msg = "Individual {0} born {1} after {2} marriage ({3}) on {4}"
    for indi in (i for i in gedcom_file.individuals if i.has("birth_date")):
        for fam in (fam for fam in indi.families("FAMS") if fam.has("marriage_date")):
            out = {"indi": {"xref": indi.xref, "birth_date": indi.birth_date.story_dict},
                   "fam": {"xref": fam.xref, "marr_date": fam.marriage_date.story_dict}}
            msg_out = (indi, indi.birth_date, indi.pronoun, fam.xref, fam.marriage_date)
            if indi.birth_date < fam.marriage_date:
                out["message"] = passed_msg.format(*msg_out)
                r["passed"].append(out)
            else:
                out["message"] = failed_msg.format(*msg_out)
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
               "husband_death_date": fam.husband.death_date.story_dict if fam.has("husband") and fam.husband.has(
                       "death_date") else None,
               "wife_death_date": fam.wife.death_date.story_dict if fam.has("wife") and fam.wife.has(
                       "death_date") else None}
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
               "husband_death_date": fam.husband.death_date.story_dict if fam.has("husband") and fam.husband.has(
                       "death_date") else None,
               "wife_death_date": fam.wife.death_date.story_dict if fam.has("husband") and fam.husband.has(
                       "death_date") else None}
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
    r = {"passed": [], "failed": []}
    death_msg = "Individual {0} was born {1} and died {2} years later on {3}"
    alive_msg = "Individual {0} was born {1} and is {2} years old as of {3} (current date)"
    for indi in (i for i in gedcom_file.individuals if i.has("birth_date")):
        out = {"xref": indi.xref, "birth_date": indi.birth_date.story_dict}
        if indi.death_date:
            out.update({"death_date": indi.death_date.story_dict, "age_at_death": indi.age})
            out["message"] = death_msg.format(indi, indi.birth_date, indi.age, indi.death_date)
        else:
            out.update({"current_date": NOW_STRING, "current_age": indi.age})
            out["message"] = alive_msg.format(indi, indi.birth_date, indi.age, NOW_STRING)
        r["passed"].append(out) if indi.age < 150 else r["failed"].append(out)
    return r


@story("Anomaly US08")
def birth_before_marriage_of_parents(gedcom_file):
    """ Child should be born after marriage of parents (and before their divorce)

    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    div_msg = "{0} with marriage date {1} and divorce date {2} has a child {3} born {4}"
    mar_msg = "{0} with marriage date {1} has a child {2} born {3}"
    for fam in (f for f in gedcom_file.families if f.has("marriage_date")):
        for child in (c for c in fam.children if c.has("birth_date")):
            out = {"family_xref": fam.xref, "child_xref": child.xref,
                   "mother_xref": fam.wife.xref if fam.has("wife") else None,
                   "father_xref": fam.husband.xref if fam.has("husband") else None,
                   "child_birth_date": child.birth_date.story_dict, "marriage_date": fam.marriage_date.story_dict,
                   "divorce_date": fam.divorce_date.story_dict if fam.has("divorce_date") else None}
            passed = fam.marriage_date < child.birth_date
            if fam.divorce_date:
                out["message"] = div_msg.format(fam, fam.marriage_date, fam.divorce_date, child, child.birth_date)
                passed = passed and (fam.divorce_date > child.birth_date)
            else:
                out["message"] = mar_msg.format(fam, fam.marriage_date, child, child.birth_date)
            r["passed"].append(out) if passed else r["failed"].append(out)
    return r


@story("Error US09")
def birth_before_death_of_parents(gedcom_file):
    """ Child should be born before death of mother and before 9 months after death of father

    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    for fam in gedcom_file.families:
        for child in (c for c in fam.children if c.has("birth_date")):
            out = {"family_xref": fam.xref, "child": {"xref": child.xref, "birth_date": child.birth_date.story_dict}}
            chk_mom = fam.has("wife") and fam.wife.has("death_date")
            chk_dad = fam.has("husband") and fam.husband.has("death_date")
            mom_pass = child.birth_date < fam.wife.birth_date if chk_mom else None
            dad_pass = ((fam.husband.birth_date.dt - child.birth_date.dt).days / 30) > 9 if chk_dad else None
            msg = "Child {0} was born {1} and has".format(child, child.birth_date)
            if mom_pass is None:
                out["mother"] = {"xref": fam.wife.xref if fam.has("wife") else None, "birth_date": None}
                msg += " mother {0} with no death date".format(fam.wife)
            else:
                out["mother"] = {"xref": fam.wife.xref, "birth_date": fam.wife.birth_date}
                msg += " mother {0} with death date {1}".format(fam.wife, fam.wife.death_date)
            if dad_pass is None:
                out["father"] = {"xref": fam.husband.xref if fam.has("husband") else None, "birth_date": None}
                msg += " and father {0} with no death date.".format(fam.husband)
            else:
                out["father"] = {"xref": fam.husband.xref, "birth_date": fam.husband.birth_date}
                msg += " and father {0} with death date {1}.".format(fam.husband, fam.husband.death_date)
            out["message"] = msg
            passed = ((mom_pass is None) or (mom_pass is True)) and ((dad_pass is None) or (dad_pass is True))
            r["passed"].append(out) if passed else r["failed"].append(out)
    return r


@story("Anomaly US10")
def marriage_after_14(gedcom_file):
    """ Marriage should be at least 14 years after birth of both spouses

    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
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
                      "husband_name": tools.get_name(family["husb"])}
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
    r = {"passed": [], "failed": []}
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
    r = {"passed": [], "failed": []}
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


@story("Anomaly US13")
def siblings_spacing(gedcom_file):
    """ Birth dates of siblings should be more than 8 months apart or less than 2 days apart

    :note: Assume 8 months is (30 days)*(8 months)=(240 days)

    :sprint: 3
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    msg = "{0} has siblings born {1} days apart with {2} born on {3} and {4} born on {5}"
    for fam in gedcom_file.families:
        siblings = [c for c in fam.children if c.has("birth_date")]
        if len(siblings) >= 2:
            for sib_a, sib_b in combinations(siblings, 2):
                days = tools.days_between(sib_a.birth_date.dt, sib_b.birth_date.dt)
                out = {"family_xref": fam.xref,
                       "mother_xref": fam.wife.xref if fam.has("wife") else None,
                       "father_xref": fam.husband.xref if fam.has("husband") else None,
                       "days_apart": days,
                       "sibling_one": {"xref": sib_a.xref, "birth_date": sib_a.birth_date.story_dict},
                       "sibling_two": {"xref": sib_a.xref, "birth_date": sib_a.birth_date.story_dict},
                       "message": msg.format(fam, days, sib_a, sib_a.birth_date, sib_b, sib_b.birth_date)}
                r["passed"].append(out) if (days < 2) or (days > 240) else r["failed"].append(out)
    return r


@story("Anomaly US14")
def multiple_births_less_than_5(gedcom_file):
    """ No more than five siblings should be born at the same time

    :sprint: 3
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US15")
def fewer_than_15_siblings(gedcom_file):
    """ There should be fewer than 15 siblings in a family

    :sprint: 3
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US16")
def male_last_names(gedcom_file):
    """ All male members of a family should have the same last name
    
    :sprint: 3
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File
    
    # loop through  families
    # get all the names of the husbands of the family
    # get all the names of the male children in the family
    # compare the surnames of the husbands and that of the male children
    # error or failed message if the names of the husband and male children are not the same
    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US17")
def no_marriages_to_descendants(gedcom_file):
    """ Parents should not marry any of their descendants

    :sprint: 3
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
# For each individual:
    # Get a list of their children (and grandchildren? How many generations to check?)
    # Get a list of their spouses
    # See if any names appear in both lists <- Check unique IDs
    return r


@story("Anomaly US18")
def siblings_should_not_marry(gedcom_file):
    """ Siblings should not marry one another

    :sprint: 3
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    # Get sibilings
    # Get an individual's marriages
    # Check if any overlap

# For reference only
############## From US13
##    msg = "{0} has siblings born {1} days apart with {2} born on {3} and {4} born on {5}"
##    for fam in gedcom_file.families:
##        siblings = [c for c in fam.children if c.has("birth_date")]
##        if len(siblings) >= 2:
##            for sib_a, sib_b in combinations(siblings, 2):
##                days = tools.days_between(sib_a.birth_date.dt, sib_b.birth_date.dt)
##                out = {"family_xref": fam.xref,
##                       "mother_xref": fam.wife.xref if fam.has("wife") else None,
##                       "father_xref": fam.husband.xref if fam.has("husband") else None,
##                       "days_apart": days,
##                       "sibling_one": {"xref": sib_a.xref, "birth_date": sib_a.birth_date.story_dict},
##                       "sibling_two": {"xref": sib_a.xref, "birth_date": sib_a.birth_date.story_dict},
##                       "message": msg.format(fam, days, sib_a, sib_a.birth_date, sib_b, sib_b.birth_date)}
##                r["passed"].append(out) if (days < 2) or (days > 240) else r["failed"].append(out)
##
############## From US02
##    passed_message = "Individual {0} born {1} before {2} marriage ({3}) on {4}"
##    failed_message = "Individual {0} born {1} after {2} marriage ({3}) on {4}"
##    for indi in (i for i in gedcom_file.individuals if i.has("birth_date")):
##        for fam in (fam for fam in indi.families("FAMS") if fam.has("marriage_date")):
##            out = {"indi": {"xref": indi.xref, "birth_date": indi.birth_date.story_dict},
##                   "fam": {"xref": fam.xref, "marr_date": fam.marriage_date.story_dict}}
##            msg_out = (indi, indi.birth_date, indi.pronoun, fam.xref, fam.marriage_date)
##            if indi.birth_date < fam.marriage_date:
##                out["message"] = passed_message.format(*msg_out)
##                r["passed"].append(out)
##            else:
##                out["message"] = failed_message.format(*msg_out)
##                r["failed"].append(out)
##
##############

    passed_message = "Individual {0} is not married to any of {1} siblings"
    failed_message = "Individual {0} is married to {1} sibling {2}"
    for fam in gedcom_file.families:
        for indi in fam.children:
            for spouse in indi.spouses:
                for sibling in (s for s in fam.children if s.xref != indi.xref):
                    out = {"indi": {"xref": indi.xref},
                           "fam": {"xref": fam.xref}}
                    msg_out = (indi, indi.pronoun, sibling)
                    if indi.xref == spouse.xref:
                        print "BAD: ", sibling, spouse
                        out["message"] = failed_message.format(*msg_out)
                        r["failed"].append(out)
                    else:
                        print "GOOD: ", sibling, spouse
                        out["message"] = passed_message.format(*msg_out)
                        r["passed"].append(out)
        print

# For each individual:
    # Get a list of their siblings
    # Get a list of their spouses
    # See if any names appear in both lists <- actually need to compare IDs, because two people could have the same name
    # (Unlikely for siblings, but... not impossible, in some specific situations. But the IDs are unique.)

    return r


@story("Anomaly US19")
def first_cousins_should_not_marry(gedcom_file):
    """ First cousins should not marry one another

    :sprint: 4
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US20")
def aunts_and_uncles(gedcom_file):
    """ Aunts and uncles should not marry their nieces or nephews

    :sprint: 4
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Error US21")
def correct_gender_for_role(gedcom_file):
    """ Husband in family should be male and wife in family should be female

    :sprint: 4
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Error US22")
def unique_ids(gedcom_file):
    """ All individual IDs should be unique and all family IDs should be unique

    :sprint: 4
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US23")
def unique_name_and_birth_date(gedcom_file):
    """ No more than one individual with the same name and birth date should appear in a GEDCOM file

    :sprint: 4
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


@story("Anomaly US24")
def unique_families_by_spouses(gedcom_file):
    """ No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file

    :sprint: 4
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: gedcom.File

    """
    r = {"passed": [], "failed": []}
    # ...
    return r


# USER STORIES BELOW NOT IN ASSIGNMENT SCOPE


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
    g = gedcom.File()
    fname = "Test_Files/My-Family-20-May-2016-697-Simplified-WithErrors.ged"
    try:
        g.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))

    # Sprint 1 - Stories
    dates_before_current_date(g)
    birth_before_marriage(g)
    birth_before_death(g)
    marriage_before_divorce(g)
    marriage_before_death(g)
    divorce_before_death(g)

    # Sprint 2 - Stories
    less_then_150_years_old(g)
    birth_before_marriage_of_parents(g)
    birth_before_death_of_parents(g)
    marriage_after_14(g)
    no_bigamy(g)
    parents_not_too_old(g)

    # Sprint 3 - Stories
    # siblings_spacing(g)
    # multiple_births_less_than_5(g)
    # fewer_than_15_siblings(g)
    # male_last_names(g)
    # no_marriages_to_descendants(g)
    # siblings_should_not_marry(g)

    # Sprint 4 - Stories
    # first_cousins_should_not_marry(g)
    # aunts_and_uncles(g)
    # correct_gender_for_role(g)
    # unique_ids(g)
    # unique_name_and_birth_date(g)
    # unique_families_by_spouses(g)
