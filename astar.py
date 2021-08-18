import pygame
import math
from queue import PriorityQueue

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('A* Visualisation')

#COLOR RGB VALUES
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (65, 225, 210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (133, 133, 133)

class Spot: #SPOT IN THE VISUALISATION
    def __init__(self, row, col, width, total_rows):
        #INSTANCE PARAMETERS
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def getPos(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == RED

    def isOpen(self):
        return self.color == GREEN

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == ORANGE

    def isEnd(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def makeClosed(self):
        self.color = RED

    def makeOpen(self):
        self.color = GREEN

    def makeBarrier(self):
        self.color = BLACK

    def makeStart(self):
        self.color = ORANGE

    def makeEnd(self):
        self.color = PURPLE

    def makePath(self):
        self.color = TURQUOISE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width)) #CAN PASS IN WIDTH TWICE BECAUSE EVERYTHING IS SQUARES

    def updateNeighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBarrier(): #IF ROW IS NOT LAST ROW IN GRID
            self.neighbours.append(grid[self.row + 1][self.col]) #APPEND NEIGHBOUR IN DOWNWARDS DIRECTION

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier(): #IF ROW IS NOT FIRST ROW IN GRID
            self.neighbours.append(grid[self.row - 1][self.col]) #APPEND NEIGHBOUR IN UPWARDS DIRECTION

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier(): #IF COLUMN IS NOT THE LEFT-MOST
            self.neighbours.append(grid[self.row][self.col - 1]) #APPEND NEIGHBOUR IN LEFT DIRECTION

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBarrier(): #IF COLUMN IS NOT THE RIGHT-MOST
            self.neighbours.append(grid[self.row][self.col + 1]) #APPEND NEIGHBOUR IN RIGHT DIRECTION

    def __lt__(self, other):
        return False

def heuristic(p1, p2): #A* HEURISTIC FUNCTION
    #MANHATTAN DISTANCE
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstructPath(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.makePath()
        draw()

def algorithm(draw, grid, start, end):
    #INITIALISATION OF A* ALGORITHM
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} #WHAT NODES CAME FROM WHERE

    #PREPARATION OF G & F SCORE LISTS
    #G SCORE = SHORTEST DISTANCE FROM START NODE TO CURRENT NODE
    #H SCORE (HEURISTIC) = ABSOLUTE DISTANCE OF CURRENT NODE FROM END NODE
    #F SCORE = H SCORE + G SCORE
    g_scores = {spot: float("inf") for row in grid for spot in row}
    g_scores[start] = 0
    f_scores = {spot: float("inf") for row in grid for spot in row}
    f_scores[start] = heuristic(start.getPos(), end.getPos())

    open_set_hash = {start} #SET OF JUST SPOT OBJECTS, NOT SCORES

    while not open_set.empty(): #WHILE WE ARE STILL CONSIDERING NODES
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] #GET THE CURRENT NODE FROM THE OPEN SET
        open_set_hash.remove(current) #TAKE CURRENT NODE OUT OF THE open_set_hash

        if current == end: #WE HAVE FOUND THE END PATH
            #RECONSTRUCTING PATH
            reconstructPath(came_from, end, draw)
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_scores[current] + 1 #ALL UNITS ARE 1, SO THE NEXT NODE IS JUST ONE UNIT FURTHER

            if temp_g_score < g_scores[neighbour]:
                came_from[neighbour] = current
                g_scores[neighbour] = temp_g_score
                f_scores[neighbour] = temp_g_score + heuristic(neighbour.getPos(), end.getPos())

                if neighbour not in open_set_hash: #IF NEIGHBOUR NOT IN OPEN SET
                    count += 1
                    open_set.put((f_scores[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.makeOpen() #MAKE NODE OPEN AS IT IS IN OPEN SET

        draw()

        if current != start:
            current.makeClosed() #CLOSE NODES WHEN THEY'RE FINISHED BEING CONSIDERED

    return False #IF WE DON'T FIND A PATH, RETURN FALSE


def makeGrid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows): #ENUMERATE ROWS
        grid.append([]) #ADD NEW EMPTY ROW TO GRID
        for j in range(rows): #ENUMERATE COLUMNS
            spot = Spot(i, j, gap, rows) #CREATE A NEW SPOT AT THIS POSITION
            grid[i].append(spot) #ADD SPOT TO GRID

    return grid

def drawGrid(window, rows, width):
    GAP = width // rows
    for i in range(rows): #ENUMERATE ROWS
        pygame.draw.line(window, GREY, (0, i * GAP), (width, i * GAP)) #DRAW GRID LINES
        for j in range(rows): #ENUMERATE COLUMNS
            pygame.draw.line(window, GREY, (j * GAP, 0), (j * GAP, width)) #DRAW VERTICAL LINES

def draw(window, grid, rows, width):
    window.fill(WHITE) #FILl SCREEN WITH WHITE

    for row in grid: #ENUMERATE THROUGH ALL ROWS IN GRID ARRAY
        for spot in row: #ENUMERATE THROUGH ALL SPOTS IN ROW
            spot.draw(window) #DRAW THAT SPOT ON THE GRID

    drawGrid(window, rows, width)
    pygame.display.update()

def getClickedPos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap #DETERMINE WHICH ROW HAS BEEN CLICKED
    col = x // gap #DETERMINE WHICH COLUMN HAS BEEN CLICKED
    return row, col

def main(window, width):
    ROWS = 50
    grid = makeGrid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]: #LEFT MOUSE BUTTON
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                spot = grid[row][col] #IDENTIFY THE SPOT IN THE GRID THAT WAS CLICKED
                if not start and spot != end: #IF THERE IS NOT YET A START POSITION SET
                    start = spot
                    start.makeStart() #MAKE THE CLICKED POSITION THE START

                elif not end and spot != start: #IF THERE IS NOT YET AN END POSITION SET
                    end = spot
                    end.makeEnd() #MAKE THE CLICKED POSITION THE END

                elif spot != end and spot != start: #IF THE CLICKED POSITION IS NEITHER THE START OR END
                    spot.makeBarrier() #MAKE THE CLICKED POSITION A BARRIER

            elif pygame.mouse.get_pressed()[2]: #RIGHT MOUSE BUTTON
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                spot = grid[row][col] #IDENTIFY THE SPOT IN THE GRID THAT WAS CLICKED
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.updateNeighbours(grid)
                    algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
                if event.key == pygame.K_r and not started:
                    for row in grid:
                        for spot in row:
                            spot.reset()
                    start = None
                    end = None

    pygame.quit()

main(WINDOW, WINDOW_WIDTH)
