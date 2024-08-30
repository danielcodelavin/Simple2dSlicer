import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys

class Cell:
    def __init__(self, x, y, fill=0):
        self.x = x
        self.y = y
        self.fill = fill

class ThermalSimulation:
    def __init__(self, grid, numrows, numcols):
        self.grid = grid
        self.numrows = numrows
        self.numcols = numcols
        self.temp_grid = np.full((numrows, numcols), 400)  # Base plate temperature
        self.k = 0.1  # Heat transfer coefficient (simplified)

    def add_cubes(self):
        for row in range(self.numrows):
            for col in range(self.numcols):
                if self.grid[row][col].fill in (1, 2):
                    self.temp_grid[row, col] = 1200  # Cube temperature

    def update_temperatures(self):
        new_temp = self.temp_grid.copy()
        for i in range(self.numrows):
            for j in range(self.numcols):
                neighbors = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.numrows and 0 <= nj < self.numcols:
                        neighbors.append(self.temp_grid[ni, nj])
                new_temp[i, j] += self.k * sum(t - self.temp_grid[i, j] for t in neighbors)
        self.temp_grid = new_temp

    def run_simulation(self, num_steps):
        self.add_cubes()
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(self.temp_grid, cmap='hot', vmin=400, vmax=1200, interpolation='nearest')
        plt.colorbar(im)

        def update(frame):
            self.update_temperatures()
            im.set_array(self.temp_grid)
            ax.set_title(f"Thermal Simulation - Step {frame}")
            return [im]

        anim = FuncAnimation(fig, update, frames=num_steps, interval=50, blit=False)
        plt.tight_layout()
        plt.show()

def run_visual_simulation():
    try:
        # Create a sample grid
        numrows, numcols = 50, 50
        grid = [[Cell(i, j) for j in range(numcols)] for i in range(numrows)]

        # Add some sample cubes
        grid[10][10].fill = 1
        grid[20][20].fill = 2
        grid[30][30].fill = 1
        grid[40][40].fill = 2

        # Print grid configuration
        print("Grid configuration:")
        for i in range(numrows):
            for j in range(numcols):
                if grid[i][j].fill != 0:
                    print(f"Cube at ({i}, {j}) with fill value {grid[i][j].fill}")

        # Run the simulation
        sim = ThermalSimulation(grid, numrows, numcols)
        print("Starting simulation...")
        sim.run_simulation(200)  # Run for 200 steps
        print("Simulation completed.")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_visual_simulation()