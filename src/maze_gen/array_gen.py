import sys, logging
import random
import numpy as np
import matplotlib.pyplot as plt
from mazelib import Maze
from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
from mazelib.generate.Kruskal import Kruskal
from mazelib.generate.Prims import Prims
from mazelib.generate.Wilsons import Wilsons
from mazelib.generate.Sidewinder import Sidewinder
from mazelib.solve.ShortestPath import ShortestPath

LOGGER = logging.getLogger(__name__)

def generate_maze(algorithm, width, height, seed, maze_exit):
    if seed == "NONE":
        m = Maze()
    else:
        m = Maze(int (seed))

    # choose a generator for maze
    if algorithm == "Backtracking":
        m.generator = BacktrackingGenerator(height, width)
    elif algorithm == "Kruskal":
        m.generator = Kruskal(height, width)
    elif algorithm == "Prims":
        m.generator = Prims(height, width)
    elif algorithm == "Wilsons":
        m.generator = Wilsons(height, width)
    elif algorithm == "Sidewinder":
        m.generator = Sidewinder(height, width)
    else:
        print("ERROR: No such algorithm supported")
        exit(1)

    m.solver = ShortestPath()

    # default solution length = r*(M + N) where r=1.5 with 0.05 padding
    length_min = int(1.45*(2*width+2*height+2))
    length_max = int(1.55*(2*width+2*height+2))

    # default exit site
    height_bug = height*2
    width_bug = width*2 - 1

    # make a maze with a solution length within min-max range
    sol_len = 0
    while sol_len < length_min or sol_len > length_max:
        m.generate()
        m.start = (0, 1)
        m.grid[0][1] = 0
        if maze_exit == "random":
            height_bug = np.random.randint(2, height)*2 - 1
            width_bug = np.random.randint(2, width)*2 - 1
        m.end = (height_bug, width_bug)
        m.grid[height_bug][width_bug] = 0
        m.solve()
        sol_len = len(m.solutions[0])
    return m

# print grid to a file
def store_maze(maze, label):
    np.set_printoptions(threshold=sys.maxsize, linewidth=310)
    with open(label + ".txt", 'w') as f:
        print(maze, file = f)

# print solution path to a file
def store_solution(maze, label, width, height):
    f = open(label + "_solution.txt", 'w')
    xy_to_num = dict()
    lis = list(range(width*height))
    for i in range(width*height):
        xy_to_num[(i // width, i % width)] = lis[i]
    for idx in range(len(maze.solutions[0])):
        if idx % 2 == 0:
            i = maze.solutions[0][idx][0]
            j = maze.solutions[0][idx][1]
            x = int((i-1)/2)
            y = int((j-1)/2)
            print(xy_to_num[(x, y)], file = f)
    f.close()

# generate a simple image of the maze
def show_png(maze, label):
    plt.figure(figsize=(width/10, height/10))
    plt.imshow(maze, cmap=plt.cm.binary, interpolation='nearest')
    plt.xticks([]), plt.yticks([])
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.savefig(label)

def apply_transforms(ttype, width, height, matrix):
    tranformations = ttype.split("_")
    for t in tranformations:
        if t.startswith("rw"):
            matrix = t_remove_walls(width, height, matrix, int(t[2:]))
    return matrix

def t_remove_walls(width, height, matrix, proportion):
    ones = []
    for i in range(1,height*2-1):
        for j in range(1,width*2-2,1):
            if((i+j)%2 == 1):
                if(matrix[i, j] == 1):
                    ones.append((i, j))
    total = len(ones)
    rm = int(total*(proportion/100))
    while (rm > 0):
        r = random.randrange(0,total-1)
        i, j = ones.pop(r)
        matrix[i,j] = 0
        total -= 1
        rm -= 1
    return matrix

def main(algorithm, width, height, seed, maze_exit, numb, t_type, t_numb):
    for index in range(numb):
        maze = generate_maze(algorithm, width, height, seed, maze_exit)
        label = algorithm + "_" + str(width) + "x" + str(height) + "_" + str(seed) + "_" + str(index) + "_" + t_type
        store_solution(maze, label, width, height)
        random.seed(seed)
        min = 0 if 'keepId' in t_type else 1
        for t_index in range(min,t_numb+1):
            grid = maze.grid.copy()
            if t_index != 0:
                grid = apply_transforms(t_type, width, height, grid)
            store_maze(grid, label+"_t"+str(t_index))
            show_png(grid, label+"_t"+str(t_index))

if __name__ == '__main__':
    algorithm = sys.argv[1]
    width, height = int (sys.argv[2]), int (sys.argv[3])
    seed = int(sys.argv[4])
    maze_exit = sys.argv[5]
    numb = int(sys.argv[6])
    t_type = sys.argv[7]
    t_numb = int(sys.argv[8])
    main(algorithm, width, height, seed, maze_exit, numb, t_type, t_numb)
