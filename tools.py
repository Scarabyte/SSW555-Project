"""
Tools for gedcom project
"""
import re
from datetime import datetime
import sys
from itertools import ifilter
import gedcom

def human_sort(s, _re=re.compile('([0-9]+)')):
    """
    key for natural sorting
    example: alist.sort(key=human_sort)    #sorts the list in place (returns none)
    example: sorted(alist, key=human_sort) #returns a new list
    """
    try:
        return [int(x) if x.isdigit() else x.lower() for x in re.split(_re, s)]
    except:
        return s


def parse_date(s):
    """
    parse linedate string into datetime object
    """
    for fmt in ('%d %b %Y', '%b %Y', '%Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError("Unsupported Date Format")


def years_between(a, b):
    """ Calculate the years between two dates

    :param a: datetime 1
    :param b: datetime 2

    :return: years between two dates
    :rtype: float

    """
    return abs(round(float((a - b).days) / 365, 2))


def get_name(individual):
    if type(individual) is gedcom.Line:
        myname = individual.children.find_one("tag", "NAME").get('line_value')
        return myname.replace("/", "") if myname else None
    else:
        raise TypeError("individual should be a gedcom.Line instance")


def get_sex(individual):
    if type(individual) is gedcom.Line:
        mysex = individual.children.find_one("tag", "SEX").get('line_value')
        return mysex if mysex else None
    else:
        raise TypeError("individual should be a gedcom.Line instance")


def get_birth_date(individual):
    """ Return the birth date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The birth date line
    :rtype: Line

    author: Constantine Davantzis
    """
    if type(individual) is gedcom.Line:
        birth = individual.children.find_one("tag", "BIRT")
        return birth.children.find_one('tag', 'DATE') if birth else None
    else:
        raise TypeError("individual should be a gedcom.Line instance")


def get_death_date(individual):
    """ Return the death date (if any) of an individual

    :param individual: The individual line
    :type individual: Line

    :return: The death date line
    :rtype: Line

    author: Adam Burbidge
    """
    death = individual.children.find_one("tag", "DEAT")
    if death:
        return death.children.find_one("tag", "DATE")


def iter_families_spouse_of(individual):
    """ Returns iterator of families where this person is a spouse.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return iter(FAMS.follow_xref() for FAMS in individual.children.find("tag", "FAMS"))


def iter_families_child_of(individual):
    """ Returns iterator of families where this person is a child.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return iter(FAMC.follow_xref() for FAMC in individual.children.find("tag", "FAMC"))


def iter_marriages(individual):
    """ Returns iterator this persons marriages.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return iter(marr for fam in iter_families_spouse_of(individual) for marr in fam.children.find('tag', 'MARR'))


def get_marriage_dates(individual):
    """ Returns marriage_dates of individual

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return [marr.children.find_one('tag', 'DATE') for marr in iter_marriages(individual)]


def iter_divorces(individual):
    """ Returns iterator this persons divorces.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return iter(div for fam in iter_families_spouse_of(individual) for div in fam.children.find('tag', 'DIV'))


def get_divorce_dates(individual):
    """ Returns the divorce dates of an individual

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return [div.children.find_one('tag', 'DATE') for div in iter_divorces(individual)]


def family_dict(family):
    """ Create dictionary of family info for a family line

    :param family: The family line
    :type family: Line

    author: Constantine Davantzis

    """
    d = {}

    d["xref"] = family.get('xref_ID')

    husb = family.children.find_one('tag', 'HUSB')
    d["husb"] = husb.follow_xref() if husb else None

    wife = family.children.find_one('tag', 'WIFE')
    d["wife"] = wife.follow_xref() if husb else None

    marr = family.children.find_one('tag', 'MARR')
    if marr:
        d["marr"] = family.children.find_one('tag', 'MARR')
        d["marr_date"] = marr.children.find_one('tag', 'DATE') if marr else None
    else:
        d["marr"] = None
        d["marr_date"] = None

    div = family.children.find_one('tag', 'DIV')
    if div:
        d["div"] = family.children.find_one('tag', 'DIV')
        d["div_date"] = div.children.find_one('tag', 'DATE') if div else None
    else:
        d["div"] = None
        d["div_date"] = None

    d["children"] = [child.follow_xref() for child in family.children.find('tag', 'CHIL')]
    return d


def iter_family_dict(individual):
    """ iterate through a list of dictionaries with family information for each family individual is a spouse of

    :param individual: The individual line
    :type individual: Line

    :rtype: dict

    author: Constantine Davantzis
    """
    xref_id = individual.get('xref_ID')
    for fam in iter_families_spouse_of(individual):
        d = family_dict(fam)
        if d["husb"] and d["husb"].val != xref_id:
            d["spouse_is"] = "husb"
        elif d["wife"] and d["wife"].val != xref_id:
            d["spouse_is"] = "wife"
        else:
            d["spouse_is"] = None
        yield d


def iter_marriage_timeframe_dict(individual):
    """ Returns dictionary with information about the start and the end of a marriage.

    Logic:
        * check if datetime of these marriages overlap
        * marriages start with marr_date
        * marriages end with div_date, or the first deat_date of either spouse
        * if the marriage hasen't ended datetime.max is used as the datetime

    author: Constantine Davantzis

    :param individual:
    :type individual: Line

    :rtype: dict

    """
    for family in iter_family_dict(individual):
        marr_date = family["marr_date"]
        div_date = family["div_date"]
        wife_deat_date = get_death_date(family["wife"])
        husb_deat_date = get_death_date(family["husb"])
        if marr_date:
            start_ln, start_val, start_dt = marr_date.ln, marr_date.val, marr_date.datetime
            if div_date:
                end_reason = "div"
                end_ln, end_val, end_dt = div_date.ln, div_date.val, div_date.datetime
            elif wife_deat_date and not husb_deat_date:
                end_reason = "wife_deat"
                end_ln, end_val, end_dt = wife_deat_date.ln, wife_deat_date.val,  wife_deat_date.datetime
            elif husb_deat_date and not wife_deat_date:
                end_reason = "husb_deat"
                end_ln, end_val, end_dt = husb_deat_date.ln, husb_deat_date.val,  husb_deat_date.datetime
            elif husb_deat_date and wife_deat_date:
                if husb_deat_date.datetime < wife_deat_date.datetime:
                    end_reason = "husb_deat"
                    end_ln, end_val, end_dt = husb_deat_date.ln, husb_deat_date.val,  husb_deat_date.datetime
                else:
                    end_reason = "wife_deat"
                    end_ln, end_val, end_dt = wife_deat_date.ln, wife_deat_date.val,  wife_deat_date.datetime
            else:
                end_reason = "Not Ended"
                end_ln, end_val, end_dt = None, None, datetime.max

            yield {"family_id": family["xref"],
                   "husband_id": family["husb"].get("xref_ID"),
                   "wife_id": family["wife"].get("xref_ID"),
                   "start": {"line_number": start_ln, "line_value": start_val, "dt": start_dt, "reason": "marr_date"},
                   "end": {"line_number": end_ln, "line_value": end_val, "dt": end_dt, "reason": end_reason}}


def iter_parent_family_dict(individual):
    """ iterate through a list of dictionaries with family information for each family individual is a child of

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        yield family_dict(fam)


def iter_spouses(individual):
    """ Returns iterator this persons spouses.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis

    """
    v = individual.get('xref_ID')
    for f in iter_families_spouse_of(individual):
        yield next(ifilter(lambda x: x.val != v, (f.children.find_one('tag', 'HUSB'), f.children.find_one('tag', 'WIFE'))))


def get_spouses(individual):
    """ Returns list of this persons spouses.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis

    """
    return list(iter_spouses(individual))


def iter_children(individual):
    """ Return iterator of this persons children

    :param individual: The individual line
    :type individual: Line

    :return: List of Children Lines
    :rtype: List of Children Lines

    author: Constantine Davantzis
    """
    return iter(c.follow_xref() for f in iter_families_spouse_of(individual) for c in f.children.find('tag', 'CHIL'))


def get_father(individual):
    """ Get father of an individual

    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        husband = fam.children.find_one("tag", "HUSB")
        return husband.follow_xref() if husband else None


def get_mother(individual):
    """ Get mother of an individual

    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        wife = fam.children.find_one("tag", "WIFE")
        return wife.follow_xref() if wife else None


def get_marriage_date(individual):
    """ Return the marriage date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The marriage date line
    :rtype: Line

    author: Constantine Davantzis

    NOTE: this function only finds the first FAMS tag, will not work properly with multiple FAMS tags

    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            marriage = family.children.find_one('tag', 'MARR')
            if marriage:
                return marriage.children.find_one('tag', 'DATE')


def get_divorce_date(individual):
    """ Return the divorce date (if any) of an individual

    :param individual: The individual line
    :type individual: Line

    :return: The divorce date line
    :rtype: Line

    author: Constantine Davantzis

    NOTE: this function only finds the first FAMS tag, will not work properly with multiple FAMS tags

    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            divorce = family.children.find_one('tag', 'DIV')
            if divorce:
                return divorce.children.find_one('tag', 'DATE')


def indi_summary(line):
    """ Returns the summary for individual

    :param line: The individual or family line
    :type line: Line

    author: Constantine Davantzis

    """
    xref = line.get("xref_ID")
    info = {"name": line.children.find_one("tag", "NAME").get('line_value', "").replace("/", ""),
            "sex": line.children.find_one("tag", "SEX").get('line_value'),
            "birth_date": get_birth_date(line).get('line_value')}
    return xref, info


def family_summary(family):
    """ Returns the summary for family

    author: Constantine Davantzis
    """
    xref = family["xref"]
    info = {"husband": indi_summary(family["husb"]) if family["husb"] else None,
            "wife": indi_summary(family["wife"]) if family["wife"] else None,
            "children": [indi_summary(child) for child in family["children"]]}
    return xref, info


if __name__ == "__main__":
    pass
