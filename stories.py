"""
Story Functions
"""
import logging
import sys
from datetime import datetime
from itertools import combinations, groupby
import gedcom

__author__ = "Adam Burbidge, Constantine Davantzis, Vibha Ravi"

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()

# Log Constants
LOG_HEADING = '\n### {0}: {1} ###'
LOG_ENTRY = '\t > {0}'
LOG_BULLET = '\t\t * {0}'
LOG_BULLET_ALT = '\t\t * {0}: {1}'

# Initiate Log
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)
logger.propagate = False


def individual_summary(gedcom_file):
    # TODO: Write Docstring
    # TODO: add message and bullets into summary
    r = []
    logger.info(LOG_HEADING.format("Summary", "Individuals"))
    for indi in gedcom_file.individuals:
        r.append(indi.summary)
        logger.info(LOG_ENTRY.format(indi))
        logger.info(LOG_BULLET_ALT.format("Gender", indi.sex))
        logger.info(LOG_BULLET_ALT.format("Birth date", indi.birth_date))
        if indi.has("death_date"):
            logger.info(LOG_BULLET_ALT.format("Death date", indi.death_date))
            logger.info(LOG_BULLET_ALT.format("Age at death", indi.age))
        else:
            logger.info(LOG_BULLET_ALT.format("Current age", indi.age))
        spouses_str = ", ".join(map(str, indi.spouses))
        if spouses_str:
            logger.info(LOG_BULLET_ALT.format("Spouses", spouses_str))
        spouse_in_str = ", ".join(map(str, indi.families("FAMS")))
        if spouse_in_str:
            logger.info(LOG_BULLET_ALT.format("Spouse in", spouse_in_str))
        child_in_str = ", ".join(map(str, indi.families("FAMC")))
        if child_in_str:
            logger.info(LOG_BULLET_ALT.format("Child in", child_in_str))
    return r


def family_summary(gedcom_file):
    # TODO: Write Docstring
    r = []
    # TODO: add message and bullets into summary
    logger.info(LOG_HEADING.format("Summary", "Families"))
    for fam in gedcom_file.families:
        r.append(fam.summary)
        logger.info(LOG_ENTRY.format(fam))
        logger.info(LOG_BULLET_ALT.format("Husband", fam.husband))
        logger.info(LOG_BULLET_ALT.format("Wife", fam.wife))
        for i, child in enumerate(fam.children):
            logger.info(LOG_BULLET_ALT.format("Child {0}".format(i + 1), child))
    return r


def story(id_):
    """ Function decorator used to find both outcomes of a story, and log and return the results """

    def story_decorator(func):
        def func_wrapper(gedcom_file):
            if type(gedcom_file) is not gedcom.parser.File:
                raise TypeError("Story function must be provided a gedcom file object.")
            r = {"id": id_, "name": func.__name__, "output": func(gedcom_file)}

            # Log Text Results To User Output
            logger.info(LOG_HEADING.format(r["id"], r["name"].replace("_", " ").title()))
            # TODO: log story description
            logger.info("~~~~")
            logger.debug("[passed]")
            for entry in r["output"]["passed"]:
                h2 = LOG_ENTRY.format(entry.get("message", entry))
                logger.debug(h2)
                for bullet in entry.get("bullets", []):
                    logger.debug(LOG_BULLET.format(bullet))
            logger.info("[failed]")
            for entry in r["output"]["failed"]:
                h2 = LOG_ENTRY.format(entry.get("message", entry))
                logger.info(h2)
                for bullet in entry.get("bullets", []):
                    logger.info(LOG_BULLET.format(bullet))
            logger.info("~~~~")

            # Return Results Dictionary
            return r

        return func_wrapper

    return story_decorator


