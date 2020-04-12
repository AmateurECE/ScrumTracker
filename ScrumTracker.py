###############################################################################
# NAME:             ScrumTracker.py
#
# AUTHOR:           Ethan D. Twardy <edtwardy@mtu.edu>
#
# DESCRIPTION:      Scrum Tracker
#
# CREATED:          04/10/2020
#
# LAST EDITED:      04/12/2020
###

from argparse import ArgumentParser
import csv
import math

###############################################################################
# TimeCampParser
###

def normalize(theList, theTree):
    for project in theTree['nodes'][0]['nodes']:
        for sprint in project['nodes']:
            for story in sprint['nodes']:
                story['sprint'] = sprint['name']
                story['project'] = project['name']
                theList.append(story)

def getTotals(totals, theTree):
    if 'total' not in theTree:
        return
    totals[theTree['name']] = theTree['total']
    for node in theTree['nodes']:
        getTotals(totals, node)

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
            node = {'name': line[0], 'nodes': [], 'total': getMinutes(line[1])}
            if parent['nodes'] and 'time' in parent['nodes'][0]:
                doTimeCampParsing(node, root, inputFile)
                specialAttach(node, root, getHeight(root, 0)
                              - getHeight(node, 0))
            else:
                parent['nodes'].append(node)
                doTimeCampParsing(node, root, inputFile)
        else:
            if line[0] == 'Total':
                root['total'] = getMinutes(line[1])
                return
            node = {'name': line[0], 'time': getMinutes(line[1])}
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
        normalized = []
        normalize(normalized, index)
        totals = {}
        getTotals(totals, index)
        return normalized, totals

###############################################################################
# Metrics
###

def getTotalStoryPoints(stories, display=True):
    total = 0
    for story in stories:
        total += int(story['name'].split()[0][1:-1])
    if display:
        print('Total story points: {}'.format(total))
    return total

def getTotalTime(total, display=True):
    if display:
        printTime = '{}h {}m'.format(math.floor(total / 60), total % 60)
        print('Total time: {}'.format(printTime))
    return total

def getMinutesPerPoint(storyPoints, totalTime, display=True):
    velocity = totalTime / storyPoints
    if display:
        print('Velocity: {} mins/point'.format(velocity))
    return velocity

def getSprints(stories):
    sprints = {}
    for story in stories:
        if story['sprint'] not in sprints:
            sprints[story['sprint']] = []
        sprints[story['sprint']].append(story)
    return sprints

def getAverageStoryPointsPerSprint(totalStoryPointsBySprint, display=True):
    average = 0
    for sprint in totalStoryPointsBySprint:
        average += sprint
    average /= len(totalStoryPointsBySprint)
    if display:
        print('Average story points per sprint: {}'.format(average))

def getAverageTimePerSprint(totalTimeBySprint, display=True):
    average = 0
    for sprint in totalTimeBySprint:
        average += sprint
    average /= len(totalTimeBySprint)
    if display:
        printTime = '{}h {}m'.format(math.floor(average / 60), average % 60)
        print('Average time per sprint: {}'.format(printTime))

def getMetrics(stories, totals):
    storyPoints = getTotalStoryPoints(stories)
    totalTime = getTotalTime(totals['TimeCamp'])
    getMinutesPerPoint(storyPoints, totalTime)
    sprints = getSprints(stories)

    totalStoryPointsBySprint = []
    totalTimeBySprint = []
    for sprint in sprints:
        print('\n{}:'.format(sprints[sprint][0]['sprint']))
        totalStoryPointsBySprint.append(getTotalStoryPoints(sprints[sprint]))
        totalTimeBySprint.append(getTotalTime(totals[sprint]))

    print()
    getAverageStoryPointsPerSprint(totalStoryPointsBySprint)
    getAverageTimePerSprint(totalTimeBySprint)

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
    stories, totals = handlers[arguments['parser']](arguments['inputFile'])
    getMetrics(stories, totals)

if __name__ == '__main__':
    main()

###############################################################################
