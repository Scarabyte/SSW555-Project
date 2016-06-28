"""
Tools for gedcom project
"""
import re
from datetime import datetime
import sys

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


def get_birth_date(individual):
    """ Return the birth date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The birth date line
    :rtype: Line

    author: Constantine Davantzis
    """
    birth = individual.children.find_one("tag", "BIRT")
    if birth:
        return birth.children.find_one('tag', 'DATE')


def get_children(individual):
    """ Return the children of an individual

    :param individual: The individual line
    :type individual: Line

    :return: List of Children Lines
    :rtype: List of Children Lines

    author: Constantine Davantzis
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            return [child.follow_xref() for child in family.children.find('tag', 'CHIL')]
    return []


def get_marriage_date(individual):
    """ Return the marriage date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The marriage date line
    :rtype: Line

    author: Constantine Davantzis
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            marriage = family.children.find_one('tag', 'MARR')
            if marriage:
                return marriage.children.find_one('tag', 'DATE')


def yield_marriage_dates(individual):
    """

    author: Constantine Davantzis
    """
    for family in yield_families(individual):
        marriage = family.children.find_one('tag', 'MARR')
        if marriage:
            marriage_date = marriage.children.find_one('tag', 'DATE')
            if marriage_date:
                yield marriage_date


def get_marriage_dates(individual):
    """

    author: Constantine Davantzis
    """
    return list(yield_marriage_dates(individual))


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


def get_divorce_date(individual):
    """ Return the divorce date (if any) of an individual

    :param individual: The individual line
    :type individual: Line

    :return: The divorce date line
    :rtype: Line

    author: Constantine Davantzis
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            divorce = family.children.find_one('tag', 'DIV')
            if divorce:
                return divorce.children.find_one('tag', 'DATE')


def yield_divorce_dates(individual):
    """

    author: Constantine Davantzis
    """
    for family in yield_families(individual):
        divorce = family.children.find_one('tag', 'DIV')
        if divorce:
            divorce_date = divorce.children.find_one('tag', 'DATE')
            if divorce_date:
                yield divorce_date


def get_divorce_dates(individual):
    """

    author: Constantine Davantzis
    """
    return list(yield_divorce_dates(individual))


def yield_families(individual):
    """
    author: Constantine Davantzis
    """
    family_spouses = individual.children.find("tag", "FAMS")
    for family_spouse in family_spouses:
        family = family_spouse.follow_xref()
        if family:
            yield family


def yield_spouses(individual):
    """
    author: Constantine Davantzis
    """
    for family in yield_families(individual):
        husband = family.children.find_one("tag", "HUSB")
        if husband.get("line_value") != individual.get("xref_ID"):
            yield husband.follow_xref()
        wife = family.children.find_one("tag", "WIFE")
        if wife.get("line_value") != individual.get("xref_ID"):
            yield wife.follow_xref()


def get_spouses(individual):
    """
    author: Constantine Davantzis
    """
    return list(yield_spouses(individual))


def get_families(individual):
    """
    author: Constantine Davantzis
    """
    return list(yield_families(individual))


def get_parent_birth_date(family):
    """ Return the birth dates of an family's father and mother
    :param family
    :type 

    :return: 
    :rtype: Line

    author: Adam Burbidge
    """
    family_child = individual.children.find_one("tag", "FAMC")
    if family_child:
        family = family_child.follow_xref()
        if family:
            pass
    pass


def get_parent_deat_date(family):
    """ Return the death dates of an family's father and mother
    :param family
    :type 

    :return: 
    :rtype: Line

    author: vibha ravi
    """
    family_child = individual.children.find_one("tag", "FAMC")
  
    pass



def get_spouse_divorce_date(individual):
    """ Return the divorce date of an individual's spouse
    :param individual
    :type 

    :return: 
    :rtype: Line

    author: Adam Burbidge
    """
    pass


def get_spouse_death_date(individual):
    """ Return the death date of an individual's spouse
    :param individual
    :type 

    :return: 
    :rtype: Line

    author: Adam Burbidge
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            spouse = family.children.find_one("tag", "HUSB")

    pass


def get_spouse(individual):
    """ Return an individual's spouse
    :param individual
    :type 

    :return: 
    :rtype: Line

    author: Adam Burbidge
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
    pass



if __name__ == "__main__":
    pass
