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
    # For testing purposes only -
    # remove before submitting assignment
    print "TESTING FIRST FILE:"
    g1 = gedcom.File("Test_Files/GEDCOM.ged")
    project_03(g1)
    print

    print "TESTING SECOND FILE:"
    g2 = gedcom.File("Test_Files/My-Family-20-May-2016-697-Simplified.ged")
    project_03(g2)
    print

    # Don't hard code filenames;
    # project description says it has to be requested at the command line
    fname = raw_input('Enter the file name to open: ')
    try:
        g_file = gedcom.File(fname)
    except:
        print 'Invalid file name: ', fname
        exit()

    project_03(g_file)

