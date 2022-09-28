"""Sokoban routines.

    A) Class SokobanState

    A specialization of the StateSpace Class that is tailored to the game of Sokoban.

    B) class Direction

    An encoding of the directions of movement that are possible for robots in Sokoban.

    Code also contains a list of 40 Sokoban problems for the purpose of testing.
"""

from search import *

class SokobanState(StateSpace):

    def __init__(self, action, gval, parent, width, height, robot, boxes, storage, obstacles,
                 restrictions=None, box_colours=None, storage_colours=None):
        """
        Create a new Sokoban state.

        @param width: The room's X dimension (excluding walls).
        @param height: The room's Y dimension (excluding walls).
        @param robot: A tuple of the robot's location.
        @param boxes: A dictionary where the keys are the coordinates of each box, and the values are the index of that box's restriction.
        @param storage: A dictionary where the keys are the coordinates of each storage point, and the values are the index of that storage point.
        @param obstacles: A frozenset of all the impassable obstacles.
        @param restrictions: A tuple of frozensets of valid storage coordinates for each box. None means that all storage locations are valid.
        @param box_colours: A mapping from each box to the colour to use with the visualizer.
        @param storage_colours: A mapping from each storage location to the colour to use with the visualizer.
        """
        StateSpace.__init__(self, action, gval, parent)
        self.width = width
        self.height = height
        self.robot = robot
        self.boxes = boxes
        self.storage = storage
        self.obstacles = obstacles
        self.restrictions = restrictions
        self.box_colours = box_colours
        self.storage_colours = storage_colours
