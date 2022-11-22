import pygame
import random
import sys
import math

pygame.init()

pygame.display.set_caption('Snake AI')

#screen settings
screen_width = 375  #600
screen_height = 375
cell_size = 25  #30
maze_size = 15  #20
obstacle_probability = 0.1
cells = []

#variables for snake AI
path_lengths = []
snake_body = []
snake_body_length = 0
food_index = 0
global prev_food

#features
target_points = 10
bfs_visualize = False
best_path_visualize = False

adjacencies = {  # Create an adjacency list.
}

visited = {  # Keep track of which nodes have been visited.
}

pred = {  # A map to keep track of the predecessor of a node in the BFS from the root node.
}

screen = pygame.display.set_mode((screen_width, screen_height))


def distance(a, b):  # Function to compute distance between two points.
    x_distance = a[0] - b[0]
    y_distance = a[1] - b[1]

    return math.sqrt(x_distance**2 + y_distance**2)


class Cell:  # Cell class
    def __init__(self, x, y, length=False, obstacle=False, current=False, food=False, body=False, node_checked=False, adjacent_checked=False, path_visualize=False):
        self.x = x
        self.y = y
        self.length = length
        self.obstacle = obstacle
        self.current = current
        self.food = food
        self.body = body

        #for visualization
        self.node_checked = node_checked
        self.adjacent_checked = adjacent_checked
        self.path_visualize = path_visualize

    def draw(self):
        cell = pygame.Rect(self.y * self.length, self.x * self.length,
                           self.length, self.length)

        if self.path_visualize:
            pygame.draw.rect(screen, (153, 255, 255), cell)
        elif self.node_checked:
            pygame.draw.rect(screen, (255, 153, 204), cell)
        elif self.adjacent_checked:
            pygame.draw.rect(screen, (255, 204, 229), cell)
        elif self.current:
            pygame.draw.rect(screen, 'green', cell)
        elif self.body:
            pygame.draw.rect(screen, (0, 204, 0), cell)
        elif self.food:
            pygame.draw.rect(screen, 'red', cell)
        elif self.obstacle:
            pygame.draw.rect(screen, 'black', cell)
        else:
            pygame.draw.rect(screen, 'white', cell)

    #finds midpoint of 2 cells
    def midpoint(self):
        return [self.x * self.length + (self.length / 2),self.y * self.length + (self.length / 2)]

    #Computes whether two cells are neighbors or not.
    def neighbors(self,cell):  
        return distance(self.midpoint(), cell.midpoint()) - self.length == 0


# Subroutine to randomly generate a map with obstacles
def init():
    global cells, adjacencies, visited, dist, pred
    cells, adjacencies = [], {}

    visited, pred, dist = {}, {}, {}

    for i in range(maze_size):
        for j in range(maze_size):
            if i == 0 and j == 0:
                cell = Cell(i, j, cell_size, current=True)
            elif random.random() < obstacle_probability:
                cell = Cell(i, j, cell_size, obstacle=True)
            else:
                cell = Cell(i, j, cell_size)

            cells.append(cell)
            visited[cell] = False

    refresh_adjacencies()


# Subroutine to make adjacency list
def refresh_adjacencies():
    global cells, adjacencies
    for i in cells:
        adjacencies[i] = []
        for j in cells:
            if (i != j and not i.obstacle and not j.obstacle and not i.body
                    and not j.body):
                if i.neighbors(j):
                    adjacencies[i].append(j)

# BFS implementation - determines if there is a path between two points and fills out the values for distances and predecessor maps.
def bfs(adjacencies, root, target, nodes, node_count):  
    global visited, pred
    queue = []

    queue.append(root)

    for node in nodes:
        visited[node] = False
        pred[node] = -1  # We assume that the root node can't be reached, so it has no predecessor to lead back to the root node.

    visited[root] = True

    while len(queue) > 0:
        val = queue[0]  # Get the first element of the queue
        if bfs_visualize:
            val.node_checked = True
            val.draw()
            pygame.display.update()
        queue.pop(0)  # Remove the first element (first in, first out)

        for i in range(len(
                adjacencies[val])):  # Iterating through all neighbors of val.
            if bfs_visualize:
                adjacencies[val][i].adjacent_checked = True
                adjacencies[val][i].draw()
                pygame.display.update()
                pygame.time.delay(200)
                adjacencies[val][i].adjacent_checked = False
                adjacencies[val][i].draw()
            if not visited[adjacencies[val][i]]:
                visited[adjacencies[val][i]] = True
                pred[adjacencies[val][i]] = val  # If val is the neighbor of the node, and val leads to the root, then the predecessor is val.

                queue.append(adjacencies[val][i])

                if adjacencies[val][i] == target:
                    if bfs_visualize:
                        val.node_checked = False
                        val.draw()
                        pygame.display.update()
                    return True

        if bfs_visualize:
            val.node_checked = False
            val.draw()
            pygame.display.update()
    return False


