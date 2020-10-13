# ECE 4524 Problem Set 2
# File Name: wwsim.py
# Author: Greg Scott
#
# Includes classes for the simulation and the Tkinter display of the simulation.
# Also includes code to process the command-line input and run the program accordingly.


from wwagent import *
from wwRationalAgent import *
from wwTestDungeon import *
import sys
from tkinter import *
from random import randint
from matplotlib import pyplot as plt

import pandas as pd

# in your inner loop use it thus (just an example, I would probably use a named tuple)
#
# wwagent.update(percept) # update the agent with the current percept
# action = wwagent.action() # get the next action to take from the agent

# Global Constants
COLUMNS = 4
ROWS = 4
FONTTYPE = "Purisa"


# SET UP CLASS AND METHODS HERE
# Simulation class for running the underlying factors of the simulation
class PerformanceSimulation:

    def __init__(self, agent, rowSize, colSize, score):
        self.rowSize = rowSize
        self.colSize = colSize
        self.agent = agent
        self.score = score
        self.lastMove = 'None'
        self.lastPos = (3, 0)
        self.agentPos = (3, 0)
        self.agentFacing = 'right'
        self.arrow = 1
        self.wumpusAlive = True
        self.pits = {}
        self.percepts = {}
        for r in range(self.rowSize):
            for c in range(self.colSize):
                self.percepts['room' + str(r) + str(c)] = (None, None, None, None, None)
        self.wumpusLoc = (None, None)
        self.goldLocation = (None, None)
        self.hasGold = False

    def set_percepts(self, r, c, item):
        if item == 'gold':
            p = self.percepts['room' + str(r) + str(c)]
            self.percepts['room' + str(r) + str(c)] = (p[0], p[1], 'glitter', p[3], p[4])
        if item == 'wumpus':
            p = self.percepts['room' + str(r) + str(c)]
            # self.percepts['room'+str(r)+str(c)] = ('stench', p[1], p[2], p[3], p[4])
            if (r - 1) >= 0:
                p = self.percepts['room' + str(r - 1) + str(c)]
                self.percepts['room' + str(r - 1) + str(c)] = ('stench', p[1], p[2], p[3], p[4])
            if (r + 1) < 4:
                p = self.percepts['room' + str(r + 1) + str(c)]
                self.percepts['room' + str(r + 1) + str(c)] = ('stench', p[1], p[2], p[3], p[4])
            if (c - 1) >= 0:
                p = self.percepts['room' + str(r) + str(c - 1)]
                self.percepts['room' + str(r) + str(c - 1)] = ('stench', p[1], p[2], p[3], p[4])
            if (c + 1) < 4:
                p = self.percepts['room' + str(r) + str(c + 1)]
                self.percepts['room' + str(r) + str(c + 1)] = ('stench', p[1], p[2], p[3], p[4])
        if item == 'pit':
            if (r - 1) >= 0:
                p = self.percepts['room' + str(r - 1) + str(c)]
                self.percepts['room' + str(r - 1) + str(c)] = (p[0], 'breeze', p[2], p[3], p[4])
            if (r + 1) < 4:
                p = self.percepts['room' + str(r + 1) + str(c)]
                self.percepts['room' + str(r + 1) + str(c)] = (p[0], 'breeze', p[2], p[3], p[4])
            if (c - 1) >= 0:
                p = self.percepts['room' + str(r) + str(c - 1)]
                self.percepts['room' + str(r) + str(c - 1)] = (p[0], 'breeze', p[2], p[3], p[4])
            if (c + 1) < 4:
                p = self.percepts['room' + str(r) + str(c + 1)]
                self.percepts['room' + str(r) + str(c + 1)] = (p[0], 'breeze', p[2], p[3], p[4])

    def generate_simulation(self, test_dungeon: TestDungeon):
        # Set wumpus location
        self.wumpusLoc = test_dungeon.wumpus_loc
        # Set wumpus percepts
        self.set_percepts(self.wumpusLoc[0], self.wumpusLoc[1], 'wumpus')
        # Set gold location
        self.goldLocation = test_dungeon.gold_loc
        # Set gold percepts
        self.set_percepts(self.goldLocation[0], self.goldLocation[1], 'gold')
        # Generate pits
        for r in range(4):
            for c in range(4):
                if (r, c) in test_dungeon.pit_locs:
                    self.pits['room' + str(r) + str(c)] = True
                    # Set pit percepts
                    self.set_percepts(r, c, 'pit')
                else:
                    self.pits['room' + str(r) + str(c)] = False

    def reset_stats(self, agent, newScore):
        self.agent = None
        self.score = newScore
        self.lastMove = 'None'
        self.lastPos = (3, 0)
        self.agentPos = (3, 0)
        self.agentFacing = 'right'
        self.arrow = 1
        self.hasGold = False
        self.wumpusAlive = True
        self.percepts = {}
        self.agent = agent
        for r in range(self.rowSize):
            for c in range(self.colSize):
                self.percepts['room' + str(r) + str(c)] = (None, None, None, None, None)

    def agent_move(self, action):
        if action == 'shoot':
            self.score = self.score - 10
        else:
            self.score = self.score - 1
        r = self.agentPos[0]
        c = self.agentPos[1]
        if action == 'move':
            self.lastPos = self.agentPos
            bump = False
            if self.agentFacing == 'right':
                if (c + 1) < 4:
                    self.agentPos = (self.agentPos[0], self.agentPos[1] + 1)
                else:
                    bump = True
            elif self.agentFacing == 'up':
                if (r - 1) >= 0:
                    self.agentPos = (self.agentPos[0] - 1, self.agentPos[1])
                else:
                    bump = True
            elif self.agentFacing == 'left':
                if (c - 1) >= 0:
                    self.agentPos = (self.agentPos[0], self.agentPos[1] - 1)
                else:
                    bump = True
            else:
                if (r + 1) < 4:
                    self.agentPos = (self.agentPos[0] + 1, self.agentPos[1])
                else:
                    bump = True
            if bump:
                p = self.percepts['room' + str(r) + str(c)]
                self.percepts['room' + str(r) + str(c)] = (p[0], p[1], p[2], 'bump', p[4])
            p = self.percepts['room' + str(r) + str(c)]
            self.percepts['room' + str(r) + str(c)] = (p[0], p[1], p[2], p[3], None)
            self.lastMove = 'Move Forward'
        elif action == 'grab':
            if self.agentPos == self.goldLocation:
                self.hasGold = True
            self.lastMove = "Grab"
        elif action == 'climb':
            self.lastMove = 'Climb'
        elif action == 'shoot':
            if self.arrow != 0:
                if self.agentFacing == 'up':
                    if (c == self.wumpusLoc[1]) and (r > self.wumpusLoc[0]):
                        self.wumpusAlive = False
                elif self.agentFacing == 'right':
                    if (r == self.wumpusLoc[0]) and (c < self.wumpusLoc[1]):
                        self.wumpusAlive = False
                elif self.agentFacing == 'left':
                    if (r == self.wumpusLoc[0]) and (c > self.wumpusLoc[1]):
                        self.wumpusAlive = False
                else:
                    if (c == self.wumpusLoc[1]) and (r < self.wumpusLoc[0]):
                        self.wumpusAlive = False
                self.arrow = 0
            if not self.wumpusAlive:
                p = self.percepts['room' + str(r) + str(c)]
                self.percepts['room' + str(r) + str(c)] = (p[0], p[1], p[2], None, 'scream')
            self.lastMove = 'Shoot'
        else:
            if action == 'left':
                if self.agentFacing == 'right':
                    self.agentFacing = 'up'
                elif self.agentFacing == 'up':
                    self.agentFacing = 'left'
                elif self.agentFacing == 'left':
                    self.agentFacing = 'down'
                else:
                    self.agentFacing = 'right'
                self.lastMove = 'Rotate Left'
            else:
                if self.agentFacing == 'right':
                    self.agentFacing = 'down'
                elif self.agentFacing == 'down':
                    self.agentFacing = 'left'
                elif self.agentFacing == 'left':
                    self.agentFacing = 'up'
                else:
                    self.agentFacing = 'right'
                self.lastMove = 'Rotate Right'
            p = self.percepts['room' + str(r) + str(c)]
            self.percepts['room' + str(r) + str(c)] = (p[0], p[1], p[2], None, None)
        # print('S-position: ', self.agentPos

    def terminal_test(self):
        r = self.agentPos[0]
        c = self.agentPos[1]
        if (self.agentPos == self.wumpusLoc) and (self.wumpusAlive == True):
            return True
        elif self.pits['room' + str(r) + str(c)]:
            return True
        elif self.lastMove.lower() == 'climb' or self.lastMove.lower() == 'grab':
            return True
        else:
            return False

    def update_score(self):
        r = self.agentPos[0]
        c = self.agentPos[1]
        if (self.agentPos == self.wumpusLoc) and (self.wumpusAlive == True):
            self.score = self.score - 1000
        elif self.pits['room' + str(r) + str(c)]:
            self.score = self.score - 1000
        elif (self.agentPos == (3, 0)) and self.lastMove.lower() == 'climb':
            if self.hasGold:
                self.score = self.score + 1000

    def move(self):
        p = self.agentPos
        self.agent.update(self.percepts['room' + str(p[0]) + str(p[1])])
        action = self.agent.action()
        # print("Sim action: ", action
        self.agent_move(action)


