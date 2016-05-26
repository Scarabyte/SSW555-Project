# Adam Burbidge
# SSW 555 Project 2

fname = raw_input('Enter the file name to open: ')
try:
    filehandle = open(fname)
except:
    print 'Invalid file name: ', fname
    exit()

# Define the valid GEDCOM flags for this project
valid_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM",
              "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

for line in filehandle:
    print line, # The line itself

    # Assumptions (stated in Project Overview):
    # -GEDCOM files are syntactically correct
    #  -Files start with a level number as the first character
    #  -Files have a legal tag
    #  -All arguments are in the proper format
    #  -One blank space separates the fields (level, tag, arguments)

    print line[0] # The level number, which we assumed to be the first character
    # (Note that we could also do this after we separate the line below.)

    # Separate the line into three parts: Level, Tag, Arguments
    # Each field is separated by a single space.
    # Use -1 as the index to remove the newline character.
    # Also note that not all tags have an argument. But for this assignment,
    # we're not required to do anything with the argument, just print the tag.

    separated_line = line[:-1].split(' ', 2)
    level = separated_line[0]
    tag = separated_line[1]

    # If the line's Tag is one of the valid tags we identified for this project, print it.
    # If not, print "Invalid tag"

    if tag in valid_tags:
        print tag
    else:
        print "Invalid tag"

    # Just as a separator to make the output easier to read, let's add a newline.
    print
