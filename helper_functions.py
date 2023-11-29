# helper functions for reading network data

# function to help convert server info that comes in strings
def tupleify_pos(str):
    # pass in two values like (1,2) - string - read_pos will return 2 variables 1 and 2 as ints.
    str = str.split(",")
    return int(str[0]), int(str[1])

# now the same func in reverse to take positions (touples) into strings to send to server.
def stringify_pos(tup):
    return str(tup[0]) + ", " + str(tup[1])