def get_agent_type(agent):
    return str(agent) if str(agent) == "Rational Agent" else "Random Agent"


# Display class for running and modifying the GUI
class Display:
    score = None
    pastMove = None
    arrowStatus = None
    arrowStatusDis = None
    percepts = None
    agentDirection = None

    def set_room(self, r, c, sim):
        # Returns agent image
        if (sim.agentPos[0] == r) and (sim.agentPos[1] == c):
            if sim.agentFacing.lower() == 'right':
                return PhotoImage(file="Images/agent-right.gif")
            elif sim.agentFacing.lower() == 'up':
                return PhotoImage(file="Images/agent-up.gif")
            elif sim.agentFacing.lower() == 'left':
                return PhotoImage(file="Images/agent-left.gif")
            else:
                return PhotoImage(file="Images/agent-down.gif")
        # Returns start image
        elif (r == 3) and (c == 0):
            return PhotoImage(file="Images/start.gif")
        # Returns wumpus
        elif (r == sim.wumpusLoc[0]) and (c == sim.wumpusLoc[1]):
            if sim.pits['room' + str(r) + str(c)]:
                return PhotoImage(file="Images/pit-wumpus.gif")
            else:
                return PhotoImage(file="Images/live-wumpus.gif")
        # Returns gold and pit or gold
        elif (r == sim.goldLocation[0]) and (c == sim.goldLocation[1]):
            if sim.pits['room' + str(r) + str(c)]:
                return PhotoImage(file="Images/gold-pit.gif")
            else:
                return PhotoImage(file="Images/gold.gif")
        # Returns a pit
        elif sim.pits['room' + str(r) + str(c)]:
            return PhotoImage(file="Images/pit.gif")
        # Returns an empty room
        else:
            return PhotoImage(file="Images/emptyroom.gif")

    def __init__(self, master, simulation):
        frame = Frame(master, width=700, height=500)
        frame.pack()
        self.grid = {}
        self.score = StringVar()
        self.pastMove = StringVar()
        self.arrowStatus = StringVar()
        self.percepts = StringVar()
        self.agentDirection = StringVar()
        self.score.set(str(0))
        self.pastMove.set('None')
        self.arrowStatus.set('Available')
        self.agentDirection.set('Right')
        self.percepts.set(str(simulation.percepts['room30']))
        theScoreDis = Label(master, font=(FONTTYPE, 16), text="Performance:")
        lastMoveDis = Label(master, font=(FONTTYPE, 16), text="Last Move:")
        performanceDis = Label(master, font=(FONTTYPE, 14), textvariable=self.score)
        pastMoveDis = Label(master, font=(FONTTYPE, 14), textvariable=self.pastMove)
        arrowTitle = Label(master, font=(FONTTYPE, 16), text="Arrow Status:")
        self.arrowStatusDis = Label(master, font=(FONTTYPE, 14), fg='Green', textvariable=self.arrowStatus)
        perceptsTitle = Label(master, font=(FONTTYPE, 16), text="Current Percepts:")
        perceptsDis = Label(master, font=(FONTTYPE, 14), textvariable=self.percepts)
        agentDirectionTitle = Label(master, font=(FONTTYPE, 16), text="Agent Facing:")
        agentDirectionDis = Label(master, font=(FONTTYPE, 14), textvariable=self.agentDirection)
        self.goldStatus = Label(master, font=(FONTTYPE, 16), fg='Gold', text="Agent has gold!")
        performanceDis.place(x=420, y=25)
        theScoreDis.place(x=420, y=0)
        arrowTitle.place(x=420, y=75)
        self.arrowStatusDis.place(x=420, y=100)
        lastMoveDis.place(x=420, y=150)
        pastMoveDis.place(x=420, y=175)
        perceptsTitle.place(x=5, y=420)
        perceptsDis.place(x=5, y=445)
        agentDirectionTitle.place(x=420, y=285)
        agentDirectionDis.place(x=420, y=312)

        # creating the initial grid
        for r in range(ROWS):
            for c in range(COLUMNS):
                tkimage = self.set_room(r, c, simulation)
                self.grid['room' + str(r) + str(c)] = Label(master, image=tkimage)
                self.grid['room' + str(r) + str(c)].image = tkimage
                self.grid['room' + str(r) + str(c)].place(x=c * 100 + c * 2, y=r * 100 + r * 2)

        # initializations

    def update_move(self, sim):
        self.score.set(str(sim.score))
        self.pastMove.set(sim.lastMove)
        self.agentDirection.set(sim.agentFacing.title())
        if sim.arrow == 0:
            self.arrowStatus.set('Used')
            self.arrowStatusDis.config(fg='Red')
        if sim.lastPos != sim.agentPos:
            r = sim.lastPos[0]
            c = sim.lastPos[1]
            tempImg = self.set_room(r, c, sim)
            self.grid['room' + str(r) + str(c)].config(image=tempImg)
            self.grid['room' + str(r) + str(c)].image = tempImg
        r = sim.agentPos[0]
        c = sim.agentPos[1]
        tempImg = self.set_room(r, c, sim)
        self.grid['room' + str(r) + str(c)].config(image=tempImg)
        self.grid['room' + str(r) + str(c)].image = tempImg
        currentPercepts = sim.percepts['room' + str(sim.agentPos[0]) + str(sim.agentPos[1])]
        self.percepts.set(str(currentPercepts))
        if sim.hasGold:
            self.goldStatus.place(x=500, y=225)
        if sim.arrow == 0:
            self.arrowStatus.set('Used')
        if not sim.wumpusAlive:
            loc = sim.wumpusLoc
            if sim.agentPos != sim.wumpusLoc:
                temp = PhotoImage(file="Images/dead-wumpus.gif")
            else:
                temp = self.set_room(loc[0], loc[1], sim)
            self.grid['room' + str(loc[0]) + str(loc[1])].config(image=temp)
            self.grid['room' + str(loc[0]) + str(loc[1])].image = temp

    def reset_display(self, sim):
        for r in range(ROWS):
            for c in range(COLUMNS):
                tkimage = self.set_room(r, c, sim)
                self.grid['room' + str(r) + str(c)].config(image=tkimage)
                self.grid['room' + str(r) + str(c)].image = tkimage
        self.score.set(str(sim.score))
        self.pastMove.set(sim.lastMove)
        self.agentDirection.set(sim.agentFacing.title())
        self.arrowStatus.set('Available')
        self.arrowStatusDis.config(fg='Green')
        currentPercepts = sim.percepts['room' + str(sim.agentPos[0]) + str(sim.agentPos[1])]
        self.percepts.set(str(currentPercepts))
        self.goldStatus.place_forget()


