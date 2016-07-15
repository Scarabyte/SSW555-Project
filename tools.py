"""
Tools for gedcom project
"""
import re
from datetime import datetime
import gedcom

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()

# TODO: Better Comments
# TODO: Move LineTools to gedcom.py?


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
        options = {"HEAD": "header", "MARR": "marriage", "DIV": "divorce", "BIRT": "birth", "DEAT": "death"}
        p = self.line.parent
        return options.get(p.tag, p.tag) if p is not None else None

    @property
    @cachemethod
    def belongs_to(self):
        p = self.line.parent
        if p:
            pp = p.parent
            if pp:
                if pp.tag == "INDI":
                    return Individual(pp)
                if pp.tag == "FAM":
                    return Family(pp)


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

    @property
    @cachemethod
    def summary(self):
        """ Returns the summary for individual
        """
        return self.xref, {"line_number": self.ln,
                           "name": self.name.story_dict,
                           "sex": self.sex.story_dict,
                           "birth_date": self.birth_date.story_dict}


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

    @property
    @cachemethod
    def summary(self):
        """ Returns the summary for family

        """
        return self.xref, {"husband": self.husband.summary if self.has("husband") else None,
                           "wife": self.wife.summary if self.has("wife") else None,
                           "children": map(lambda c: c.summary, self.children)}

if __name__ == "__main__":
    pass
