"""
 SSW555 GEDCOM Parsing Project
 Team 02 - Adam Burbidge; Constantine Davantzis; Vibha Ravi
"""

import gedcom
import tools
import stories







if __name__ == "__main__":
    g = gedcom.File("Test_Files/GEDCOM.ged")

    print " - Individuals - "
    print g.individuals

    print " - Families - "
    print g.families