# RUN SIMULATION WHILE WRITING TO standard output
test1 = TestDungeon(wumpus_loc=(0, 1), pit_locs=[], gold_loc=(1, 1))
test2 = TestDungeon(wumpus_loc=(2, 2), pit_locs=[], gold_loc=(2, 0))
test3 = TestDungeon(wumpus_loc=(3, 3), pit_locs=[(2, 1)], gold_loc=(0, 0))
test4 = TestDungeon(wumpus_loc=(3, 3), pit_locs=[(0, 0), (1, 0), (2, 3)], gold_loc=(2, 2))
test5 = TestDungeon(wumpus_loc=(0, 2), pit_locs=[(0, 1), (0, 3), (1, 3), (3, 2)], gold_loc=(0, 0))
test6 = TestDungeon(wumpus_loc=(1, 0), pit_locs=[(0, 1), (1, 3), (2, 3)], gold_loc=(0, 3))
tests = [test1, test2, test3, test4, test5, test6]

agents = [WWAgent, WWRationalAgent]
results = {agents[0]: {"TestDungeon" + str(i + 1): [] for i in range(len(tests))},
           agents[1]: {"TestDungeon" + str(i + 1): [] for i in range(len(tests))}}

print("Running Performance Tests -- Comparing Random Agent vs. Rational Agent...")
print('------------------------------------------------------------------')
for agent in agents:
    print("Testing", str(len(tests)), "Dungeons with", agent() if str(agent()) == "Rational Agent" else "Random Agent")
    for i, test in enumerate(tests):
        print("Running TestDungeon" + str(i + 1), "50 times...")
        print(test)
        wins = 0
        deaths = 0
        escapes = 0
        total_score = 0
        for j in range(50):
            if str(agent()) == "Rational Agent":
                a = agent(True)
            else:
                a = agent()
            sim = PerformanceSimulation(a, ROWS, COLUMNS, 0)
            sim.generate_simulation(test)
            wl = sim.wumpusLoc
            gl = sim.goldLocation
            pl = test.pit_locs
            moveCount = 0

            # Print the steps
            print('\nSTART OF SIMULATION', j + 1, "of 50")
            while sim.terminal_test() is not True:
                # print('------------------------------------------------------------------')
                # print('Move: ', moveCount)
                # print('Last Action: ', sim.lastMove)
                # print('\n')
                # print('Wumpus World Item Locations:')
                # print('Wumpus Location: ', wl, '   Gold Location: ', gl)
                # print('Pit Locations: ', str(pl))
                # print('\n')
                # print('Agent Info:')
                # print('Position: ', sim.agentPos, '   Facing: ', sim.agentFacing)
                # print('Has Gold: ', str(sim.hasGold), '   Arrow: ', sim.arrow)
                # print('\n')
                # print('Simlulation Current States:')
                # print('Wumpus Alive: ', str(sim.wumpusAlive), '   Performance: ', sim.score)
                # print('Current Percepts: ', str(sim.percepts['room' + str(sim.agentPos[0]) + str(sim.agentPos[1])]))
                # Prompt agent to move
                sim.move()
                sim.update_score()
                moveCount = moveCount + 1
            # Print final result
            # print('------------------------------------------------------------------')
            print('Last Action: ', sim.lastMove)
            print('GAME OVER')
            left_dungeon = sim.lastMove.lower() == 'climb'
            won = sim.hasGold
            pit = False
            wumpus = sim.agentPos == sim.wumpusLoc

            if left_dungeon:
                print('Agent has climbed out of cave.')
                escapes += 1
            elif won:
                print('Agent found and grabbed the gold!')
                wins += 1
            elif wumpus:
                print('Agent was eaten by the wumpus and died!')
                deaths += 1
            else:
                pit = True
                deaths += 1
                print('Agent fell into pit and died!')
            print('Final Performance: ', sim.score, "\n")
            total_score += sim.score
        avg_score = total_score / 50.0
        results[agent]["TestDungeon" + str(i + 1)].append({"Avg Score": avg_score,
                                                           "Wins": wins,
                                                           "Deaths": deaths,
                                                           "Escapes": escapes})