# Successors function
    def successors(self):
        """
        Generate all the actions that can be performed from this state, and the states those actions will create.        
        """
        successors = []
        transition_cost = 1

        for direction in (UP, RIGHT, DOWN, LEFT):
            new_location = direction.move(self.robot)
            
            if new_location[0] < 0 or new_location[0] >= self.width:
                continue
            if new_location[1] < 0 or new_location[1] >= self.height:
                continue
            if new_location in self.obstacles:
                continue
            
            new_boxes = dict(self.boxes)

            if new_location in self.boxes:
                new_box_location = direction.move(new_location)
                
                if new_box_location[0] < 0 or new_box_location[0] >= self.width:
                    continue
                if new_box_location[1] < 0 or new_box_location[1] >= self.height:
                    continue
                if new_box_location in self.obstacles:
                    continue
                if new_box_location in new_boxes:
                    continue
                
                index = new_boxes.pop(new_location)
                new_boxes[new_box_location] = index
            
            new_robot = tuple(new_location)

            new_state = SokobanState(action=direction.name, gval=self.gval + transition_cost, parent=self,
                                     width=self.width, height=self.height, robot=new_robot,
                                     boxes=new_boxes, storage=self.storage, obstacles=self.obstacles,
                                     restrictions=self.restrictions, box_colours=self.box_colours,
                                     storage_colours=self.storage_colours)
            successors.append(new_state)

        return successors

    def hashable_state(self):
        """
        Return a data item that can be used as a dictionary key to UNIQUELY represent a state.
        """
        return hash((self.robot, frozenset(self.boxes.items())))

    # Initiate function
    def state_string(self):
        """
        Return a string representation of a state that can be printed to stdout.

        disable_terminal_colouring turns off terminal colouring for terminals
        that do not support ansi characters
        """
        disable_terminal_colouring = False
        fg_colours = {
            'red': '\033[31m',
            'cyan': '\033[36m',
            'blue': '\033[34m',
            'green': '\033[32m',
            'magenta': '\033[35m',
            'yellow': '\033[33m',
            'normal': '\033[0m'
        }
        bg_colours = {
            'red': '\033[41m',
            'cyan': '\033[46m',
            'blue': '\033[44m',
            'green': '\033[42m',
            'magenta': '\033[45m',
            'yellow': '\033[43m',
            'normal': '\033[0m'
        }
        map = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                row += [' ']
            map += [row]
        if self.storage_colours:
            if disable_terminal_colouring:
                for storage_point in self.storage:
                    map[storage_point[1]][storage_point[0]] = self.storage_colours[self.storage[storage_point]][0:1].upper()
            else:
                for storage_point in self.storage:
                    map[storage_point[1]][storage_point[0]] = bg_colours[self.storage_colours[self.storage[storage_point]]] + '.' + bg_colours['normal']
        else:
            for (i, storage_point) in enumerate(self.storage):
                map[storage_point[1]][storage_point[0]] = 'S'
        for obstacle in self.obstacles:
            map[obstacle[1]][obstacle[0]] = 'O'
        map[self.robot[1]][self.robot[0]] = 'R'
        if self.box_colours:
            if disable_terminal_colouring:
                for box in self.boxes:
                    if box in self.storage:
                        if self.restrictions is None or box in self.restrictions[self.boxes[box]]:
                            map[box[1]][box[0]] = 'B'
                        else:
                            map[box[1]][box[0]] = 'B'
                    else:
                        map[box[1]][box[0]] = self.box_colours[self.boxes[box]][0:1].lower()
            else:
                for box in self.boxes:
                    if box in self.storage:
                        if self.restrictions is None or box in self.restrictions[self.boxes[box]]:
                            map[box[1]][box[0]] = bg_colours[self.storage_colours[self.storage[box]]] + fg_colours[self.box_colours[self.boxes[box]]] + 'B' + bg_colours['normal']
                        else:
                            map[box[1]][box[0]] = bg_colours[self.storage_colours[self.storage[box]]] + fg_colours[self.box_colours[self.boxes[box]]] + 'x' + bg_colours['normal']
                    else:
                        map[box[1]][box[0]] = fg_colours[self.box_colours[self.boxes[box]]] + 'B' + fg_colours['normal']
        else:
            for box in self.boxes:
                if box in self.storage:
                    if self.restrictions is None or box in self.restrictions[self.boxes[box]]:
                        map[box[1]][box[0]] = 'B'
                    else:
                        map[box[1]][box[0]] = 'B'
                else:
                    map[box[1]][box[0]] = 'B'

        for y in range(0, self.height):
            map[y] = ['O'] + map[y]
            map[y] = map[y] + ['O']
        map = ['O' * (self.width + 2)] + map
        map = map + ['O' * (self.width + 2)]

        s = ''
        for row in map:
            for char in row:
                s += char
            s += '\n'

        return s        

    def print_state(self):
        """
        Print the string representation of the state. ASCII art FTW!
        """        
        print("ACTION was " + self.action)      
        print(self.state_string())


def sokoban_goal_state(state):
  """
  Returns True if we have reached a goal state.

  @param state: a sokoban state
  OUTPUT: True (if goal) or False (if not)
  """
  if state.restrictions is None:
    for box in state.boxes:
      if box not in state.storage:
        return False
    return True
  for box in state.boxes:
    if box not in state.restrictions[state.boxes[box]]:
      return False
  return True

def generate_coordinate_rect(x_start, x_finish, y_start, y_finish):
    """
    Generate tuples for coordinates in rectangle (x_start, x_finish) -> (y_start, y_finish)
    """
    coords = []
    for i in range(x_start, x_finish):
        for j in range(y_start, y_finish):
            coords.append((i, j))
    return coords

