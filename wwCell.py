from typing import *


class Percept:
    def __init__(self, cell, truth_value=False):
        self.cell = cell
        self.pos = self.cell.pos
        self.truth_value = truth_value

        self.suffix = str(cell.pos[0]) + str(cell.pos[1])

    def clone(self, truth_value):
        return

    @property
    def prefix(self):
        return "" if (self.truth_value or self.truth_value is None) else "not "

    @staticmethod
    def get_type():
        return "percept"

    def __eq__(self, other):
        return type(self) == type(other) and self.pos == other.pos and str(self) == str(other)

    def __ne__(self, other):
        return type(self) != type(other) or self.pos != other.pos or str(self) != str(other)

    def __hash__(self):
        return hash((self.pos, str(self)))


class Stench(Percept):
    def __init__(self, cell, truth_value=False):
        super().__init__(cell, truth_value)

    def clone(self, truth_value):
        return Stench(self.cell, truth_value)

    @staticmethod
    def get_type():
        return "stench"

    def __str__(self):
        return self.prefix + "S" + self.suffix

    def __repr__(self):
        return self.prefix + "S" + self.suffix


class Breeze(Percept):
    def __init__(self, cell, truth_value=False):
        super().__init__(cell, truth_value)

    def clone(self, truth_value):
        return Breeze(self.cell, truth_value)

    @staticmethod
    def get_type():
        return "breeze"

    def __str__(self):
        return self.prefix + "B" + self.suffix

    def __repr__(self):
        return self.prefix + "B" + self.suffix


class Wumpus(Percept):
    def __init__(self, cell, truth_value=False):
        super().__init__(cell, truth_value)

    def clone(self, truth_value):
        return Wumpus(self.cell, truth_value)

    @staticmethod
    def get_type():
        return "wumpus"

    def __str__(self):
        return self.prefix + "W" + self.suffix

    def __repr__(self):
        return self.prefix + "W" + self.suffix


class Pit(Percept):
    def __init__(self, cell, truth_value=False):
        super().__init__(cell, truth_value)

    def clone(self, truth_value):
        return Pit(self.cell, truth_value)

    @staticmethod
    def get_type():
        return "pit"

    def __str__(self):
        return self.prefix + "P" + self.suffix

    def __repr__(self):
        return self.prefix + "P" + self.suffix


class DungeonCell:
    def __init__(self, pos, percepts=(None, None, None, None, None), pit=False, wumpus=False):
        self.pos = pos
        # self.map = map
        self.explored = self.pos == (3, 0)
        # if map is not None:
        #     self.explored = self.map[self.pos[0]][self.pos[1]].explored

        self.safe = self.explored

        self.percept_types = [Stench, Breeze, Wumpus, Pit]
        self.keys = [p.get_type() for p in self.percept_types]
        self.percepts: List[Percept] = []
        for p in self.percept_types:
            if p.get_type() == "wumpus":
                self.percepts.append(Wumpus(self, wumpus))
            elif p.get_type() == "pit":
                self.percepts.append(Pit(self, pit))
            else:
                self.percepts.append(p(self, p.get_type() in percepts))

        self.wumpus = self['wumpus']
        self.pit = self['pit']

    @property
    def adjacent_cells(self) -> List[Tuple[int, int]]:
        adjacent_positions = []
        if self.pos[0] + 1 <= 3:
            adjacent_positions.append((self.pos[0] + 1, self.pos[1]))
        if self.pos[0] - 1 >= 0:
            adjacent_positions.append((self.pos[0] - 1, self.pos[1]))
        if self.pos[1] + 1 <= 3:
            adjacent_positions.append((self.pos[0], self.pos[1] + 1))
        if self.pos[1] - 1 >= 0:
            adjacent_positions.append((self.pos[0], self.pos[1] - 1))

        return [pos for pos in adjacent_positions if pos != self.pos]

    def set_wumpus(self):
        self.wumpus = True
        self['wumpus'] = True
        self.safe = False

    def set_pit(self):
        self.pit = True
        self['pit'] = True
        self.safe = False

    def get_percept_type(self, percept) -> Type[Union[Stench, Breeze, Wumpus, Pit]]:
        for p in self.percept_types:
            if p.get_type() == percept:
                return p

    def clone(self):
        pos = self.pos
        # map = self.map
        percepts = tuple(p for p in self.keys if self[p])
        pit = self.pit
        wumpus = self.wumpus
        return DungeonCell(pos, percepts, pit, wumpus)

    def __str__(self):
        return "room" + str(self.pos[0]) + str(self.pos[1])

    def __repr__(self):
        return "room" + str(self.pos[0]) + str(self.pos[1])

    def __eq__(self, other):
        if self.pos != other.pos or self.explored != other.explored:
            return False
        else:
            for k in self.keys:
                if self[k] != other[k]:
                    return False
        return True

    def __ne__(self, other):
        if self.pos != other.pos or self.explored != other.explored:
            return True
        else:
            for k in self.keys:
                if self[k] != other[k]:
                    return True
        return False

    def __getitem__(self, item):
        return next(p.truth_value for p in self.percepts if item == p.get_type())

    def __setitem__(self, key, value):
        percept = next(p for p in self.percepts if key == p.get_type())
        if percept is None:
            self.percepts.append(self.get_percept_type(key)(self, value))
        else:
            percept.truth_value = value

    def __hash__(self):
        return hash((self.pos, self['stench'],
                     self['breeze'],
                     self['pit'],
                     self['wumpus'],
                     self.explored))
