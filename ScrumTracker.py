###############################################################################
# NAME:             ScrumTracker.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Scrum Tracker
#
# CREATED:          04/10/2020
#
# LAST EDITED:      04/11/2020
###

from argparse import ArgumentParser
import csv

###############################################################################
# TimeCampParser
###

def getHeight(node, distance):
    if 'nodes' in node and node['nodes']:
        return getHeight(node['nodes'][0], distance + 1)
    return distance

def specialAttach(tree1, tree2, level):
    """Holy mackerel."""
    if level == 0:
        tree2['nodes'].append(tree1)
    else:
        specialAttach(tree1, tree2['nodes'][-1], level - 1)

def getMinutes(timeSpec):
    if ' ' in timeSpec:
        hours, minutes = timeSpec.split(' ')
        return (int(hours[:-1]) * 60) + int(minutes[:-1])
    return int(timeSpec[:-1])

def doTimeCampParsing(parent, root, inputFile):
    try:
        line = inputFile.__next__()
        if line[2] == '': # If (!isLeaf(node))
            node = {'name': line[0], 'nodes': []}
            if parent['nodes'] and 'time' in parent['nodes'][0]:
                doTimeCampParsing(node, root, inputFile)
                specialAttach(node, root, getHeight(root, 0)
                              - getHeight(node, 0))
            else:
                parent['nodes'].append(node)
                doTimeCampParsing(node, root, inputFile)
        else:
            node = {'name': line[0], 'time': getMinutes(line[1])}
            if line[0] is 'Total':
                return # Ignore the 'Total' line.
            parent['nodes'].append(node)
            doTimeCampParsing(parent, root, inputFile)
    except StopIteration:
        return

def timecampParser(inputFile):
    """Parses CSV files output from TimeCamp"""
    with open(inputFile, 'r') as inputStream:
        reader = csv.reader(inputStream, delimiter=',', quotechar='"')
        index = {'name': 'TimeCamp', 'nodes': []}
        reader.__next__() # Eat the header
        doTimeCampParsing(index, index, reader)
        return index

###############################################################################
# Main
###

def parseArguments():
    """Parse the arguments."""
    parser = ArgumentParser()
    parser.add_argument('parser', choices=['timecamp'],
                        help='Parser for the input spreadsheet.')
    parser.add_argument('inputFile', help='The data file')
    return vars(parser.parse_args())

def main():
    arguments = parseArguments()
    handlers = {'timecamp': timecampParser}
    print(handlers[arguments['parser']](arguments['inputFile']))

if __name__ == '__main__':
    main()

###############################################################################