"""
Sokoban Problem Set, for testing
"""
# Assignment 1 https://office365-iad-prod.instructure.com/lti/linked-share-item/820694/rce_content_item_selection
PROBLEMS = (
#Game 1
SokobanState("START", 0, None, 6, 5,  # dimensions
             (4, 0),  #robot
             {(4, 1): 0, (4, 3): 1},  #boxes
             {(5, 3): 0, (5, 4): 1},  #storage
             frozenset(((3, 0), (3, 2), (0, 3), (1, 3), (2,3), (3, 3), (0, 4), (1, 4), (2, 4), (3, 4))),  #obstacles
             None  # restrictions
             ),
#Game 2
SokobanState("START", 0, None, 6, 3,  # dimensions
             (0, 0), #robot
             {(2, 1): 0, (3, 1): 1, (4, 1): 2}, #, #boxes
             {(0, 2): 0, (1, 2): 1}, #storage
             frozenset(((3, 0))), #obstacles
             None
             #frozenset(((0, 2), (1, 2))) #restrictions,
             ),
#Game 3
SokobanState("START", 0, None, 9, 6, # dimensions
             (0, 0), #robot
             {(1, 1): 0, (1, 3): 1, (3, 1): 2, (3, 4): 3}, #, #boxes
             {(1, 0): 0, (2, 0): 1, (4, 2): 2}, #storage
             frozenset(((5, 0), (6, 0), (5, 1), (6, 1), (0,2), (2,2), (5, 2), (6,2), (3, 3), (4, 3), (5, 3), (8, 3), (3, 5), (4, 5), (5, 5))), #obstacles
             None
             #frozenset(((1, 0), (2, 0), (4, 2))) #restrictions,
             ),
#Game 4
SokobanState("START", 0, None, 6, 6, # dimensions
             (1, 1), #robot
             {(2, 1): 0, (1, 2): 1, (2, 2): 2}, #, #boxes
             {(0, 4): 0, (2, 4): 1, (4, 5): 2}, #storage
             frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (4, 1), (0, 2), (2, 3), (3, 3), (5, 3), (0, 5))), #obstacles
             None
             #frozenset(((0, 2), (1, 2))) #restrictions,
             ),
#Game 5
SokobanState("START", 0, None, 6, 5, # dimensions
             (0, 0), #robot
             {(1, 2): 0, (2, 1): 1, (3, 1): 2}, #, #boxes
             {(3, 0): 0, (4, 0): 1, (5, 0): 2}, #storage
             frozenset(((2, 0), (2, 3), (2, 4), (3, 3), (3, 4), (4, 3), (4, 4), (5, 3), (5, 4))), #obstacles
             None
             #frozenset(((0, 2), (1, 2))) #restrictions,
             ),
#Game 6
SokobanState("START", 0, None, 9, 6, # dimensions
             (5, 4), #robot
             {(1, 4): 0, (4, 4): 1, (6, 4): 2, (7, 2): 3}, #, #boxes
             {(7, 3): 0, (8, 3): 1, (7, 5): 2}, #storage
             frozenset(((2, 3), (3, 0), (3, 1), (3, 2), (4, 2), (5, 2), (5, 3), (5, 5), (6, 3), (8, 5))), #obstacles
             None
             #frozenset(((0, 2), (1, 2))) #restrictions,
             )
)
"""
Sokoban Directions: encodes directions of movement that are possible for each robot.
"""
class Direction():
    """
    A direction of movement.
    """
    
    def __init__(self, name, delta):
        """
        Creates a new direction.
        @param name: The direction's name.
        @param delta: The coordinate modification needed for moving in the specified direction.
        """
        self.name = name
        self.delta = delta
    
    def __hash__(self):
        """
        The hash method must be implemented for actions to be inserted into sets 
        and dictionaries.
        @return: The hash value of the action.
        """
        return hash(self.name)
    
    def __str__(self):
        """
        @return: The string representation of this object when *str* is called.
        """
        return str(self.name)
    
    def __repr__(self):
        return self.__str__()
    
    def move(self, location):
        """
        @return: Moving from the given location in this direction will result in the returned location.
        """
        return (location[0] + self.delta[0], location[1] + self.delta[1])


#Global Directions
UP = Direction("north", (0, -1))
RIGHT = Direction("east", (1, 0))
DOWN = Direction("south", (0, 1))
LEFT = Direction("west", (-1, 0))



  
