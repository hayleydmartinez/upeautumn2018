#!/usr/bin/env python
import requests
import json

# global variables
actions = [ 'RIGHT', 'UP', 'LEFT', 'DOWN']
opp     = { 'RIGHT':'LEFT', 'UP':'DOWN', 'LEFT':'RIGHT', 'DOWN':'UP' }
mx, my  = 0, 0

# checks if a coordinate is within our map
def valid(x, y):
    return x > -1 and x < mx and y > -1 and y < my

def escape(url, seen, stack):
    # refresh data
    r    = requests.get(url)
    data = json.loads(r.content)

    # location variables
    x = data['current_location'][0]
    y = data['current_location'][1]
    seen.add((str(x), str(y)))

    # movements
    moves = { 'UP':[x,y-1], 'DOWN':[x,y+1], 'RIGHT':[x+1,y], 'LEFT':[x-1,y] }

    for i in actions:
        
        coord = (str(moves[i][0]), str(moves[i][1]))
        
        # is this an unexplored spot in our map?
        if valid(moves[i][0], moves[i][1]) and coord not in seen:

            # step in direction
            direction = requests.post(url, data = { 'action': i })
            result = json.loads(direction.content)['result']

            # if we are at the end, we have escaped
            if result == 'END':
                return True

            # if we can't move there, we add to seen so we don't re-check it
            elif result == 'OUT_OF_BOUNDS' or result == 'WALL':
                seen.add(coord)
                continue

            # add our move to the stack
            stack.append(i)

            # if we have escaped, we're done!
            if escape(url, seen, stack):
                return True

    # if we can't move anywhere, we undo our last action
    requests.post(url, data = { 'action': opp[stack.pop()] })
    
    return False


# MAIN CODE PORTION
# post to server
r = requests.post('http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session', data = { 'uid': '104926567' })
token = json.loads(r.content)['token']
url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token=' + token

# get data from server
r = requests.get(url)
data = json.loads(r.content)

# complete all levels
while(data['levels_completed'] != data['total_levels']):
    print ("Begin maze")
    print (data['maze_size'])
    
    # collect our data and escape
    mx, my = data['maze_size'][0], data['maze_size'][1]
    seen = set()
    stack = []
    escape(url, seen, stack)

    # refresh data
    r = requests.get(url)
    data = json.loads(r.content)
    print("Escaped a maze!")

print("Finished all mazes!")
