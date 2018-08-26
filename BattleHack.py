"""
#########################
#   Functionality       #
#########################
1. Determine which bots are on own team
   - Set signal
   - Determine team
2. Form nexus
   -

#########################
#   Strategy            #
#########################
1. On random spawn
   - Move towards CONGREGATION_LOCATION
     - If CONGREGATION_LOCATION is a hole, congregate north of it
2. Once four friendly bots see each other
   1. Form NEXUS
   2. Expand
3. Once a nexus sees enemies
"""

CONGREGATION_LOCATION = {
    "x": 8,
    "y": 8,
    "pad": 3
}

DIRECTIONS = {
    "north": bc.NORTH,
    "northeast": bc.NORTHEAST,
    "east": bc.EAST,
    "southeast": bc.SOUTHEAST,
    "south": bc.SOUTH,
    "southwest": bc.SOUTHWEST,
    "west": bc.WEST,
    "northwest": bc.NORTHWEST
}

STATUSES = {
    "nexus": "nexus",
    "roaming": "roaming"
}

class MyRobot(BCAbstractRobot):

    def __init__(self, *args):
        BCAbstractRobot.__init__(self, *args)
        self.state = {
            "robots": {
                "friendly": [], # Array of authenticated friendly bot ids
                "enemy": [],
            },
            "status": STATUSES["roaming"],
            # "map" : [[-2 for _ in range(32)] for _ in range(32)],
            "moves": [],
            "turn_count": 0,
            "current": {
                "me": {},
                "visible_map": [],
                "visible_robots": None
            }
        }

    def turn(self):
        if self.state["current"]["visible_robots"] == None:
            self.state["current"]["visible_robots"] = VisibleRobots(str(self.get_visible_robots()))
        self.state["current"]["visible_map"] = self.get_visible_map()
        self.state["current"]['visible_robots'].add(str(self.get_visible_robots()))
        self.state["current"]['visible_robots'].get_visible_robots()
        self.state["current"]["me"] = self.me()
        if self.find_my_team_around_me() >= 4:
            t = self.four_bot_nexus()
            action = self.goto({"x": t[0], "y": t[1]})
        elif self.state["status"] == "roaming":
            action = self.goto(CONGREGATION_LOCATION)
        elif self.state["status"] == "nexus":
            dir_dict = {
            [-1,-1]: bc.NORTHWEST,
            [-1, 0]: bc.WEST,
            [0, -1]: bc.NORTH,
            [0, 1]:  bc.SOUTH,
            [1, 1]:  bc.SOUTHEAST,
            [-1, 1]: bc.SOUTHWEST,
            [1, -1]: bc.NORTHEAST
            }

        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == y and x == 0:
                    continue
                rel = self.get_relative_pos(x, y)
                if rel != bc.HOLE and rel != bc.EMPTY:
                    # self.log('get ready to get spanked!')
                    # self.log(dir_dict[[x, y]])
                    return self.attack(dir_dict[[x, y]])

        # self.log('no action')
        return None
        # elif self.state["status"] == "nexus":
            # action = self.four_bot_nexus()
        self.state["turn_count"] += 1
        return action

    def goto(self, destination):
        '''
        Returns a function that moves the robot closer to destination
        If destination is a hole, moves above destination
        '''
        # Oscar
        weighted_map = self.state["current"]["visible_map"]
        coordinates = {
            "x": self.state["current"]["me"]["x"],
            "y": self.state["current"]["me"]["y"]
        }
        deltas_between_robot_and_congregation = {
            "x": destination["x"] - coordinates["x"],
            "y": destination["y"] - coordinates["y"]
        }
        # Determine where destination is in terms of indexes on the visible map
        indexes_of_end_on_visible_map = {
            "x": 3 - deltas_between_robot_and_congregation["x"],
            "y": 3 - deltas_between_robot_and_congregation["y"]
        }
        # Prevent the destination indexes from going out of bounds
        if indexes_of_end_on_visible_map["x"] < 0: indexes_of_end_on_visible_map["x"] = 0
        if indexes_of_end_on_visible_map["y"] < 0: indexes_of_end_on_visible_map["y"] = 0
        if indexes_of_end_on_visible_map["x"] >= 7: indexes_of_end_on_visible_map["x"] = 6
        if indexes_of_end_on_visible_map["y"] >= 7: indexes_of_end_on_visible_map["y"] = 6
        # Treat robots on visible_map as holes
        for row in range(len(weighted_map)):
            for column in range(len(row)):
                if [row, column] in self.state["moves"]:
                    self.log("In moves")
                    weighted_map[row][column] = -1
                if weighted_map[row][column] != 0:
                    weighted_map[row][column] = -1
        # Determine which direction robot should ideally go towards
        def write_distances(weighted_map, x, y, distance = 0):
            if not (x < 0 or y < 0 or x >= 7 or y >= 7) or distance < weighted_map[x][y]:
                weighted_map[x][y] = distance
                weighted_map = write_distances(weighted_map, x - 1, y - 1, distance + 1)
                weighted_map = write_distances(weighted_map, x - 1, y, distance + 1)
                weighted_map = write_distances(weighted_map, x - 1, y + 1, distance + 1)
                weighted_map = write_distances(weighted_map, x, y - 1, distance + 1)
                weighted_map = write_distances(weighted_map, x, y, distance + 1)
                weighted_map = write_distances(weighted_map, x, y + 1, distance + 1)
                weighted_map = write_distances(weighted_map, x + 1, y - 1, distance + 1)
                weighted_map = write_distances(weighted_map, x + 1, y, distance + 1)
                weighted_map = write_distances(weighted_map, x + 1, y - 1, distance + 1)
            return weighted_map
        weighted_map = write_distances(weighted_map, indexes_of_end_on_visible_map["x"], indexes_of_end_on_visible_map["y"])
        directions = {
            "NORTH": weighted_map[3 - 1][3],
            "NORTHEAST": weighted_map[3 - 1][3 + 1],
            "EAST": weighted_map[3][3 + 1],
            "SOUTHEAST": weighted_map[3 + 1][3 + 1],
            "SOUTH": weighted_map[3 + 1][3],
            "SOUTHWEST": weighted_map[3 + 1][3 - 1],
            "WEST": weighted_map[3][3 - 1],
            "NORTHWEST": weighted_map[3 - 1][3 - 1]
        }
        for key in directions.keys():
            if directions[key] != -1:
                if distance_min:
                    if directions[key] < distance_min:
                        direction_best = key
                        distance_min = directions[key]
                else:
                    direction_best = key
                    distance_min = directions[key]
        self.state["moves"].append((coordinates))
        self.log(coordinates)
        self.log(directions)
        if direction_best:
            return self.move(bc[direction_best])
        else:
            return None

    def search_my_team(self, given_id):
        '''
        Returns whether or not this ID represents a robot
        that is on our team.
        RETURNS: Boolean
        '''
        # Hide
        for friendly_id in self.state['robots']['friendly']:
            if given_id == friendly_id:
                return True
        return False

    def find_my_team(self):

        # Find my team robots and cache them to status
        # Naive find_my_team function
        # RETURNS: void
        # Hide

        robots_around_me = self.get_visible_robots()
        for visible_robot in robots_around_me:
            robot_signal = visible_robot['signal']
            if robot_signal == 3:
                self.state['robots']['friendly'].append(visible_robot)
            else:
                self.state['robots']['enemy'].append(visible_robot)

    def find_my_team_around_me(self):

        # Returns the number of friendly_bots in a visible map
        # RETURNS: Integer
        # Hide

        team_count = 0
        robots_around_me = self.get_visible_robots()
        for visible_robot in robots_around_me:
            robot_signal = visible_robot['signal']
            if robot_signal == 3:
                team_count += 1
        return team_count

    def four_bot_nexus(self):
        '''
        Finds it's location that it should move to if there
        is a nexus possible.
        RETURNS x, y
        '''
        centroid_x, centroid_y = Utils.find_centroid(self.state["current"]["visible_robots"].visible_robots)
        valid = Utils.valid_centroid(centroid_x - self.me()["x"], centroid_y - self.me()["y"])
        for dy in range(-1, 2):
            if valid:
                break
            centroid_y += dy
            for dx in range(-1, 2):
                if valid:
                    break
                centroid_x += dx
                valid = Utils.valid_centroid(centroid_x - self.me()["x"], centroid_y - self.me()["y"])

        nexus_spots = [
                        [centroid_x, centroid_y + 1],
                        [centroid_x - 1, centroid_y],
                        [centroid_x + 1, centroid_y],
                        [centroid_x, centroid_y - 1]
                        ]                                   # Should check for optimization
        x = self.state["current"]["me"]["x"]
        y = self.state["current"]["me"]["y"]

        return Utils.find_closest(y, x, nexus_spots, self)

    def is_empty(self, x, y):
        '''
        Checks if bot can move to a spot.
        1) Can't if it's a hole.
        2) Can't if occupied by a player that won't probably move.
        3) Can't if another bot will probably move there. (lower bot has precidence)
        RETURNS: Boolean
        '''
        if self.get_relative_pos(x, y) == bc.EMPTY:
            return True
        return False

    def is_hole(self, x, y):
        '''
        Checks if this spot is a hole.
        RETURNS: Boolean
        '''
        if self.get_relative_pos(x, y) == bc.HOLE:
            return True
        return False

