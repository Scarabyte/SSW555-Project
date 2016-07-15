"""
Tools for gedcom project
"""
import re
from datetime import datetime
from itertools import ifilter
import gedcom

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()


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


def days_between(a, b):
    """ Calculate the days between two dates

    :param a: datetime 1
    :param b: datetime 2

    :return: days between two dates
    :rtype: float

    """
    return abs((a - b).days)


def years_between(a, b):
    """ Calculate the years between two dates

    :param a: datetime 1
    :param b: datetime 2

    :return: years between two dates
    :rtype: float

    """
    return abs(round(float((a - b).days) / 365, 2))


def get_name(individual):
    """ Return the name line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The name line
    :rtype: Line

    author: Adam Burbidge
    """
    if type(individual) is gedcom.Line:
        myname = individual.children.find_one("tag", "NAME").get('line_value')
        return myname.replace("/", "") if myname else None
    else:
        raise TypeError("individual should be a gedcom.Line instance")


def get_sex(individual):
    """ Return the sex line of an individual line

    :param individual: The individual line
    :type individual: Line

    :return: The sex line
    :rtype: Line

    author: Adam Burbidge
    """
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


def cachemethod(func):
    def wrapper(self, *args):
        if func.__name__ in self.cache:
            return self.cache.get(func.__name__)
        val = func(self, *args)
        self.cache[func.__name__] = val
        return val
    return wrapper


class LineTool(object):
    def __init__(self, line):
        self.line = line
        self.cache = {}

    @property
    @cachemethod
    def ln(self):
        return self.line.ln

    @property
    @cachemethod
    def val(self):
        return self.line.val

    @property
    @cachemethod
    def story_dict(self):
        return self.line.story_dict

    def has(self, p):
        return getattr(self, p) is not None


class Sex(LineTool):
    def __str__(self):
        return "{0} (line {1})".format("Male" if self.val == "M" else "Female", self.ln)

    def __repr__(self):
        return "{0} (line {1})".format("Male" if self.val == "M" else "Female", self.ln)


class Name(LineTool):

    @property
    @cachemethod
    def surname(self):
        m = re.match(r".*?/([^/]*)/", self.val)
        return m.group(1).strip() if m else None


class Date(LineTool):
    def __str__(self):
        return "{0} (line {1})".format(self.val, self.ln)

    def __eq__(self, other):
        return self.dt == other.dt

    def __ne__(self, other):
        return self.dt != other.dt

    def __lt__(self, other):
        return self.dt < other.dt

    def __gt__(self, other):
        return self.dt > other.dt

    def __le__(self, other):
        return self.dt <= other.dt

    def __ge__(self, other):
        return self.dt >= other.dt

    @property
    @cachemethod
    def dt(self):
        return self.line.datetime

    @property
    @cachemethod
    def type(self):
        tag = self.line.parent.tag
        if tag == "MARR":
            return "marriage date"
        if tag == "HEAD":
            return "header date"
        if tag == "DIV":
            return "divorce date"
        if tag == "BIRT":
            return "birth date"
        if tag == "DEAT":
            return "death date"


class Individual(LineTool):
    def __str__(self):
        name = self.name.val.replace("/", "") if self.has("name") else "N/A"
        return "{0} ({1} - line {2})".format(name, self.xref, self.ln)

    def __repr__(self):
        name = self.name.val.replace("/", "") if self.has("name") else "N/A"
        return "{0} ({1} - line {2})".format(name, self.xref, self.ln)

    @property
    @cachemethod
    def story_dict(self):
        return {"xref": self.xref, "line_number": self.ln}

    @property
    @cachemethod
    def xref(self):
        return self.line.get('xref_ID')

    @property
    @cachemethod
    def name(self):
        return Name(self.line.children.find_one("tag", "NAME"))

    @property
    @cachemethod
    def sex(self):
        return Sex(self.line.children.find_one("tag", "SEX"))

    @property
    @cachemethod
    def age(self):
        if self.birth_date:
            if self.death_date:
                return years_between(self.birth_date.dt, self.death_date.dt)
            return years_between(self.birth_date.dt, NOW)
        return None

    @property
    @cachemethod
    def pronoun(self):
        sex = self.sex.val if self.has("sex") else None
        if sex == "M":
            return "his"
        if sex == "F":
            return "her"
        return "there"

    @property
    @cachemethod
    def birth(self):
        return self.line.children.find_one("tag", "BIRT")

    @property
    @cachemethod
    def birth_date(self):
        l = self.birth
        return Date(l.children.find_one('tag', 'DATE')) if type(l) is gedcom.Line else None

    @property
    @cachemethod
    def death(self):
        return self.line.children.find_one("tag", "DEAT")

    @property
    @cachemethod
    def death_date(self):
        l = self.death
        return Date(l.children.find_one('tag', 'DATE')) if type(l) is gedcom.Line else None

    def families(self, tag):
        """ Returns iterator of families where this person is a spouse.

        Note: Tag should be FAMS or FAMC
        """
        if tag not in ["FAMS", "FAMC"]:
            raise ValueError("families tag must be 'FAMS' or 'FAMC'")
        return iter(Family(f.follow_xref()) for f in self.line.children.find("tag", tag))

    @property
    def spouses(self):
        """
        """
        for fam in self.families("FAMS"):
            if fam.has("husband") and fam.husband.xref != self.xref:
                yield fam.husband
            if fam.has("wife") and fam.wife.xref != self.xref:
                yield fam.wife


