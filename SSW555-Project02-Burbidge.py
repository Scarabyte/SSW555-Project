# Adam Burbidge
# SSW 555 Project 2

fname = raw_input('Enter the file name to open: ')
try:
    filehandle = open(fname)
except:
    print 'Invalid file name: ', fname
    exit()


for line in filehandle:
    print line,

    # Assumptions (stated in Project Overview):
    # -GEDCOM files are syntactically correct
    #  -Files start with a level number as the first character
    #  -Files have a legal tag
    #  -All arguments are in the proper format
    #  -One blank space separates the fields (level, tag, arguments)

    print line[0]