##############################
#        SIGNALER class      #
##############################
'''
Encodes and decodes signals from bots.

'''
'''
class Signaler:
    def __init__(self):
        self.keyword = 'sadbears'

    def encode_signal(self):
        lst_of_ascii = []
        for char in self.keyword:
            lst_of_ascii.append(ord(char))

        sig = sum(lst_of_ascii) % 16
        return sig

    def decode_signal(self, signal):
        pass
'''


##############################
#        UTILS class         #
##############################
'''
Functions to help with maths and what not.
STATIC
'''
class Utils:

    @staticmethod
    def find_centroid(bots):
        '''
        Finds the centroid of a list of different bots.
        RETURNS: x, y
        '''
        num_bots = len(bots)

        centroid_x = sum([b.get_x() for b in bots]) // num_bots     #look at visible bots class
        centroid_y = sum([b.get_y() for b in bots]) // num_bots     #^

        return centroid_x, centroid_y

    @staticmethod
    def valid_centroid(bot, dx, dy):
        '''
        Checks if the centroid doesn't contain any holes around it that
        would prevent a nexus. dx and dy represent distances from the current
        robot.
        RETURNS boolean.
        '''
        if bot.get_relative_pos(dx + 1, dy) == bc.HOLE:
            return False
        if bot.get_relative_pos(dx - 1, dy) == bc.HOLE:
            return False
        if bot.get_relative_pos(dx, dy + 1) == bc.HOLE:
            return False
        if bot.get_relative_pos(dx, dy - 1) == bc.HOLE:
            return False
        return True

    @staticmethod
    def find_closest(bot_x, bot_y, spaces, bot):
        '''
        Finds the closest spot in which a bot should go to start a nexus.
        RETURN: an array of spot where a[0] = x
        '''
        min_dist = -1
        closest_space = spaces[0]
        for s in spaces:
            dist = pythogorean_distance(bot_x, bot_y, s)
            if dist < min_dist and bot.get_relative_pos(s[0] - bot_x, s[1] - bot_y):
                min_dist = distance
                closest_space = s
        return s

    @staticmethod
    def pythogorean_distance(bot_x, bot_y, spot_x, spot_y):
        '''
        Finds an approximate path distance to how close
        it is to the spot.
        RETURN: The 'distance' to the spot
        '''
        dx = bot_x - spot_x
        dy = bot_y - spot_y

        return Math.sqrt(pow(dx, 2) + pow(dy, 2))

