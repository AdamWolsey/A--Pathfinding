import pygame
import sys
import random

# | ----------------------------- A* Pathfinding Alogrithm -----------------------------|

def a_star(start_pos, end_pos, wall_pos, boundaries):
    # Initialize open nodes with the start position, containing its parent, g_cost, h_cost, and f_cost
    # open_nodes: nodes that are to be evaluated
    open_nodes = {start_pos: {"parent": (0, 0), "g_cost": 0, "h_cost": 0, "f_cost": 0}}
    
    # closed_nodes: nodes that have already been evaluated
    closed_nodes = {}

    # A flag to check if the path is found
    found_path = False
    
    # Continue the loop until the path is found or open_nodes is empty
    while not found_path:
        # If there are no more open nodes to evaluate, return an empty path (no valid path exists)
        if open_nodes == {}:
            return []
        
        # Select the node with the lowest f_cost (current best guess for the shortest path)
        current_node = min(open_nodes, key=lambda k: open_nodes[k]["f_cost"])
        
        # If the current node is the end position, reconstruct the path
        if current_node == end_pos:
            path = []
            parent = open_nodes[current_node]["parent"]
            # Reconstruct the path by following the parent nodes back to the start position
            while parent != start_pos:
                path.append(parent)
                parent = closed_nodes[parent]["parent"]
                
            # Return the path in the correct order from start to end
            return path[::-1]

        # Move the current node from open to closed (meaning it's evaluated)
        closed_nodes[current_node] = open_nodes[current_node]
        open_nodes.pop(current_node)

        # Define the neighboring nodes (up, down, left, right) in a 2D grid
        neighbors = [
            (current_node[0], current_node[1] - 1),  # Left
            (current_node[0] - 1, current_node[1]),  # Up
            (current_node[0] + 1, current_node[1]),  # Down
            (current_node[0], current_node[1] + 1)   # Right
        ]
        
        # Loop through each neighbor
        for neighbor in neighbors:
            # Check if the neighbor is out of bounds, in the closed nodes, or is a wall; skip if so
            if neighbor in closed_nodes or neighbor in wall_pos or neighbor[0] < 0 or neighbor[1] < 0 or neighbor[0] >= boundaries[0] or neighbor[1] >= boundaries[1]:
                continue

            # Calculate g_cost (distance from start to the neighbor)
            g_cost = abs(current_node[0] - neighbor[0]) + abs(current_node[1] - neighbor[1])
            
            # Calculate h_cost (heuristic: estimated distance from the neighbor to the end)
            h_cost = abs(end_pos[0] - neighbor[0]) + abs(end_pos[1] - neighbor[1])
            
            # Calculate f_cost (total cost: g_cost + h_cost)
            f_cost = g_cost + h_cost

            # If the neighbor is not in open_nodes or if its new f_cost is lower than the existing f_cost, update it
            if neighbor not in open_nodes or (neighbor in open_nodes and open_nodes[neighbor]["f_cost"] < f_cost):
                # Add or update the neighbor in open_nodes with its parent, g_cost, h_cost, and f_cost
                open_nodes[neighbor] = {"parent": current_node, "g_cost": g_cost, "h_cost": h_cost, "f_cost": f_cost}

    # If no path is found, return an empty list
    return []



# | ----------------------------- Prim's Maze Generation Alogrithm -----------------------------|

def prim_maze_generation(boundaries):
    def get_walls(position):
        walls = set()
        x, y = position
        # Add valid walls (neighboring positions) based on boundaries
        if x > 0:
            walls.add((x - 1, y))  # North
        if x < boundaries[0] - 1:
            walls.add((x + 1, y))  # South
        if y > 0:
            walls.add((x, y - 1))  # West
        if y < boundaries[1] - 1:
            walls.add((x, y + 1))  # East
        return walls

    maze = set()  # Set to store the maze cells
    walls = set()  # Set to store the walls (frontier)
    
    # Pick a random starting position inside the grid
    initial_pos = (random.randint(0, boundaries[0] - 1), random.randint(0, boundaries[1] - 1))
    maze.add(initial_pos)
    
    # Add initial walls surrounding the starting cell
    walls.update(get_walls(initial_pos))
    
    while walls:
        # Pick a random wall from the wall list
        random_wall = random.choice(list(walls))
        
        # Find the maze cells that are neighbors to the current wall
        neighbours = get_walls(random_wall) & maze
        
        # If the wall separates a maze cell from a non-maze cell, we carve a path
        if len(neighbours) == 1:
            # Add the random wall to the maze
            maze.add(random_wall)
            
            # Find a new cell to add to the maze
            new_path = random_wall
            
            # Add the new path to the maze
            maze.add(new_path)
            
            # Add the new cell's walls to the wall list
            walls.update(get_walls(new_path))
        
        # Remove the processed wall from the walls set
        walls.discard(random_wall)
    
    return maze

