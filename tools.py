"""
Tools for gedcom project
"""
import re
from datetime import datetime
import sys
from itertools import ifilter

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
    return birth.children.find_one('tag', 'DATE') if birth else None


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
    """

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
    """

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    return [div.children.find_one('tag', 'DATE') for div in iter_divorces(individual)]


def iter_marr_and_div_date_pairs(individual):
    """

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis
    """
    for fam in iter_families_spouse_of(individual):
        marr = fam.children.find_one('tag', 'MARR')
        div = fam.children.find_one('tag', 'DIV')
        if marr or div:
            marr_date = marr.children.find_one('tag', 'DATE') if marr else None
            div_date = div.children.find_one('tag', 'DATE') if div else None
            yield {"marr_date":  marr_date, "div_date": div_date}


def iter_spouses(individual):
    """ Returns iterator this persons spouses.

    :param individual: The individual line
    :type individual: Line

    author: Constantine Davantzis

    """
    v = individual.get('xref_ID')
    for f in iter_families_spouse_of(individual):
        yield next(ifilter(lambda x: x.val != v, (f.children.find_one('tag', 'HUSB'), f.children.find_one('tag', 'WIFE'))))


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
    """
    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        husband = fam.children.find_one("tag", "HUSB")
        return husband.follow_xref() if husband else None


def get_mother(individual):
    """
    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        wife = fam.children.find_one("tag", "WIFE")
        return wife.follow_xref() if wife else None


def get_parents_marriage_date(individual):
    """
    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        marr = fam.children.find_one('tag', 'MARR')
        return marr.children.find_one('tag', 'DATE') if marr else None


def get_parents_divorce_date(individual):
    """
    author: Constantine Davantzis
    """
    for fam in iter_families_child_of(individual):
        div = fam.children.find_one('tag', 'DIV')
        return div.children.find_one('tag', 'DATE') if div else None


# DEPRECATED Functions to be removed


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


if __name__ == "__main__":
    pass