# Ben
'''
DEBUG = False
def self.log(*args):
    if DEBUG:
        print(args)
'''

class VisibleRobots:
    '''
    Class representing list of visible robots
      keeps track of all of the robots that has come across
    '''

    def __init__(self, visible_robots_string):
        '''
        Pass in the self.get_visible_robots() output
        '''
        self.robot_manager = RobotManager()
        self.my_id = None
        self.add(visible_robots_string)

    def add(self, visible_robots_string):
        '''
        Pass in the self.get_visible_robots() output
        '''
        self.parse_string(visible_robots_string)

    def get_visible_robots(self):
        '''
        returns a list of Robot objects that are seen on the screen
        '''
        return_robots = []
        my_robot = [robot for robot in self.robot_manager.visible_robots if not robot.is_me][0]
        self.robot_manager.visible_robots = [robot for robot in self.robot_manager.visible_robots if not robot.is_me]
        # my_robot = next(filter(lambda robot: robot.is_me, self.robot_manager.visible_robots))
        for robot in self.robot_manager.visible_robots:
            if robot.is_me:
                continue

            if (abs(robot.xy[0]-my_robot.xy[0]) <= 3) and (abs(robot.xy[1]-my_robot.xy[1]) <= 3):
                return_robots.append(robot)

        return return_robots

    def get_all_robots(self):
        '''
        Returns a list of all Robot objects that it has ever encounterd
        '''
        return [r for r in self.robot_manager.visible_robots if not r.is_me]

    # Private functions

    def parse_string(self, s):
        '''
        DON'T CALL THIS FUNCTION
        '''

        s = s.lstrip('[')
        s = s.rstrip(']')
        split_robots = s.split('},')
        for i, s in enumerate(split_robots):
            split_robots[i] = split_robots[i].lstrip()
            split_robots[i] = s.replace('{', '')
            split_robots[i] = split_robots[i].replace('}', '')
            split_robot = split_robots[i].split(',')


        typ, r_id, x, y, sig, is_me = "", "", -99, -99, -99, False
        for i, _ in enumerate(split_robot):
            splt = split_robot[i].replace('\'', '')

        if 'type' in splt:
            typ = splt.split(':')[1]
        elif 'id' in splt:
            r_id = splt.split(':')[1]
        elif 'team' in splt:
            self.log('current player')
            self.reference_self(r_id)
            is_me = True
        elif 'x' in splt:
            x = splt.split(':')[1]
        elif 'y' in splt:
            y = splt.split(':')[1]
        elif 'signal' in splt:
            sig = splt.split(':')[1]
            if typ.strip() == 'robot':
                self.robot_manager.add(r_id, x, y, sig, is_me)
                is_me = False

    def reference_self(self, id):
        self.my_id = id

