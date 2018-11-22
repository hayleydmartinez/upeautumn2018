#!/usr/bin/env python
import requests
import json

def escape(url, seen):
    # REFRESH DATA
    r    = requests.get(url)
    data = json.loads(r.content)

    # LOCATION VARIABLES
    x = data['current_location'][0]
    y = data['current_location'][1]
    seen[y][x] = '+'

    # MOVEMENT VARIABLES
    actions = [ 'UP', 'DOWN', 'RIGHT', 'LEFT']
    opp     = { 'UP':'DOWN', 'DOWN':'UP', 'RIGHT':'LEFT', 'LEFT':'RIGHT'}
    moves   = { 'UP':[x,y-1], 'DOWN':[x,y+1], 'RIGHT':[x+1,y], 'LEFT':[x-1,y] }

    for i in actions:
        print("We are at: [" + str(x) + ',' + str(y) + ']')
        print('Try to move ' + i)
        for j in seen:
            print(j)

        # STEP IN DIRECTION
        direction = requests.post(url, data = { 'action': i })
        result = json.loads(direction.content)['result']

        print(result)

        if result == 'END':
            return True

        if result == 'OUT_OF_BOUNDS':
            continue

        # REFRESH DATA
        r    = requests.get(url)
        data = json.loads(r.content)

        # LOCATION VARIABLES
        x = data['current_location'][0]
        y = data['current_location'][1]

        if result == 'WALL':
            seen[moves[i][1]][moves[i][0]] = 'X'
            continue

        # IF YOU HAVEN'T BEEN TO THIS SPOT
        if seen[y][x] == ' ':
            print('Move ' + i)
            if escape(url, seen):
                return True

        # IF YOU'VE ALREADY BEEN, STEP BACK
        elif seen[y][x] != 'X':
            requests.post(url, data = { 'action': opp[i] })
            r = requests.get(url)
            data = json.loads(r.content)

    return False


# POST TO SERVER
r = requests.post('http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session', data = { 'uid': '104926567' })
token = json.loads(r.content)['token']
url = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token=' + token

# GET DATA FROM SERVER
r = requests.get(url)
data = json.loads(r.content)

while(data['levels_completed'] != data['total_levels']):
    # ESCAPE FROM MAZE
    print ("Begin maze")
    print (data['maze_size'])

    seen = []
    for i in range(data['maze_size'][1]):
        item = []
        for j in range(data['maze_size'][0]):
            item.append(' ')
        seen.append(item)

    escape(url, seen)

    # REFRESH DATA EVERY LEVEL
    r = requests.get(url)
    data = json.loads(r.content)
    print("Escaped " + str(data['levels_completed']) + " mazes!")

print("Finished all mazes!")
