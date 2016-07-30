import re
import tools
import parser
from datetime import datetime

NOW = datetime.now()
NOW_STRING = NOW.strftime("%d %b %Y").upper()


def cachemethod(func):
    def wrapper(self, *args):
        if func.__name__ in self.cache:
            return self.cache.get(func.__name__)
        val = func(self, *args)
        self.cache[func.__name__] = val
        return val
    return wrapper


class Base(object):
    def __init__(self, line):
        self.line = line
        self.cache = {}

    @property
    @cachemethod
    def ln(self):
        try:
            return self.line.ln
        except AttributeError:
            return None

    @property
    @cachemethod
    def val(self):
        try:
            return self.line.val
        except AttributeError:
            return None

    @property
    @cachemethod
    def story_dict(self):
        try:
            return self.line.story_dict
        except AttributeError:
            return None

    def has(self, p):
        return (getattr(self, p) is not None) and (getattr(self, p) is not {})


class Sex(Base):
    def __str__(self):
        return "{0} (line {1})".format("Male" if self.val == "M" else "Female", self.ln)

    def __repr__(self):
        return "{0} (line {1})".format("Male" if self.val == "M" else "Female", self.ln)


class Name(Base):
    def __str__(self):
        return self.val.replace("/", "")

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)


    @property
    @cachemethod
    def surname(self):
        m = re.match(r".*?/([^/]*)/", self.val)
        return m.group(1).strip() if m else None


class Date(Base):
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
        try:
            return self.line.datetime
        except AttributeError:
            return None

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


class Individual(Base):
    def __str__(self):
        name = self.name.val.replace("/", "") if self.has("name") else "N/A"
        return "{0} ({1} - line {2})".format(name, self.xref, self.ln)

    def __repr__(self):
        name = self.name.val.replace("/", "") if self.has("name") else "N/A"
        return "{0} ({1} - line {2})".format(name, self.xref, self.ln)

    def __eq__(self, other):
        return self.xref == other.xref

    def __ne__(self, other):
        return self.xref != other.xref

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
                return tools.years_between(self.birth_date.dt, self.death_date.dt)
            return tools.years_between(self.birth_date.dt, NOW)
        return None

    @property
    @cachemethod
    def pronoun(self):
        sex = self.sex.val if self.has("sex") else None
        if sex == "M":
            return "his"
        if sex == "F":
            return "her"
        return "their"

    @property
    @cachemethod
    def niece_or_nephew(self):
        sex = self.sex.val if self.has("sex") else None
        if sex == "M":
            return "nephew"
        if sex == "F":
            return "niece"
        return "niece/nephew"

    @property
    @cachemethod
    def aunt_or_uncle(self):
        sex = self.sex.val if self.has("sex") else None
        if sex == "M":
            return "uncle"
        if sex == "F":
            return "aunt"
        return "niece/nephew"

    @property
    @cachemethod
    def birth(self):
        return self.line.children.find_one("tag", "BIRT")

    @property
    @cachemethod
    def birth_date(self):
        if type(self.birth) is parser.Line:
            date = self.birth.children.find_one('tag', 'DATE')
            if type(date) is parser.Line:
                return Date(date)

    @property
    @cachemethod
    def death(self):
        l = self.line.children.find_one("tag", "DEAT")
        return l if type(l) is parser.Line else None

    @property
    @cachemethod
    def death_date(self):
        if type(self.death) is parser.Line:
            date = self.death.children.find_one('tag', 'DATE')
            if type(date) is parser.Line:
                return Date(date)

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
                fam.husband.spouse_family = fam
                yield fam.husband
            if fam.has("wife") and fam.wife.xref != self.xref:
                fam.wife.spouse_family = fam
                yield fam.wife

    @property
    def families_and_spouses(self):
        """
        """
        for fam in self.families("FAMS"):
            if fam.has("husband") and fam.husband.xref != self.xref:
                yield fam, fam.husband
            if fam.has("wife") and fam.wife.xref != self.xref:
                yield fam, fam.wife

    @property
    @cachemethod
    def summary(self):
        """ Returns the summary for individual
        """
        return self.xref, {"line_number": self.ln,
                           "name": self.name.story_dict if self.has("name") else None,
                           "sex": self.sex.story_dict if self.has("sex") else None,
                           "birth_date": self.birth_date.story_dict if self.has("birth_date") else None}

    @property
    @cachemethod
    def siblings(self):
        for fam in self.families("FAMC"):
            for child in fam.children:
                if self != child:
                    yield child

    @property
    @cachemethod
    def aunts_and_uncles(self):
        for fam in self.families("FAMC"):
            for sib in fam.husband.siblings:
                sib.rel_by = fam.husband
                sib.rel_by_type = "dad"
                yield sib
            for sib in fam.wife.siblings:
                sib.rel_by = fam.wife
                sib.rel_by_type = "mom"
                yield sib

    @property
    @cachemethod
    def cousins(self):
        for fam in self.families("FAMC"):
            for sib in fam.husband.siblings:
                for child in sib.children:
                    yield child
            for sib in fam.wife.siblings:
                for child in sib.children:
                    yield child

    @property
    @cachemethod
    def families_and_siblings(self):
        for fam in self.families("FAMC"):
            for child in fam.children:
                if self != child:
                    yield fam, child

    @property
    @cachemethod
    def families_and_children(self):
        for fam in self.families("FAMS"):
            for child in fam.children:
                yield fam, child


    @property
    @cachemethod
    def children(self):
        return [c for f in self.families("FAMS") for c in f.children]

    @property
    @cachemethod
    def descendants(self):

        title = lambda i: "child" if i == 1 else "grandchild" if i == 2 else (i-2)*"great-"+"grandchild"

        def get_d(individuals=[], checked=[], i=1):
            new = []
            for indi in individuals:
                for child in indi.children:
                    if child in checked:
                        pass
                    else:
                        child.descendant_title = title(i)
                        checked.append(child)
                        new.append(child)
            return new + get_d(new, checked, i+1) if len(new) > 0 else new


        return get_d([self])


class Family(Base):
    def __str__(self):
        return "Family ({0} - line {1})".format(self.xref, self.ln)

    def __eq__(self, other):
        return self.xref == other.xref

    @property
    @cachemethod
    def xref(self):
        return self.line.get('xref_ID')

    @property
    @cachemethod
    def story_dict(self):
        return {"xref": self.xref, "line_number": self.ln}

    @property
    @cachemethod
    def husband(self):
        husb = self.line.children.find_one('tag', 'HUSB')
        return Individual(husb.follow_xref()) if husb else None

    @property
    @cachemethod
    def husband_marriage_age(self):
        return tools.years_between(self.marriage_date.dt, self.husband.birth_date.dt)

    @property
    @cachemethod
    def wife(self):
        wife = self.line.children.find_one('tag', 'WIFE')
        return Individual(wife.follow_xref()) if wife else None

    @property
    @cachemethod
    def wife_marriage_age(self):
        return tools.years_between(self.marriage_date.dt, self.wife.birth_date.dt)

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

