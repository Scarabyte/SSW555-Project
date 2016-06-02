"""
 SSW555 GEDCOM Parsing Project
 Team 02 - Adam Burbidge; Constantine Davantzis; Vibha Ravi
"""

import gedcom
import stories


def project_03(g):
    print " - Individuals - "
    for individual in g.individuals.iteritems():
        print individual
    print
    print " - Families - "
    for family in g.families.iteritems():
        print family

if __name__ == "__main__":
    g = gedcom.File("Test_Files/GEDCOM.ged")
    project_03(g)
    