@story("Error US01")
def dates_before_current_date(gedcom_file):
    """ Dates (birth, marriage, divorce, death) should not be after the current date

    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = "{0}{1} has a {2} date {3} the current date".format
    bul = ["Current Date is {0} (date script ran)".format, "{0} date is {1}".format]

    for date in gedcom_file.dates:
        if date.type in ("birth", "marriage", "divorce", "death"):
            out = {"bullets": [bul[0](NOW_STRING), bul[1](date.type.capitalize(), date)]}
            passed, word = (True, "before") if date.dt < NOW else (True, "on") if date.dt == NOW else (False, "after")
            if type(date.belongs_to) is gedcom.tag.Individual:
                out["message"] = msg("Individual ", date.belongs_to, date.type, word)
            elif type(date.belongs_to) is gedcom.tag.Family:
                out["message"] = msg("", date.belongs_to, date.type, word)
            else:
                out["message"] = msg("", "Gedcom File", date.type, word)

            r["passed"].append(out) if passed else r["failed"].append(out)
    return r


@story("Error US02")
def birth_before_marriage(gedcom_file):
    """ Birth should occur before marriage of an individual

    :sprint: 1
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"passed": "{0} was born before {1} marriage".format,
           "failed": "{0} was born after {1} marriage".format}
    bul = "{0} date is {1}".format

    for indi in gedcom_file.individuals:
        if not indi.has("birth_date"):
            continue  # Project Overview Assumptions not met
        for fam in indi.families("FAMS"):
            if not fam.has("marriage_date"):
                continue  # Project Overview Assumptions not met
            status = "passed" if indi.birth_date < fam.marriage_date else "failed"
            r[status].append({"message": msg[status](indi, indi.pronoun),
                              "bullets": [bul("Birth", indi.birth_date), bul("Marriage", indi.birth_date)]})

    return r


