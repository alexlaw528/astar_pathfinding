import asyncio
import pygame 
import math 
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# width = width of each cube
class Spot:
  def __init__(self, row, col, width, total_rows):
    self.row = row
    self.col = col
    self.x = row * width
    self.y = col * width
    self.color = WHITE
    self.neighbors = []
    self.width = width
    self.total_rows = total_rows
  
  def get_pos(self):
    return self.row, self.col

  # Has this spot already been looked at
  def is_closed(self):
    return self.color == RED

  def is_open(self):
    return self.color == GREEN

  def is_barrier(self):
    return self.color == BLACK
  
  def is_start(self):
    return self.color == ORANGE

  def is_end(self):
    return self.color == PURPLE

  def reset(self):
    self.color = WHITE

  def make_start(self):
    self.color = ORANGE

  def make_close(self):
    self.color = RED

  def make_open(self):
    self.color = GREEN

  def make_barrier(self):
    self.color = BLACK
  
  def make_end(self):
    self.color = TURQUOISE

  def make_path(self):
    self.color = PURPLE

  def draw(self, win):
    pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

  def update_neighbors(self, grid):
    # Straights (not a barrier)
    self.neighbors = []
    if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #S
      self.neighbors.append(grid[self.row + 1][self.col])

    if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #N
      self.neighbors.append(grid[self.row - 1][self.col])

    if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #E
      self.neighbors.append(grid[self.row][self.col + 1])

    if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #W
      self.neighbors.append(grid[self.row][self.col - 1])

    # Diagonals
    if self.col > 0 and self.row > 0 and not grid[self.row - 1][self.col - 1].is_barrier() and not (grid[self.row - 1][self.col].is_barrier() and grid[self.row][self.col-1].is_barrier()): #N-W
      self.neighbors.append(grid[self.row - 1][self.col - 1])

    if self.col < self.total_rows - 1 and self.row > 0 and not grid[self.row - 1][self.col + 1].is_barrier() and not (grid[self.row - 1][self.col].is_barrier() and grid[self.row][self.col + 1].is_barrier()): #N-E
      self.neighbors.append(grid[self.row - 1][self.col + 1])
    
    if self.col > 0 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col - 1].is_barrier() and not (grid[self.row + 1][self.col].is_barrier() and grid[self.row][self.col - 1].is_barrier()): #S-W
      self.neighbors.append(grid[self.row + 1][self.col - 1])

    if self.col < self.total_rows - 1 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier() and not (grid[self.row + 1][self.col].is_barrier() and grid[self.row][self.col + 1].is_barrier()): #S-E
      self.neighbors.append(grid[self.row + 1][self.col + 1])
         
  # less than -> how we handle when we compare two spots together
  def __lt__(self, other):
    return False

# h(n) function
def h(p1, p2):
  x1, y1 = p1 
  x2, y2 = p2
  return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw, start):
  while current in came_from:
    current = came_from[current]
    # Return out if current is at the end. Prevents changing the color of starting point
    if current.get_pos() == start.get_pos():
      return

    current.make_path()
    draw()

def algorithm(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))
  came_from = {}
  g_score = {spot: float("inf") for row in grid for spot in row}
  g_score[start] = 0
  f_score = {spot: float("inf") for row in grid for spot in row}
  f_score[start] = h(start.get_pos(), end.get_pos())

  # Initialize a hash table that mirrors the openSet(PriorityQueue) b/c PriorityQueue does not allow for lookups
  open_set_hash = {start}

  while not open_set.empty():
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()

    # Grab starting node
    current = open_set.get()[2] 
    open_set_hash.remove(current)

    # End condition
    if current == end:
      reconstruct_path(came_from, end, draw, start)
      end.make_end()
      return True

    # neighbor temp_g_score dependent on position of neighbor relative to current (diagonal or straight) 
    crow, ccol = current.get_pos()
    for neighbor in current.neighbors:
      nrow, ncol = neighbor.get_pos()
      dist_from_curr = math.sqrt(abs(crow - nrow) + abs(ccol - ncol))
      if dist_from_curr > 1:
        temp_g_score = g_score[current] + 1.4
      else: 
        temp_g_score = g_score[current] + 1

      if temp_g_score < g_score[neighbor]: 
        came_from[neighbor] = current
        g_score[neighbor] = temp_g_score
        f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

        if neighbor not in open_set_hash:
          count += 1
          open_set.put((f_score[neighbor], count, neighbor))
          open_set_hash.add(neighbor)
          neighbor.make_open()

    if current != start:
      current.make_close()

    draw()
    
  return False

def make_grid(rows, width):
  grid = []
  # integer division
  gap = width // rows
  for i in range(rows):
    grid.append([])
    for j in range(rows):
      spot = Spot(i, j, gap, rows)
      grid[i].append(spot)
  
  return grid

# draw grid lines
def draw_grid(win, rows, width):
  gap = width // rows
  for i in range(rows):
    pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows):
      pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
  win.fill(WHITE)

  for row in grid:
    for spot in row:
      spot.draw(win)

  draw_grid(win, rows, width)
  pygame.display.update()
    
def get_clicked_pos(pos, rows, width):
  gap = width // rows
  y, x = pos

  row = y // gap
  col = x // gap
  return row, col

async def main(win, width):
  ROWS = 10
  grid = make_grid(ROWS, WIDTH)
  start = None
  end = None
  run = True

  while run:
    draw(win, grid, ROWS, width)

    for event in pygame.event.get():
      
      if event.type == pygame.QUIT:
        run = False

      # prevents user from changing conditions during runtime
      if pygame.mouse.get_pressed()[0]: # Left-click
        # Grab grid position
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_pos(pos, ROWS, width)
        spot = grid[row][col]

        # Initialize starting point if it hasn't been set & ensure it cannot equal end position
        if not start and spot != end:
          start = spot
          start.make_start()

        # Initialize ending point if it hasn't been set
        elif not end and spot != start:
          end = spot
          end.make_end()
        elif spot != end and spot != start:
          spot.make_barrier()

      # right-click
      elif pygame.mouse.get_pressed()[2]: # Right-click
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_pos(pos, ROWS, width)
        spot = grid[row][col]
        spot.reset()

        if spot == start:
          start = None
        if spot == end:
          end = None
      
      
      # Run algo
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE and start and end:
          for row in grid:
            for spot in row:
              spot.update_neighbors(grid)
          algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
          pygame.display.update()

        # press c to clear
        if event.key == pygame.K_c:
          start = None
          end = None
          grid = make_grid(ROWS, width)

    await asyncio.sleep(0)

  pygame.quit()

# main(WIN, WIDTH)
asyncio.run( main(WIN, WIDTH) )

