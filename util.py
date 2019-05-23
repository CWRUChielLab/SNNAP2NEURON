


def formatedObjectVar(obj, var):
    """
    returns a left justified sting (obj.var) with a length of 20 characters
    Inputs:
    obj - object name
    var - variable name

    Returns:
    a left justified sting with a length of 20 characters
    """
    return (obj+"."+var).ljust(20)



def cleanupFileText(text):
    """
    returns an arry for after striping whitespaces and comments of SNNAP files

    Inputs:
    text - content of a SNNAP file in one single string

    Returns:
    lineArr - an array of lines without comments and empty lines
    
    """
    fileLines = text.split('\n')
    lineArr = []

    for i in range(len(fileLines)):
        l = fileLines[i].strip()
        if len(l) == 0 or l[0] == '>':
            continue
        else:
            lineArr.append([elem.strip() for elem in l.split('>')])
    return lineArr