class RobotManager:
    def __init__(self):
        self.visible_robots = []

    def add(self, id, x, y, signal, is_me):
        if id in self.visible_robots:
            # robot already exists
            self.visible_robots[self.visible_robots.index(id)].update(id, x, y, signal)
            self.log("updating robot")
        else:
            # did not see the robot yet
            self.visible_robots.append(Robot(id, x, y, signal, is_me))
            self.log("creating new robot")

class Robot:
    '''
    Basic robot object with 4 object variables
    '''
    def __init__(self, id, x, y, signal, is_me=False):
        self.id = id
        self.xy = (x, y)
        self.signal = signal
        self.history_signal = [self.signal]
        self.history_xy = [self.xy]
        self.is_me = is_me

    def __str__(self):
        return "id:{}, pos:{}, {}".format(self.id, self.xy, self.signal)

    def __repr__(self):
        return "|id:{}, pos:{}, {}|".format(self.id, self.xy, self.signal)

    def __eq__(self, other):
        return self.id == other

    def update(self, id, x, y, signal):
        if self.id != id:
            return Exception("robot update() tried to update a robot with different id")

        self.log((self.xy, self.signal), ((x, y), signal))

        self.signal = signal
        self.xy = (int(x), int(y))
        self.history_xy.append(self.xy)
        self.history_signal.append(self.signal)
    '''
    if __name__ == "__main__":
        a = VisibleRobots("[{'type': 'robot', 'id': 3969, 'x': 7, 'y': 2, 'signal': 0}, {'type': 'robot', 'id': 3460, 'team': 1, 'x': 3, 'y': 3, 'health': 64, 'signal': 0}, {'type': 'robot', 'id': 504, 'x': 5, 'y': 3, 'signal': 0}, {'type': 'robot', 'id': 3494, 'x': 5, 'y': 4, 'signal': 0}, {'type': 'robot', 'id': 3969, 'x': 2, 'y': 2, 'signal': 3}]")
        a.add("[{'type': 'robot', 'id': 3969, 'x': 7, 'y': 2, 'signal': 0}, {'type': 'robot', 'id': 3460, 'team': 1, 'x': 3, 'y': 3, 'health': 64, 'signal': 0}, {'type': 'robot', 'id': 504, 'x': 5, 'y': 3, 'signal': 0}, {'type': 'robot', 'id': 3494, 'x': 5, 'y': 7, 'signal': 0}, {'type': 'robot', 'id': 3969, 'x': 6, 'y': 6, 'signal': 3}]")

        self.log( "VISIBLE ROBOTS ")
        self.log( a.get_visible_robots() )

        self.log( "ALL ROBOTS ")
        self.log( a.get_all_robots() )
    '''









    