@story("Error US03")
def birth_before_death(gedcom_file):
    """ Birth should occur before death of an individual

    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"passed": "{0} was born before {1} death".format,
           "failed": "{0} was born after {1} death".format}
    bul = "{0} date is {1}".format

    for indi in gedcom_file.individuals:
        if not indi.has("birth_date"):
            continue  # Project Overview Assumptions not met
        if not indi.has("death_date"):
            continue  # Individual not applicable to story
        status = "passed" if indi.birth_date < indi.death_date else "failed"
        r[status].append({"message": msg[status](indi, indi.pronoun),
                          "bullets": [bul("Birth", indi.birth_date), bul("Death", indi.death_date)]})

    return r


@story("Error US04")
def marriage_before_divorce(gedcom_file):
    """ Marriage should occur before divorce of spouses, and divorce can only occur after marriage

    :sprint: 1
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"passed": "{0} with husband {1} and wife {2} has marriage on {3} before divorce on {4}".format,
           "failed": "{0} with husband {1} and wife {2} has marriage on {3} after divorce on {4}".format}
    for fam in gedcom_file.families:

        if not fam.has("marriage_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("divorce_date"):
            continue  # Family not applicable to story

        status = "passed" if fam.marriage_date < fam.divorce_date else "failed"
        r[status].append({"message": msg[status](fam, fam.husband, fam.wife, fam.marriage_date, fam.divorce_date)})

    return r


@story("Error US05")
def marriage_before_death(gedcom_file):
    """ Marriage should occur before death of either spouse

    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg_intro = "{0} with marriage on {1} ".format
    pass_msg = "has {0} {1} with death {2} after marriage".format
    fail_msg = "has {0} {1} with death {2} before marriage".format
    for fam in gedcom_file.families:

        if not fam.has("marriage_date"):
            continue  # Project Overview Assumptions not met

        intro = msg_intro(fam, fam.marriage_date)
        if fam.husband.has("death_date") and fam.wife.has("death_date"):
            if fam.marriage_date < fam.husband.death_date:
                passed, msg_husb = True, pass_msg("husband", fam.husband, fam.husband.death_date)
            else:
                passed, msg_husb = False, fail_msg("husband", fam.husband, fam.husband.death_date)
            if fam.marriage_date < fam.wife.death_date:
                passed, msg_wife = passed and True, pass_msg("wife", fam.wife, fam.wife.death_date)
            else:
                passed, msg_wife = passed and False, fail_msg("wife", fam.wife, fam.wife.death_date)
            status = "passed" if passed else "failed"
            r[status].append({"message": intro + msg_husb + " and " + msg_wife})
        elif fam.husband.has("death_date"):
            if fam.marriage_date < fam.husband.death_date:
                r["passed"].append(
                        {"message": intro + pass_msg("husband", fam.husband, fam.husband.death_date)})
            else:
                r["failed"].append(
                        {"message": intro + fail_msg("husband", fam.husband, fam.husband.death_date)})
        elif fam.wife.has("death_date"):
            if fam.marriage_date < fam.wife.death_date:
                r["passed"].append({"message": intro + pass_msg("wife", fam.wife, fam.wife.death_date)})
            else:
                r["failed"].append({"message": intro + fail_msg("wife", fam.wife, fam.wife.death_date)})
    return r


@story("Error US06")
def divorce_before_death(gedcom_file):
    """ Divorce can only occur before death of both spouses

    :sprint: 1
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg_intro = "{0} with divorce on {1} ".format
    pass_msg = "has {0} {1} with death {2} before divorce".format
    fail_msg = "has {0} {1} with death {2} after divorce".format
    for fam in gedcom_file.families:

        if not fam.has("divorce_date"):
            continue  # Family not applicable to story

        intro = msg_intro(fam, fam.divorce_date)
        if fam.husband.has("death_date") and fam.wife.has("death_date"):
            if fam.husband.death_date < fam.divorce_date:
                passed, msg_husb = True, pass_msg("husband", fam.husband, fam.husband.death_date)
            else:
                passed, msg_husb = False, fail_msg("husband", fam.husband, fam.husband.death_date)
            if fam.wife.death_date < fam.divorce_date:
                passed, msg_wife = passed and True, pass_msg("wife", fam.wife, fam.wife.death_date)
            else:
                passed, msg_wife = passed and False, pass_msg("wife", fam.wife, fam.wife.death_date)
            status = "passed" if passed else "failed"
            r[status].append({"message": intro + msg_husb + " and " + msg_wife})
        elif fam.husband.has("death_date"):
            if fam.husband.death_date < fam.divorce_date:
                r["passed"].append({"message": intro + pass_msg("husband", fam.husband, fam.husband.death_date)})
            else:
                r["failed"].append({"message": intro + fail_msg("husband", fam.husband, fam.husband.death_date)})
        elif fam.wife.has("death_date"):
            if fam.wife.death_date < fam.divorce_date:
                r["passed"].append({"message": intro + pass_msg("wife", fam.wife, fam.wife.death_date)})
            else:
                r["failed"].append({"message": intro + fail_msg("wife", fam.wife, fam.wife.death_date)})

    return r


@story("Error US07")
def less_then_150_years_old(gedcom_file):
    """ Death should be less than 150 years after birth for dead people, and
        current date should be less than 150 years after birth for all living people

    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"death": "Individual {0} was born {1} and died {2} years later on {3}".format,
           "alive": "Individual {0} was born {1} and is {2} years old as of {3} (current date)".format}

    for indi in gedcom_file.individuals:
        if not indi.has("birth_date"):
            continue  # Project Overview Assumptions not met
        out = {}
        if indi.has("death_date"):
            out["message"] = msg["death"](indi, indi.birth_date, indi.age, indi.death_date)
        else:
            out["message"] = msg["alive"](indi, indi.birth_date, indi.age, NOW_STRING)
        r["passed"].append(out) if indi.age < 150 else r["failed"].append(out)

    return r


@story("Anomaly US08")
def birth_before_marriage_of_parents(gedcom_file):
    """ Child should be born after marriage of parents (and before their divorce)

    :sprint: 2
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    div_msg = "{0} with marriage date {1} and divorce date {2} has a child {3} born {4}"
    mar_msg = "{0} with marriage date {1} has a child {2} born {3}"
    for fam in (f for f in gedcom_file.families if f.has("marriage_date")):

        if not fam.has("marriage_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("husband") or not fam.husband.has("birth_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("wife") or not fam.wife.has("birth_date"):
            continue  # Project Overview Assumptions not met

        for child in (c for c in fam.children if c.has("birth_date")):
            out = {}
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
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    for fam in gedcom_file.families:
        for child in (c for c in fam.children if c.has("birth_date")):
            chk_mom = fam.has("wife") and fam.wife.has("death_date")
            chk_dad = fam.has("husband") and fam.husband.has("death_date")
            mom_pass = child.birth_date < fam.wife.birth_date if chk_mom else None
            dad_pass = ((fam.husband.birth_date.dt - child.birth_date.dt).days / 30) > 9 if chk_dad else None
            msg = "{0} has Child {1} with birth date {2} and has".format(fam, child, child.birth_date)

            if mom_pass is None:
                msg += " mother {0} with no death date".format(fam.wife)
            else:
                msg += " mother {0} with death date {1}".format(fam.wife, fam.wife.death_date)

            if dad_pass is None:
                msg += " and father {0} with no death date.".format(fam.husband)
            else:
                msg += " and father {0} with death date {1}.".format(fam.husband, fam.husband.death_date)

            passed = ((mom_pass is None) or (mom_pass is True)) and ((dad_pass is None) or (dad_pass is True))
            status = "passed" if passed else "failed"
            r[status].append({"message": msg})

    return r


@story("Anomaly US10")
def marriage_after_14(gedcom_file):
    """ Marriage should be at least 14 years after birth of both spouses

    :sprint: 2
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = "{0} has marriage date {1}".format
    bul = "{0} {1} born {2} [married at {3} years old]".format

    for fam in gedcom_file.families:
        # Check Project Overview Assumptions
        if not fam.has("marriage_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("husband") or not fam.husband.has("birth_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("wife") or not fam.wife.has("birth_date"):
            continue  # Project Overview Assumptions not met

        status = "passed" if (fam.wife_marriage_age > 14) and (fam.husband_marriage_age > 14) else "failed"
        r[status].append({"message": msg(fam, fam.marriage_date),
                          "bullets": [bul("Wife", fam.wife, fam.wife.birth_date, fam.wife_marriage_age),
                                      bul("Husband", fam.husband, fam.husband.birth_date, fam.husband_marriage_age)]})
    return r


@story("Anomaly US11")
def no_bigamy(gedcom_file):
    """ Marriage should not occur during marriage to another spouse

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    msg = {"passed": "Individual {0} has overlapping marriages".format,
           "failed": "Individual {0} has non-overlapping marriages".format}

    bul = "{0} marriage starts {1} and ends {2} (line {3}) because {4}".format

    for indi in gedcom_file.individuals:
        # Get all combinations of marriages this individual is or has been in
        for fam_1, fam_2 in combinations(indi.families("FAMS"), 2):

            # Check Project Overview Assumptions
            if (not fam_1.has("marriage_date")) or (not fam_2.has("marriage_date")):
                continue  # Project Overview Assumptions not met

            s1, e1 = fam_1.marriage_date, fam_1.marriage_end
            s2, e2 = fam_2.marriage_date, fam_2.marriage_end

            b = [bul(fam_1, s1, e1["story_dict"].get("line_value"), e1["story_dict"]["line_number"], e1["reason"]),
                 bul(fam_2, s2, e2["story_dict"].get("line_value"), e2["story_dict"]["line_number"], e2["reason"])]

            status = "failed" if (s1.dt <= e2["dt"]) and (e1["dt"] >= s2.dt) else "passed"
            r[status].append({"message": msg[status](indi), "bullets": b})

    return r


@story("Anomaly US12")
def parents_not_too_old(gedcom_file):
    """ Mother should be less than 60 years older than her children and
        father should be less than 80 years older than his children

    :sprint: 2
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = "{0} with child {1} born {2} has mother {3} born {4} [{5} years older than child] " \
          + "and father {6} born {7} [{8} years older than child]."
    msg = msg.format
    for fam in gedcom_file.families:
        # Check Project Overview Assumptions
        if not fam.has("marriage_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("husband") or not fam.husband.has("birth_date"):
            continue  # Project Overview Assumptions not met
        if not fam.has("wife") or not fam.wife.has("birth_date"):
            continue  # Project Overview Assumptions not met

        for child in fam.children:
            # Check Project Overview Assumptions
            if not child.has("birth_date"):
                continue  # Project Overview Assumptions not met

            m_yrs_older = gedcom.tools.years_between(child.birth_date.dt, fam.wife.birth_date.dt)
            f_yrs_older = gedcom.tools.years_between(child.birth_date.dt, fam.husband.birth_date.dt)
            status = "passed" if (m_yrs_older < 60) and (f_yrs_older < 80) else "failed"
            r[status].append({"message": msg(fam, child, child.birth_date, fam.wife, fam.wife.birth_date, m_yrs_older,
                                             fam.husband, fam.husband.birth_date, f_yrs_older)})

    return r


@story("Anomaly US13")
def siblings_spacing(gedcom_file):
    """ Birth dates of siblings should be more than 8 months apart or less than 2 days apart

    :note: Assume 8 months is (30 days)*(8 months)=(240 days)

    :sprint: 3
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = "{0} has siblings born {1} apart ({2} days)".format
    bullet_msg = "Sibling {0} born {1}".format
    for fam in gedcom_file.families:
        for sib_a, sib_b in combinations((c for c in fam.children if c.has("birth_date")), 2):
            days = gedcom.tools.days_between(sib_a.birth_date.dt, sib_b.birth_date.dt)
            out = {"bullets": [bullet_msg(sib_a, sib_a.birth_date), bullet_msg(sib_b, sib_b.birth_date)]}
            if days < 2:
                out["message"] = msg(fam, "less than two days", days, sib_a, sib_a.birth_date, sib_b, sib_b.birth_date)
                r["passed"].append(out)
            elif days > 240:
                out["message"] = msg(fam, "more than 8 months", days, sib_a, sib_a.birth_date, sib_b, sib_b.birth_date)
                r["passed"].append(out)
            else:
                out["message"] = msg(fam, "less than 8 months but more than two days", days, sib_a, sib_a.birth_date,
                                     sib_b, sib_b.birth_date)
                r["failed"].append(out)
    return r


@story("Anomaly US14")
def less_than_5_multiple_births(gedcom_file):
    """ No more than five siblings should be born at the same time

    :sprint: 3
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    msg_pass = "{0} has no more than 5 siblings born on the same date, with {1} {2} born on {3}".format
    msg_fail = "{0} has more than 5 siblings born on the same date, with {1} siblings born on {2}".format

    for fam in gedcom_file.families:
        group = groupby(sorted(fam.children, key=lambda x: x.birth_date.dt), lambda x: x.birth_date)
        for date, born_on_date in ((date, list(born_on_date)) for date, born_on_date in group):
            i = len(born_on_date)
            out = {"bullets": ["Sibling {0} born {1}".format(c, c.birth_date) for c in born_on_date]}
            if i <= 5:
                out["message"] = msg_pass(fam, i, "sibling" if i == 1 else "siblings", date.val)
                r["passed"].append(out)
            else:
                out["message"] = msg_fail(fam, i, date.val)
                r["failed"].append(out)

    return r


@story("Anomaly US15")
def fewer_than_15_siblings(gedcom_file):
    """ There should be fewer than 15 siblings in a family

    :sprint: 3
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = ["{0} has {1} children".format, "{0} has {1} child".format]
    bul = "Child {0}: {1}".format
    for fam in gedcom_file.families:
        i = len(fam.children)
        out = {"message": msg[1](fam, i) if i == 1 else msg[0](fam, i),
               "bullets": [bul(i + 1, child) for i, child in enumerate(fam.children)]}
        r["passed"].append(out) if i < 15 else r["failed"].append(out)
    return r


@story("Anomaly US16")
def male_last_names(gedcom_file):
    """ All male members of a family should have the same last name

    :sprint: 3
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    sib_msg = "{0} with male siblings {1} and {2}{3} have the same surname".format  # Sibling Check Message Formatter
    dad_msg = "{0} with father {1} and son {2}{3} have the same surname".format  # Dad/Son Check Message Formatter

    for fam in gedcom_file.families:

        # Compare children to each other
        for sib_a, sib_b in combinations(fam.male_children, 2):
            if sib_a.name.surname == sib_b.name.surname:
                r["passed"].append({"message": sib_msg(fam, sib_a, sib_b, "")})
            else:
                r["failed"].append({"message": sib_msg(fam, sib_a, sib_b, " do not")})

        # Check Project Overview Assumptions
        if not fam.has("husband") or not fam.husband.has("name"):
            continue  # Project Overview Assumptions not met
        if not fam.husband.has("sex") or fam.husband.sex.val != "M":
            continue  # Project Overview Assumptions not met

        # Compare father to each child
        for child in fam.male_children:
            if fam.husband.name.surname == child.name.surname:
                r["passed"].append({"message": dad_msg(fam, fam.husband, child, "")})
            else:
                r["failed"].append({"message": dad_msg(fam, fam.husband, child, " do not")})

    return r


@story("Anomaly US17")
def no_marriages_to_descendants(gedcom_file):
    """ Parents should not marry any of their descendants

    :sprint: 3
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    passed_message = "Individual {0} is not married to any descendants".format
    failed_message = "Individual {0} is married to {1} of {2} descendants".format
    bullet = "Married to {0} {1} in {2}".format
    for indi in gedcom_file.individuals:
        b = []
        for descendant in indi.descendants:
            for fam, spouse in indi.families_and_spouses:
                if spouse == descendant:
                    b.append(bullet(descendant.descendant_title, descendant, fam))
        if len(b) == 0:
            r["passed"].append({"message": passed_message(indi), "bullets": b})
        else:
            r["failed"].append({"message": failed_message(indi, len(b), len(indi.descendants)), "bullets": b})
    return r


@story("Anomaly US18")
def siblings_should_not_marry(gedcom_file):
    """ Siblings should not marry one another

    :sprint: 3
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    passed_msg = "Individual {0} is married to none of {1} siblings".format
    failed_msg = "Individual {0} is married to {1} of {2} siblings".format
    bullet = "Married to sibling {0}. Sibling in {1}, Married in {2}".format
    # Keep track of individuals checked just in case individual is a child in multiple families (ERROR)
    checked = []
    for fam in gedcom_file.families:
        for indi in (i for i in fam.children if (i not in checked)):
            siblings = [s for s in fam.children if s.xref != indi.xref]
            checked.append(indi)
            b = []
            for spouse_fam, spouse in indi.families_and_spouses:
                for sibling in siblings:
                    if sibling == spouse:
                        b.append(bullet(sibling, fam, spouse_fam))
            if len(b) == 0:
                r["passed"].append({"message": passed_msg(indi, len(siblings))})
            else:
                r["failed"].append({"message": failed_msg(indi, len(b), len(siblings)), "bullets": b})

    return r


@story("Anomaly US19")
def first_cousins_should_not_marry(gedcom_file):
    """ First cousins should not marry one another

    :sprint: 4
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    msg = {"passed": "{0} is not married to any cousins".format,
           "failed": "{0} is married to {1} {2}".format}

    bul = "{0} is married to cousin {1} in {2}".format

    for indi in gedcom_file.individuals:
        spouses = list(indi.spouses)
        bullets = [bul(indi, c, spouses.pop(spouses.index(c)).spouse_family) for c in indi.cousins if c in spouses]
        count = len(bullets)
        if count == 0:
            r["passed"].append({"message": msg["passed"](indi)})
        elif count == 1:
            r["failed"].append({"message": msg["failed"](indi, count, "cousin"), "bullets": bullets})
        else:
            r["failed"].append({"message": msg["failed"](indi, count, "cousins"), "bullets": bullets})

    return r


@story("Anomaly US20")
def aunts_and_uncles(gedcom_file):
    """ Aunts and uncles should not marry their nieces or nephews

    :sprint: 4
    :author: Constantine Davantzis

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    msg = {"passed": "{0} is not married to any aunt(s) and/or uncle(s)".format,
           "failed": "{0} is married to {1} aunt(s) and/or uncle(s)".format}

    bul = "{0} is married to {1} {2} in {3}".format

    for indi in gedcom_file.individuals:
        spouses = list(indi.spouses)
        bullets = [bul(indi, x.aunt_or_uncle, x, spouses.pop(spouses.index(x)).spouse_family) for x in
                   indi.aunts_and_uncles if x in spouses]
        count = len(bullets)
        if count == 0:
            r["passed"].append({"message": msg["passed"](indi)})
        else:
            r["failed"].append({"message": msg["failed"](indi, count), "bullets": bullets})

    return r


@story("Error US21")
def correct_gender_for_role(gedcom_file):
    """ Husband in family should be male and wife in family should be female

    :sprint: 4
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}

    msg = {"passed": "{0} has traditional gender roles".format,
           "failed": "{0} does not have traditional gender roles".format}

    bul = "{0} {1} is {2}".format

    for fam in gedcom_file.families:

        # Check Project Overview Assumptions
        if not fam.has("wife") or not fam.wife.has("sex"):
            continue  # Project Overview Assumptions not met
        if not fam.has("husband") or not fam.husband.has("sex"):
            continue  # Project Overview Assumptions not met

        status = "passed" if (fam.husband.sex.val == "M") and (fam.wife.sex.val == "F") else "failed"
        r[status].append({"message": msg[status](fam, fam.husband, fam.wife),
                          "bullets": [bul("Husband", fam.husband, fam.husband.sex),
                                      bul("Wife", fam.wife, fam.wife.sex)]})

    return r


@story("Error US22")
def unique_ids(gedcom_file):
    """ All individual IDs should be unique and all family IDs should be unique

    :sprint: 4
    :author: vibharavi

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """

    def _matches(a):
        m = {}
        [m[b.xref].append(b) if b.xref in m else m.update({b.xref: [b]}) for b in a]
        return m

    def _sort(x):
        try:
            return int(x[0][2:].replace("@", ""))
        except ValueError:
            return x

    r = {"passed": [], "failed": []}

    l = [{"items": gedcom_file.individuals,
          "msg": {"passed": "{0} individual found with xref {1}".format,
                  "failed": "{0} individuals found with xref {1}".format}},
         {"items": gedcom_file.families,
          "msg": {"passed": "{0} family found with xref {1}".format,
                  "failed": "{0} families found with xref {1}".format}}]

    for d in l:
        for xref, with_xref in iter(sorted(_matches(d["items"]).iteritems(), key=_sort)):
            status = "passed" if len(with_xref) == 1 else "failed"
            r[status].append({"message": d["msg"][status](len(with_xref), xref), "bullets": map(str, with_xref)})

    return r


def matches(a, key):
    """ Group Matches """
    m = {}
    for b in a:
        try:
            k = key(b)
        except AttributeError as e:
            #logger.warning("{0} does not meet project standards".format(b))
            pass
        else:
            m[k].append(b) if k in m else m.update({k: [b]})
    for key, items in sorted(m.iteritems()):
        yield key, items, len(items)


@story("Anomaly US23")
def unique_name_and_birth_date(gedcom_file):
    """ No more than one individual with the same name and birth date should appear in a GEDCOM file

    :sprint: 4
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"passed": "{0} individual found with the name {1} and birth date {2}".format,
           "failed": "{0} individuals found with the name {1} and birth date {2}".format}
    bul = "{0.xref} - Name: {0.name} Birth Date: {0.birth_date}".format

    for key, items, count in matches(gedcom_file.individuals, lambda x: (x.name.val.replace("/", ""), x.birth_date.val)):
        status = "passed" if count == 1 else "failed"
        r[status].append({"message": msg[status](count, key[0], key[1]), "bullets": map(bul, items)})
        
    return r


@story("Anomaly US24")
def unique_families_by_spouses(gedcom_file):
    """ No more than one family with the same spouses by name and the same marriage date should appear in a GEDCOM file

    :sprint: 4
    :author: Adam Burbidge

    :param gedcom_file: GEDCOM File to check
    :type gedcom_file: parser.File

    """
    r = {"passed": [], "failed": []}
    msg = {"passed": "{0} family found with the husband name {1}, wife name {2} and marriage date {3}".format,
           "failed": "{0} families found with the husband name {1}, wife name {2} and marriage date {3}".format}
    bul = "{0.xref} - Husband Name: {0.husband.name}, Wife Name: {0.wife.name}, Marriage Date: {0.marriage_date}".format

    for key, items, count in matches(gedcom_file.families, lambda f: (f.marriage_date.val, f.husband.name.val.replace("/", ""), f.wife.name.val.replace("/", ""))):
        status = "passed" if count == 1 else "failed"
        r[status].append({"message": msg[status](count, key[1], key[2], key[0]), "bullets": map(bul, items)})

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
    gedcom_file = gedcom.File()
    fname = "Test_Files/My-Family-20-May-2016-697-Simplified-WithErrors-Sprint04.ged"
    try:
        gedcom_file.read_file(fname)
    except IOError as e:
        sys.exit("Error Opening File - {0}: '{1}'".format(e.strerror, e.filename))

    # Log only passed and failed cases to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    # Sprint 0 - Summaries
    individual_summary(gedcom_file)
    family_summary(gedcom_file)

    # Sprint 1 - Stories
    dates_before_current_date(gedcom_file)
    birth_before_marriage(gedcom_file)
    birth_before_death(gedcom_file)
    marriage_before_divorce(gedcom_file)
    marriage_before_death(gedcom_file)
    divorce_before_death(gedcom_file)

    # Sprint 2 - Stories
    less_then_150_years_old(gedcom_file)
    birth_before_marriage_of_parents(gedcom_file)
    birth_before_death_of_parents(gedcom_file)
    marriage_after_14(gedcom_file)
    no_bigamy(gedcom_file)
    parents_not_too_old(gedcom_file)

    # Sprint 3 - Stories
    siblings_spacing(gedcom_file)
    less_than_5_multiple_births(gedcom_file)
    fewer_than_15_siblings(gedcom_file)
    male_last_names(gedcom_file)
    no_marriages_to_descendants(gedcom_file)
    siblings_should_not_marry(gedcom_file)

    # Sprint 4 - Stories
    first_cousins_should_not_marry(gedcom_file)
    aunts_and_uncles(gedcom_file)
    correct_gender_for_role(gedcom_file)
    unique_ids(gedcom_file)
    unique_name_and_birth_date(gedcom_file)
    unique_families_by_spouses(gedcom_file)
