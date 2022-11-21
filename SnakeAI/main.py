import pygame
import random
import sys
import math

pygame.init()

pygame.display.set_caption('Maze Solver')

screen_width = 600
screen_height = 600

cell_size = 25 #30
maze_size = 15 #20

path_lengths = []
probability = 0.1 # The likelihood that a cell is an obstacle.
target_points = 10

cells = []
snake_body = []
snake_body_length=0
food_index = 0
global prev_food


adjacencies = { # Create an adjacency list.
    
}

visited = { # Keep track of which nodes have been visited.
    
}

pred = { # A map to keep track of the predecessor of a node in the BFS from the root node.
        
}

screen = pygame.display.set_mode((screen_width, screen_height))

def distance(a, b): # Function to compute distance between two points.
    x_distance = a[0]-b[0]
    y_distance = a[1]-b[1]
    
    return math.sqrt(x_distance**2+y_distance**2)

class Cell: # Cell class
    def __init__(self, x, y, length=False, obstacle=False, current=False, food=False, body=False):
        self.x = x
        self.y = y
        self.length = length
        self.obstacle = obstacle
        self.current = current
        self.food = food
        self.body = body
        
    def draw(self):
        
        cell = pygame.Rect(self.y * self.length, self.x * self.length, self.length, self.length)
        
        if self.obstacle:
            pygame.draw.rect(screen, 'black', cell)
        elif self.current:
            pygame.draw.rect(screen, 'green', cell)
        elif self.body:
            pygame.draw.rect(screen, (0,204,0), cell)
        elif self.food:
            pygame.draw.rect(screen, 'red', cell)
        else:
            pygame.draw.rect(screen, 'white', cell)
    
    def midpoint(self):
        return [self.x * self.length + (self.length / 2), self.y * self.length + (self.length / 2)]
    
    def neighbors(self, cell): # Method to compute whether two cells are neighbors or not.
        return distance(self.midpoint(), cell.midpoint())-self.length == 0


def init(): # Subroutine to randomly generate a maze and adjacency list.
    
    global cells, adjacencies, visited, dist, pred
    cells, adjacencies = [], {}
    
    visited, pred, dist = {}, {}, {}

    food_x = round(random.random() * maze_size)
    food_y = round(random.random() * maze_size)
    print("Coordinates:", food_x, food_y)
    for i in range(maze_size):
        for j in range(maze_size):
            if i == 0 and j == 0:
                cell = Cell(i, j, cell_size, current=True)
            elif j == food_x-1 and i == food_y-1:
                cell = Cell(i, j, cell_size, food=True)
                global food_index
                food_index=len(cells)
            elif random.random() < probability:
                cell = Cell(i, j, cell_size, obstacle=True)
            else:
                cell = Cell(i, j, cell_size)
              
            cells.append(cell)
            visited[cell] = False

    for i in cells:
        adjacencies[i] = []

        for j in cells:
            if (i != j and not i.obstacle and not j.obstacle):
                if i.neighbors(j):
                    adjacencies[i].append(j)


def refreshAdjacencies():
  global cells, adjacencies
  for i in cells:
        adjacencies[i] = []

        for j in cells:
            if (i != j and not i.obstacle and not j.obstacle and not i.body and not j.body):
                if i.neighbors(j):
                    adjacencies[i].append(j)

def bfs(adjacencies, root, target, nodes, node_count): # BFS implementation - determines if there is a path between two points and fills out the values for distances and predecessor maps.
    global visited, pred
    queue = []
    
    queue.append(root)
    
    for node in nodes:
        visited[node] = False
        
        pred[node] = -1 # We assume that the root node can't be reached, so it has no predecessor to lead back to the root node.
        
    
    visited[root] = True
    
    while len(queue) > 0:
        val = queue[0] # Get the first element of the queue
        queue.pop(0) # Remove the first element (first in, first out)
        
        for i in range(len(adjacencies[val])): # Iterating through all neighbors of val.
            
            if not visited[adjacencies[val][i]]:
                visited[adjacencies[val][i]] = True
                pred[adjacencies[val][i]] = val # If val is the neighbor of the node, and val leads to the root, then the predecessor is val.
                
                queue.append(adjacencies[val][i])
                
                if adjacencies[val][i] == target:
                    return True
    return False

