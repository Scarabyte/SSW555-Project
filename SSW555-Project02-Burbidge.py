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