class Family(LineTool):
    def __str__(self):
        return "Family ({0} - line {1})".format(self.xref, self.ln)

    @property
    @cachemethod
    def xref(self):
        return self.line.get('xref_ID')

    @property
    @cachemethod
    def husband(self):
        husb = self.line.children.find_one('tag', 'HUSB')
        return Individual(husb.follow_xref()) if husb else None

    @property
    @cachemethod
    def husband_marriage_age(self):
        return years_between(self.marriage_date.dt, self.husband.birth_date.dt)

    @property
    @cachemethod
    def wife(self):
        wife = self.line.children.find_one('tag', 'WIFE')
        return Individual(wife.follow_xref()) if wife else None

    @property
    @cachemethod
    def wife_marriage_age(self):
        return years_between(self.marriage_date.dt, self.wife.birth_date.dt)

    @property
    @cachemethod
    def marriage(self):
        return self.line.children.find_one('tag', 'MARR')

    @property
    @cachemethod
    def marriage_date(self):
        marr = self.marriage
        return Date(marr.children.find_one('tag', 'DATE')) if marr else None

    @property
    @cachemethod
    def divorce(self):
        return self.line.children.find_one('tag', 'DIV')

    @property
    @cachemethod
    def divorce_date(self):
        div = self.divorce
        return Date(div.children.find_one('tag', 'DATE')) if div else None

    @property
    @cachemethod
    def marriage_end(self):
        """
            Logic:
            * marriages end with div_date, or the first deat_date of either spouse
            * if the marriage hasen't ended datetime.max is used as the datetime
        """
        if self.divorce_date:
            return {"reason": "divorce",
                    "dt": self.divorce_date.dt,
                    "story_dict": self.divorce_date.story_dict}
        if self.wife.has("death_date") and not self.husband.has("death_date"):
            return {"reason": "wife death",
                    "dt": self.wife.death_date.dt,
                    "story_dict": self.wife.death_date.story_dict}
        if self.husband.has("death_date") and not self.wife.has("death_date"):
            return {"reason": "husband death",
                    "dt": self.husband.death_date.dt,
                    "story_dict": self.husband.story_dict}
        if self.wife.has("death_date") and self.husband.has("death_date"):
            if self.husband.death_date < self.wife.death_date:
                return {"reason": "husband death",
                        "dt": self.husband.death_date.dt,
                        "story_dict": self.husband.death_date.story_dict}
            else:
                return {"reason": "wife death",
                        "dt": self.wife.death_date.dt,
                        "story_dict": self.wife.death_date.story_dict}
        return {"reason": "marriage has not ended",
                "dt": datetime.max,
                "story_dict": {"line_number": "N/A", "line_value": "never"}}

    @property
    @cachemethod
    def children(self):
        return [Individual(child.follow_xref()) for child in self.line.children.find('tag', 'CHIL')]

    @property
    @cachemethod
    def male_children(self):
        return filter(lambda c: c.sex.val == "M", self.children)

    @property
    @cachemethod
    def female_children(self):
        return filter(lambda c: c.sex.val == "F", self.children)


def family_dict(family):
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
        yield next(
            ifilter(lambda x: x.val != v, (f.children.find_one('tag', 'HUSB'), f.children.find_one('tag', 'WIFE'))))


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
