"""
Modified from wwagent.py written by Greg Scott

Modified to only do random motions so that this can be the base
for building various kinds of agent that work with the wwsim.py
wumpus world simulation -----  dml Fordham 2019

# FACING KEY:
#    0 = up
#    1 = right
#    2 = down
#    3 = left

# Actions
# 'move' 'grab' 'shoot' 'left' right'

"""
from typing import *
from copy import deepcopy
from itertools import combinations
from wwCell import *

# This is the class that represents an agent


class WWRationalAgent:

    def __init__(self, test=False):
        self.max = 4  # number of cells in one side of square world
        self.position = (3, 0)  # top is (0,0)
        self.last_position = (3, 0)
        self.last_move = "Entered dungeon"
        self.next_position = (3, 0)

        self.directions = ['up', 'right', 'down', 'left']
        self.facing = 'right'
        self.arrow = 1

        self.keys = ["stench", "breeze", "glitter", "wumpus", "pit"]
        self.percepts = []

        self.map: List[List[DungeonCell]] = self.create_map()
        self.map[self.position[0]][self.position[1]].explored = True

        self.wumpus_position = (0, 0)
        self.knows_wumpus_position = False
        self.killed_wumpus = False

        # self.kb = set()
        self.kb: Set[Union[Stench, Breeze, Wumpus, Pit]] = \
            {percept for percept in self.map[self.position[0]][self.position[1]].percepts}
        self.journey = {(self.position[0], self.position[1]): 1}

        self.test = test

        print("New Rational Agent created")

    # Add the latest percepts to list of percepts received so far
    # This function is called by the wumpus simulation and will
    # update the sensory data. The sensor data is placed into a
    # map structured KB for later use

    def update(self, percepts):
        self.percepts = [p for p in percepts if p is not None]
        if 'glitter' in self.percepts:
            return

        if self.position[0] in range(self.max) and self.position[1] in range(self.max):
            self.map[self.position[0]][self.position[1]].explored = True
            self.add_safe_position(self.map[self.position[0]][self.position[1]])

        if not self.percepts:
            for move in self.adjacent_positions:
                self.add_safe_position(move)

        else:
            self.update_kb()

    @property
    def adjacent_positions(self) -> Union[List['DungeonCell'], List[Tuple]]:
        adjacent_positions = []
        if self.position[0] + 1 <= 3:
            adjacent_positions.append((self.position[0] + 1, self.position[1]))
        if self.position[0] - 1 >= 0:
            adjacent_positions.append((self.position[0] - 1, self.position[1]))
        if self.position[1] + 1 <= 3:
            adjacent_positions.append((self.position[0], self.position[1] + 1))
        if self.position[1] - 1 >= 0:
            adjacent_positions.append((self.position[0], self.position[1] - 1))

        adjacent_positions.reverse()
        return [self.map[pos[0]][pos[1]] for pos in adjacent_positions if pos != self.position]

    # Since there is no percept for location, the agent has to predict
    # what location it is in based on the direction it was facing
    # when it moved

    def calculateNextPosition(self, action):
        self.last_position = self.position
        if self.facing == 'up':
            self.position = (min(self.max - 1, self.position[0] - 1), self.position[1])
        elif self.facing == 'down':
            self.position = (min(self.max - 1, self.position[0] + 1), self.position[1])
        elif self.facing == 'right':
            self.position = (self.position[0], min(self.max - 1, self.position[1] + 1))
        elif self.facing == 'left':
            self.position = (self.position[0], min(self.max - 1, self.position[1] - 1))

        if self.position in [cell.pos for cell in self.safe_positions]:
            self.journey[(self.position[0], self.position[1])] += 1
        else:
            self.journey[(self.position[0], self.position[1])] = 1

        self.map[self.position[0]][self.position[1]].explored = True
        self.last_move = 'move ' + self.facing
        return self.position

    # and the same is true for the direction the agent is facing, it also
    # needs to be calculated based on whether the agent turned left/right
    # and what direction it was facing when it did

    def calculateNextDirection(self, action):
        if self.facing == 'up':
            if action == 'left':
                self.facing = 'left'
            else:
                self.facing = 'right'
        elif self.facing == 'down':
            if action == 'left':
                self.facing = 'right'
            else:
                self.facing = 'left'
        elif self.facing == 'right':
            if action == 'left':
                self.facing = 'up'
            else:
                self.facing = 'down'
        elif self.facing == 'left':
            if action == 'left':
                self.facing = 'down'
            else:
                self.facing = 'up'
        self.last_move = 'rotated ' + self.facing

    # this is the function that will pick the next action of
    # the agent using truth table enumeration.

    def action(self):
        """
        Choose an action based on self.kb
        :return: a valid Wumpus World action
        """
        if 'glitter' in self.percepts:
            return self.grab_gold()

        if 'rotated' in self.last_move:
            return self.get_action()

        if self.journey[self.last_position] > 3:
            return self.exit_dungeon(self.test)

        valid_moves = self.get_valid_moves()
        if len(valid_moves) == 0:
            return self.exit_dungeon(self.test)
        unexplored = [move for move in valid_moves if not move.explored]

        self.next_position = self.get_next_position(valid_moves, unexplored)

        action = self.get_action()

        if not self.test:
            print("Rational agent:", action, "-->", self.position[0], self.position[1], self.facing)
        return action

    # Truth Table Enumeration Methods
    def tt_entails(self, alpha: Percept):
        """
        Checks that self.map entails alpha
        :param alpha: a query for model checking.
        :return:
        """
        if alpha.get_type() == 'wumpus':
            symbols = {percept.clone(None) for percept in self.kb
                       if (percept.cell in self.adjacent_positions or percept.pos == self.position)
                       and percept.get_type() == 'stench'}
        else:
            symbols = {percept.clone(None) for percept in self.kb
                       if (percept.cell in self.adjacent_positions or percept.pos == self.position)
                       and percept.get_type() == 'breeze'}
        symbols.add(alpha.clone(None))
        symbols = [symbol for symbol in symbols]
        return self.tt_checkall(alpha, symbols, set())

    def tt_checkall(self, alpha: Percept, symbols: List[Percept], model: Set):
        def add(s, cell):
            s.add(cell)
            return s

        if len(symbols) == 0:
            if self.pl_true(self.kb, model):
                return self.pl_true([alpha], model)
            else:
                return True
        else:
            p = symbols[0]
            rest = symbols[1:]
            p_true = self.tt_checkall(alpha, rest, add(model, p.clone(True)))
            if not p_true:
                return False
            p_false = self.tt_checkall(alpha, rest, add(model, p.clone(False)))
            if not p_false:
                return False
            return True

    @staticmethod
    def pl_true(query, model):
        for q in query:
            for percept in model:
                if q.get_type() == percept.get_type():
                    if q.pos == percept.pos:
                        if q != percept:
                            return False
                    continue
        return True

    # Helper Methods
    def create_map(self):  # , query=False):
        return [[DungeonCell((i, j), percepts=self.percepts) for j in range(self.max)] for i in range(self.max)]

    def get_valid_moves(self):
        """
        Removes "bad" moves from possible_moves through model checking for pits and wumpuses in possible next positions.
        :return: possible_moves with bad moves filtered out
        """
        bad_moves = []
        for move in self.adjacent_positions:
            if move in self.safe_positions:
                continue
            if 'stench' in self.percepts and not self.knows_wumpus_position:
                if self.tt_entails(Wumpus(move, True)):
                    bad_moves.append(move)
            if 'breeze' in self.percepts:
                if self.tt_entails(Pit(move, True)):
                    bad_moves.append(move)

        return [move for move in self.adjacent_positions if move not in bad_moves]

    def get_next_position(self, valid, unexplored):
        if len(unexplored) > 0:
            return unexplored[0].pos
        elif len(valid) > 1:
            retraceable = {k: v for k, v in self.journey.items() if self.map[k[0]][k[1]] in valid}
            fewest_visits = min(retraceable, key=retraceable.get)
            return self.map[fewest_visits[0]][fewest_visits[1]].pos
            # return [move for move in valid if move.pos != self.last_position][0].pos
        else:
            return valid[0].pos

    def update_kb(self):
        unexplored = [cell for cell in self.adjacent_positions if not cell.explored]
        if 'scream' in self.percepts:
            self.percepts.remove('scream')
            self.dead_wumpus()
            if 'stench' in self.percepts:
                self.percepts.remove('stench')
                self.map[self.position[0]][self.position[1]]['stench'] = False

        for p in self.percepts:
            self.map[self.position[0]][self.position[1]][p] = True

        for p in self.map[self.position[0]][self.position[1]].percepts:
            self.add_to_kb(p)

        for cell in unexplored:
            safe = True
            if self.possible_hazard(cell, 'stench'):
                self.add_to_kb(Wumpus(cell, True))
                safe = False
            if self.possible_hazard(cell, 'breeze'):
                self.add_to_kb(Pit(cell, True))
                safe = False
            if safe:
                self.add_safe_position(cell)

    def possible_hazard(self, cell: DungeonCell, percept) -> bool:
        explored = [self.map[pos[0]][pos[1]] for pos in cell.adjacent_cells if self.map[pos[0]][pos[1]].explored]
        count = 0
        for c in explored:
            if c[percept]:
                count += 1
        return count == len(explored)

    @property
    def safe_positions(self):
        return [self.map[i][j] for (i, j) in list(self.journey.keys())]

    def add_safe_position(self, cell):
        for percept in cell.percepts:
            self.add_to_kb(percept)
        cell.safe = True
        cell.wumpus = False
        cell.pit = False

        if not cell.explored:
            self.journey[(cell.pos[0], cell.pos[1])] = 0

    def add_to_kb(self, percept):
        old_knowledge = []
        possible_wumpus = []
        for p in self.kb:
            if percept.get_type() == p.get_type():
                if percept.pos == p.pos:
                    if percept != p:
                        old_knowledge.append(p)
                if p.get_type() == 'wumpus' and not self.knows_wumpus_position:
                    if p.truth_value and not percept.truth_value:
                        possible_wumpus.append(p.cell)

        if len(possible_wumpus) == 1 and not self.knows_wumpus_position:
            possible_wumpus = possible_wumpus[0]
            possible_wumpus.set_wumpus()
            self.wumpus_position = possible_wumpus.pos
            self.knows_wumpus_position = True

        self.kb.add(percept)
        self.kb = {p for p in self.kb if p not in old_knowledge}

    def get_possible_moves(self):
        return [cell for cell in self.adjacent_positions]

    def get_action(self):
        action = 'move'
        if self.next_position[1] == self.position[1] + 1:
            if self.facing == 'right':
                action = 'move'
            elif self.facing == 'left' or self.facing == 'down':
                action = 'left'
            elif self.facing == 'up':
                action = 'right'

        elif self.next_position[0] == self.position[0] - 1:
            if self.facing == 'up':
                action = 'move'
            elif self.facing == 'right' or self.facing == 'down':
                action = 'left'
            elif self.facing == 'left':
                action = 'right'

        elif self.next_position[1] == self.position[1] - 1:
            if self.facing == 'left':
                action = 'move'
            elif self.facing == 'right' or self.facing == 'up':
                action = 'left'
            elif self.facing == 'down':
                action = 'right'

        elif self.next_position[0] == self.position[0] + 1:
            if self.facing == 'down':
                action = 'move'
            elif self.facing == 'left' or self.facing == 'up':
                action = 'left'
            elif self.facing == 'right':
                action = 'right'

        if action == 'move':
            if self.knows_wumpus_position and self.next_position == self.wumpus_position and not self.killed_wumpus:
                self.last_move = 'shot arrow'
                return 'shoot'
            self.position = self.calculateNextPosition(action)
        else:
            self.calculateNextDirection(action)

        return action

    def dead_wumpus(self):
        if self.last_move == 'shot arrow':
            self.last_move = 'killed wumpus'
            self.killed_wumpus = True
            self.map[self.wumpus_position[0]][self.wumpus_position[1]]['wumpus'] = False
            self.add_safe_position(self.map[self.wumpus_position[0]][self.wumpus_position[1]])

    def grab_gold(self):
        if self.last_move == 'picked up gold':
            if not self.test:
                print("The agent has the gold! Climbing out...")
                exit()
            return 'climb'
        else:
            self.last_move = 'picked up gold'
            if not self.test:
                print("Rational agent: ", self.last_move)
            return 'grab'

    @staticmethod
    def exit_dungeon(test=False):
        if test:
            print("This dungeon is not safe! Climbing out...")
            return 'climb'
        exit()

    def __str__(self):
        return "Rational Agent"
