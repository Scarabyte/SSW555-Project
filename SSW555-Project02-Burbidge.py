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


    # Separate the line into three parts: Level, Tag, Arguments
    # Each field is separated by a single space.
    # Use line.strip() to remove leading and trailing whitespace.
    # Also note that not all tags have an argument. But for this assignment,
    # we're not required to do anything with the argument, just print the tag.
    separated_line = (line.strip()).split(' ', 2)

    # Check if the first element in separated_line has a length greater than 0
    # If not, assume it's a blank spacer line in the GEDCOM file and continue.
    if len(separated_line[0]) > 0:
        level = separated_line[0]
    else:
        continue

    print level

    if int(level) > 0:
        tag = separated_line[1]
    elif (len(separated_line) == 3 and
          (separated_line[2] == 'FAM' or
           separated_line[2] == 'INDI')):
        tag = separated_line[2]
    else:
        tag = separated_line[1]

    # If the line's Tag is one of the valid tags we identified for this project, print it.
    # If not, print "Invalid tag"

    if tag in valid_tags:
        print tag
    else:
        print "Invalid tag"

    # Just as a separator to make the output easier to read, let's add a newline.
    print


# Close the file when done
filehandle.close()
