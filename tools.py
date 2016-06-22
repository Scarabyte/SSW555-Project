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
    raise ValueError


def get_birth_date(individual):
    """ Return the birth date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The birth date line
    :rtype: Line

    auther: Constantine Davantzis
    """
    birth = individual.children.find_one("tag", "BIRT")
    if birth:
        return birth.children.find_one('tag', 'DATE')


def get_marriage_date(individual):
    """ Return the marriage date line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The marriage date line
    :rtype: Line

    auther: Constantine Davantzis
    """
    family_spouse = individual.children.find_one("tag", "FAMS")
    if family_spouse:
        family = family_spouse.follow_xref()
        if family:
            marriage = family.children.find_one('tag', 'MARR')
            if marriage:
                return marriage.children.find_one('tag', 'DATE')


def get_death_date(individual):
    """ Return the death date (if any) of an individual

    :param individual: The individual line
    :type individual: Line

    :return: The death date line
    :rtype: Line

    auther: Adam Burbidge
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

    auther: Constantine Davantzis
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