def best_path(adjacencies, root, target, nodes):
    
    if not bfs(adjacencies, root, target, nodes, len(nodes)): # If there is no path, we return an empty list.
        return []
    
    path = []
    
    crawl = target
    path.append(crawl) # First add the target to the path.
    
    while (pred[crawl] != -1): # Next add the predecessor of the target, then the predecessor of that until you have reached the root node.
        path.append(pred[crawl])
        crawl = pred[crawl] # We are iteratively visiting predecessors to 'crawl' back.
    return path[::-1]
    

def show_path(path): # Main loop
    global snake_body_length
    while len(path) > 0:
        screen.fill([255, 255, 255])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
        
        for cell in cells:
            cell.draw()

        if len(path) > 1: # If there is more than one move left, change the value of the cell the agent is currently in.
            #update body
            current_index = cells.index(path[0])
            cells[current_index].current = False
            cells[current_index].body = True
          
            snake_body.append(cells[current_index])
            if(len(snake_body) > snake_body_length):
              snake_body[0].body = False
              snake_body.pop(0)

            #update head
            new_index = cells.index(path[1])
            cells[new_index].current = True
        else:
          snake_body_length+=1
        path.pop(0) # Remove the most recent step taken
        
        pygame.time.delay(250)
        
        pygame.display.update()

def main():
    init() # Initialize the maze
    path = best_path(adjacencies, cells[0], cells[food_index], cells) # compute the path

    while len(path) == 0: # If there is no path to the target node, generate a new maze until there is a path.
        init()
        path = best_path(adjacencies, cells[0], cells[food_index], cells)
        #print(cells[food_index].x, cells[food_index].y)
    global prev_food 
    prev_food = cells[food_index]
    prev_food.food = False

    show_path(path)
    generate_next_path()

def generate_next_path():
  #new food position
  food_x = round(random.random() * maze_size)
  food_y = round(random.random() * maze_size)
  print("New Coordinates:", food_x, food_y)
  food_index = ((food_y-1) * maze_size) + food_x
  #make sure new food doesn't overlap with snake
  while(check_on_body(cells[food_index])):
    food_x = round(random.random() * maze_size)
    food_y = round(random.random() * maze_size)
    #print("New Coordinates:", food_x, food_y)
    food_index = ((food_y-1) * maze_size) + food_x
  cells[food_index] = Cell(food_x-1, food_y-1, cell_size, food=True)
  print("Next food index:",food_index)
  #print("Next food coords:",cells[food_index].x, cells[food_index].y)
  
  # path = best_path(adjacencies, cells[0], cells[food_index], cells)
  # show_path(path)
  #

  
  # show_path(path)
  
  #draw path
  #TODO: pass in current cell
  global prev_food, adjacencies
  refreshAdjacencies()
  path = best_path(adjacencies, prev_food, cells[food_index], cells)
  #print("Prev food",prev_food.x,prev_food.y)
  print("Score:",snake_body_length)
  prev_food.food = False
  prev_food = cells[food_index]
  if len(path) == 0: #no path to target
    print("No path available")
  elif(snake_body_length == target_points):
    print("got score!")
  else:
    print("showing path")
    show_path(path)
    #recursively call function again unless lost (no path) or reached target points
    generate_next_path() 
  

#returns true if the passed in cell is on the snake's body #TODO: head?
#returns false if not
def check_on_body(checked_cell): #TODO: test
  for i in range(len(snake_body)):
    if(checked_cell == snake_body): #TODO: check x and y?
      return True
  return False
  
if __name__ == '__main__':
    main()