def best_path(adjacencies, root, target, nodes):
    if not bfs(adjacencies, root, target, nodes,len(nodes)):  # If there is no path, we return an empty list.
        return []

    path = []

    crawl = target
    path.append(crawl)  # First add the target to the path.

    while (pred[crawl] != -1):  # Next add the predecessor of the target, then the predecessor of that until you have reached the root node.
        path.append(pred[crawl])
        crawl = pred[crawl]  # We are iteratively visiting predecessors to 'crawl' back.
        if best_path_visualize:
            crawl.path_visualize = True
            crawl.draw()
            pygame.display.update()
            pygame.time.delay(200)
    
    if best_path_visualize:
        for i in path:
            i.path_visualize = False
            i.draw()
            pygame.display.update()

    return path[::-1]


#draw snake's path to food
def show_path(path):
    global snake_body_length
    while len(path) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # If there is more than one move left, change the value of the cell the agent is currently in.
        if len(path) > 1:
            #update body as head moves to next position
            current_index = cells.index(path[0])
            cells[current_index].current = False
            cells[current_index].body = True
            snake_body.append(cells[current_index])
            cells[current_index].draw()

            #remove final snake body cell as it moves
            if (len(snake_body) > snake_body_length):
                snake_body[0].body = False
                snake_body[0].draw()
                snake_body.pop(0)

            #update head
            new_index = cells.index(path[1])
            cells[new_index].current = True
            cells[new_index].draw()
        else:
            snake_body_length += 1

        path.pop(0)  # Remove the most recent step taken

        pygame.time.delay(250)
        pygame.display.update()


def main():
    init()  # Initialize the maze

    for cell in cells:
        cell.draw()
    pygame.display.update()

    #determine visualization
    global bfs_visualize, best_path_visualize
    bfs_input = input("Would you like to visualize bfs (Y/N)?")
    if (bfs_input == "Y"):
        bfs_visualize = True
    else:
        bfs_visualize = False
    best_path_input = input("Would you like to visualize the best path (Y/N)?")
    if (best_path_input == "Y"):
        best_path_visualize = True
    else:
        best_path_visualize = False

    #initialize variables and generate path
    global prev_food
    prev_food = cells[0]
    generate_next_path()

def generate_next_path():
    #new food position
    food_x = round(random.random() * (maze_size - 1) + 1)
    food_y = round(random.random() * (maze_size - 1) + 1)
    food_index = ((food_y - 1) * maze_size) + food_x
    #make sure new food doesn't overlap with snake
    while (check_on_body(cells[food_index])):
        food_x = round(random.random() * (maze_size - 1) + 1)
        food_y = round(random.random() * (maze_size - 1) + 1)
        food_index = ((food_y - 1) * maze_size) + food_x
    cells[food_index] = Cell(food_x - 1, food_y - 1, cell_size, food=True)
    #draw food
    cells[food_index].draw()
    pygame.display.update()

    #draw path
    global prev_food, adjacencies
    refresh_adjacencies()
    path = best_path(adjacencies, prev_food, cells[food_index], cells)
    print("Score:", snake_body_length)
    prev_food.food = False
    prev_food = cells[food_index]
    if len(path) == 0:  #no path to target
        print("No path available")
    elif (snake_body_length == target_points):
        print("The snake reached its target length!!")
    else:
        show_path(path)
        #recursively call function again unless lost (no path) or reached target points
        generate_next_path()


#returns true if the passed in cell is on the snake's body
#returns false if not
def check_on_body(checked_cell):
    for i in range(len(snake_body)):
        if (checked_cell.x == snake_body[i].x and checked_cell.y == snake_body[i].y):
            return True
    return False


if __name__ == '__main__':
    main()