# | ----------------------------- GUI Implementation -----------------------------|


# Initialize Pygame
pygame.init()

# Set up the display

grid_position = (100, 100)

width, height = 800, 600
rows, cols = 16, 24  # Number of rows and columns
cell_size = 25  # Size of each cell
window = pygame.display.set_mode((width, height))

pygame.display.set_caption("A* Pathfinding Algorithm")

# Set up font
font = pygame.font.Font(None, 50)  # None uses the default font, 74 is the font size


# Create a 2D list to keep track of cell colors (False for white, True for black)
grid = [["empty" for _ in range(cols)] for _ in range(rows)]

place = "start"
text_value = "Place Start Point"

start_pos = ()
end_pos = ()
wall_pos = []
path = []
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if mouse_x > grid_position[0] and mouse_y > grid_position[1]:
                # Calculate grid cell that was clicked
                row = (mouse_y - grid_position[1]) // cell_size
                col = (mouse_x - grid_position[0]) // cell_size
                if row < rows and col < cols:
                    if place == "start":
                        start_pos = (row, col)
                        grid[row][col] = "start"
                        place = "end"
                        text_value = "Place End Point"
                    elif place == "end" and grid[row][col] == "empty":
                        end_pos = (row, col)
                        grid[row][col] = "end"
                        text_value = "Place Walls"
                        place = "wall"
                        path = a_star(start_pos, end_pos, wall_pos, (rows, cols))
                        for pos in path:
                            grid[pos[0]][pos[1]] = "path"
                    elif place == "wall":
                        for pos in path:
                            grid[pos[0]][pos[1]] = "empty"
        
                        if grid[row][col] == "empty":
                            wall_pos.append((row, col))
                            grid[row][col] = "wall"
                        elif grid[row][col] == "wall":
                            wall_pos.remove((row, col))
                            grid[row][col] = "empty"

                        path = a_star(start_pos, end_pos, wall_pos, (rows, cols))
                        if path == []:
                            text_value = "No Path Found"
                        else:
                            for pos in path:
                                grid[pos[0]][pos[1]] = "path"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                grid = [["empty" for _ in range(cols)] for _ in range(rows)]
                place = "start"
                text_value = "Place Start Point"
                start_pos = ()
                end_pos = ()
                wall_pos = []
                path = []

            elif event.key == pygame.K_p:
                maze = prim_maze_generation((rows, cols))
                print(maze)
                grid = [["wall" for _ in range(cols)] for _ in range(rows)]
                for pos in maze:
                    grid[pos[0]][pos[1]] = "empty"
                place = "start"
                text_value = "Place Start Point"
                start_pos = ()
                end_pos = ()
                wall_pos = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in maze]
                path = []

    # Draw the grid
    window.fill((255, 255, 255))  # Fill the screen with white
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(grid_position[0] + col * cell_size, grid_position[1] + row * cell_size, cell_size, cell_size)
            if grid[row][col] == "wall":
                pygame.draw.rect(window, (0, 0, 0), rect)
            elif grid[row][col] == "start":
                pygame.draw.rect(window, (0, 255, 0), rect)
            elif grid[row][col] == "end":
                pygame.draw.rect(window, (255, 0, 0), rect)
            elif grid[row][col] == "path":
                pygame.draw.rect(window, (0, 0, 255), rect)
            else:
                pygame.draw.rect(window, (255, 255, 255), rect)  # White cell
            pygame.draw.rect(window, (0, 0, 0), rect, 1)  # Cell border


    text = pygame.font.Font(None, 50).render(text_value, True, (0, 0, 0))

    text_rect = text.get_rect()
    text_rect.center = (400, 50)

    window.blit(text, text_rect)

    text = pygame.font.Font(None, 25).render("Press 'C' to clear, Press 'P' to generate maze", True, (0, 0, 0))

    text_rect = text.get_rect()
    text_rect.center = (400, 75)

    window.blit(text, text_rect)

    pygame.display.flip()