random_agent_results = []
rational_agent_results = []
result_list = [random_agent_results, rational_agent_results]

for i, (agent, tests) in enumerate(results.items()):
    for j, (test, data) in enumerate(tests.items()):
        df = pd.DataFrame(data)
        df['Test'] = "TestDungeon" + str(j + 1)
        df['Agent'] = "Random Agent" if i == 0 else "Rational Agent"
        df = df[['Test', 'Agent', 'Avg Score', 'Wins', 'Deaths', 'Escapes']]
        result_list[i].append(df)

    all_dungeons = result_list[i][0]
    j = 1
    while j < len(result_list[i]):
        all_dungeons = all_dungeons.append(result_list[i][j])
        j += 1
    result_list[i] = all_dungeons

random = result_list[0]
rational = result_list[1]
df = pd.concat([random, rational])
index = list(rational['Test'])

score_comparison = pd.DataFrame({'Random Agent': list(random['Avg Score']),
                                 'Rational Agent': list(rational['Avg Score'])},
                                 index=index)

win_comparisons = pd.DataFrame({'Random Agent': list(random['Wins']),
                                'Rational Agent': list(rational['Wins'])},
                                index=index)

death_comparisons = pd.DataFrame({'Random Agent': list(random['Deaths']),
                                  'Rational Agent': list(rational['Deaths'])},
                                  index=index)

score_comparison.plot.bar()
plt.title("Avg Scores of Random vs Rational Agent")
plt.gcf().subplots_adjust(bottom=0.35)
fig = plt.gcf()
fig.savefig(r'C:\Users\hgore\OneDrive - Fordham University\Documents\Fordham\Year 1\Winter\AI\wumpus-world\score.png')

win_comparisons.plot.bar()
plt.title("Number of Wins per Test Dungeon of Random vs Rational Agent")
plt.gcf().subplots_adjust(bottom=0.35)
fig = plt.gcf()
fig.savefig(r'C:\Users\hgore\OneDrive - Fordham University\Documents\Fordham\Year 1\Winter\AI\wumpus-world\wins.png')

death_comparisons.plot.bar()
plt.title("Number of Deaths per Test Dungeon of Random vs Rational Agent")
plt.gcf().subplots_adjust(bottom=0.35)
fig = plt.gcf()
fig.savefig(r'C:\Users\hgore\OneDrive - Fordham University\Documents\Fordham\Year 1\Winter\AI\wumpus-world\deaths.png')
