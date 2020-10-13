class TestDungeon:
    def __init__(self, wumpus_loc, pit_locs, gold_loc):
        self.wumpus_loc = wumpus_loc
        self.pit_locs = pit_locs
        self.gold_loc = gold_loc

    def __repr__(self):
        return "Test Dungeon"

    def __str__(self):
        return "Wumpus Location: " + str(self.wumpus_loc) + "\n" + \
               "Pit Locations: " + str(self.pit_locs) + "\n" + \
               "Gold Location: " + str(self.gold_loc)
