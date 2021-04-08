import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import math

class AntColonyTSP:
    """
    Ant Colony Optimization for solving the Traveling Salesman Problem.
    
    The algorithm simulates ant behavior where ants:
    1. Choose paths probabilistically based on pheromone trails and distance
    2. Deposit pheromones on paths they traverse
    3. Pheromones evaporate over time
    4. Shorter paths accumulate more pheromones due to faster ant cycles
    """
    
    def __init__(self, cities, n_ants=20, n_iterations=100, alpha=1.0, beta=2.0, 
                 evaporation_rate=0.5, pheromone_deposit=1.0, seed=None):
        """
        Initialize ACO algorithm.
        
        Parameters:
        -----------
        cities : np.ndarray
            Array of city coordinates (n_cities x 2)
        n_ants : int
            Number of ants in the colony
        n_iterations : int
            Number of iterations to run
        alpha : float
            Pheromone importance factor (higher = more influenced by pheromones)
        beta : float
            Distance importance factor (higher = more influenced by short distances)
        evaporation_rate : float
            Rate at which pheromones evaporate (0-1)
        pheromone_deposit : float
            Amount of pheromone deposited by ants
        seed : int
            Random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        self.cities = cities
        self.n_cities = len(cities)
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha  # Pheromone influence
        self.beta = beta    # Distance influence
        self.evaporation_rate = evaporation_rate
        self.pheromone_deposit = pheromone_deposit
        
        # Calculate distance matrix
        self.distances = self._calculate_distances()
        
        # Initialize pheromone matrix
        self.pheromones = np.ones((self.n_cities, self.n_cities)) * 0.1
        
        # Best solution tracking
        self.best_path = None
        self.best_distance = float('inf')
        self.history = []
        
    def _calculate_distances(self):
        """Calculate Euclidean distance matrix between all cities."""
        distances = np.zeros((self.n_cities, self.n_cities))
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                if i != j:
                    distances[i, j] = np.sqrt(
                        (self.cities[i, 0] - self.cities[j, 0])**2 + 
                        (self.cities[i, 1] - self.cities[j, 1])**2
                    )
        return distances
    
    def _calculate_path_distance(self, path):
        """Calculate total distance of a path."""
        distance = 0
        for i in range(len(path) - 1):
            distance += self.distances[path[i], path[i + 1]]
        # Add distance back to start
        distance += self.distances[path[-1], path[0]]
        return distance
    
    def _select_next_city(self, current_city, unvisited):
        """
        Select next city based on pheromone levels and distances.
        Uses probabilistic decision rule combining pheromones and heuristic information.
        """
        pheromone = np.array([self.pheromones[current_city, city] for city in unvisited])
        # Heuristic: inverse of distance (closer cities are more attractive)
        heuristic = np.array([1.0 / self.distances[current_city, city] if self.distances[current_city, city] > 0 else 0 
                             for city in unvisited])
        
        # Calculate probabilities
        pheromone_factor = np.power(pheromone, self.alpha)
        heuristic_factor = np.power(heuristic, self.beta)
        
        probabilities = pheromone_factor * heuristic_factor
        probabilities = probabilities / probabilities.sum()
        
        # Select city based on probabilities
        next_city_idx = np.random.choice(len(unvisited), p=probabilities)
        return unvisited[next_city_idx]
    
    def _construct_solution(self):
        """Construct a solution for one ant."""
        # Start from a random city
        start_city = random.randint(0, self.n_cities - 1)
        path = [start_city]
        unvisited = list(range(self.n_cities))
        unvisited.remove(start_city)
        
        # Build path by selecting cities one by one
        while unvisited:
            current_city = path[-1]
            next_city = self._select_next_city(current_city, unvisited)
            path.append(next_city)
            unvisited.remove(next_city)
        
        return path
    
    def _update_pheromones(self, all_paths, all_distances):
        """Update pheromone levels based on ant solutions."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation_rate)
        
        # Add new pheromones
        for path, distance in zip(all_paths, all_distances):
            pheromone_amount = self.pheromone_deposit / distance
            for i in range(len(path) - 1):
                self.pheromones[path[i], path[i + 1]] += pheromone_amount
                self.pheromones[path[i + 1], path[i]] += pheromone_amount
            # Add pheromone for return to start
            self.pheromones[path[-1], path[0]] += pheromone_amount
            self.pheromones[path[0], path[-1]] += pheromone_amount
    
    def solve(self, verbose=True):
        """
        Run the ACO algorithm to solve TSP.
        
        Returns:
        --------
        best_path : list
            Best path found
        best_distance : float
            Distance of best path
        """
        for iteration in range(self.n_iterations):
            # Construct solutions for all ants
            all_paths = []
            all_distances = []
            
            for ant in range(self.n_ants):
                path = self._construct_solution()
                distance = self._calculate_path_distance(path)
                
                all_paths.append(path)
                all_distances.append(distance)
                
                # Update best solution
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path
            
            # Update pheromones
            self._update_pheromones(all_paths, all_distances)
            
            # Track progress
            avg_distance = np.mean(all_distances)
            self.history.append({
                'iteration': iteration,
                'best_distance': self.best_distance,
                'avg_distance': avg_distance
            })
            
            if verbose and (iteration % 10 == 0 or iteration == self.n_iterations - 1):
                print(f"Iteration {iteration}: Best = {self.best_distance:.2f}, Avg = {avg_distance:.2f}")
        
        return self.best_path, self.best_distance
    
    def plot_solution(self, save_path=None):
        """Plot the best solution found."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot the tour
        if self.best_path is not None:
            path_cities = self.cities[self.best_path + [self.best_path[0]]]
            ax1.plot(path_cities[:, 0], path_cities[:, 1], 'b-', linewidth=2, alpha=0.7)
            ax1.scatter(self.cities[:, 0], self.cities[:, 1], c='red', s=100, zorder=5)
            
            # Mark start city
            start_city = self.cities[self.best_path[0]]
            ax1.scatter(start_city[0], start_city[1], c='green', s=200, 
                       marker='*', zorder=10, label='Start')
            
            # Add city numbers
            for i, (x, y) in enumerate(self.cities):
                ax1.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points')
            
            ax1.set_title(f'Best Tour (Distance: {self.best_distance:.2f})')
            ax1.set_xlabel('X Coordinate')
            ax1.set_ylabel('Y Coordinate')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Plot convergence
        if self.history:
            iterations = [h['iteration'] for h in self.history]
            best_distances = [h['best_distance'] for h in self.history]
            avg_distances = [h['avg_distance'] for h in self.history]
            
            ax2.plot(iterations, best_distances, 'g-', linewidth=2, label='Best Distance')
            ax2.plot(iterations, avg_distances, 'b--', alpha=0.7, label='Average Distance')
            ax2.set_title('Convergence Over Iterations')
            ax2.set_xlabel('Iteration')
            ax2.set_ylabel('Distance')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        return fig


def generate_random_cities(n_cities=20, width=100, height=100, seed=None):
    """Generate random city coordinates."""
    if seed is not None:
        np.random.seed(seed)
    
    cities = np.random.rand(n_cities, 2) * [width, height]
    return cities


def demo_aco_tsp():
    """Demonstration of ACO for TSP."""
    print("=" * 70)
    print("ANT COLONY OPTIMIZATION FOR TRAVELING SALESMAN PROBLEM")
    print("=" * 70)
    print()
    
    # Generate cities
    n_cities = 20
    cities = generate_random_cities(n_cities=n_cities, seed=42)
    
    print(f"Problem: {n_cities} cities")
    print(f"Total possible tours: {math.factorial(n_cities-1) // 2:,}")
    print()
    
    # Create and run ACO
    print("Running Ant Colony Optimization...")
    print("-" * 70)
    
    aco = AntColonyTSP(
        cities=cities,
        n_ants=30,
        n_iterations=100,
        alpha=1.0,      # Pheromone importance
        beta=3.0,       # Distance importance
        evaporation_rate=0.5,
        pheromone_deposit=1.0,
        seed=42
    )
    
    best_path, best_distance = aco.solve(verbose=True)
    
    print("-" * 70)
    print()
    print("RESULTS:")
    print(f"Best path found: {best_path}")
    print(f"Best distance: {best_distance:.2f}")
    print()
    
    # Plot solution
    aco.plot_solution(save_path='/mnt/user-data/outputs/tsp_aco_solution.png')
    
    return aco


if __name__ == "__main__":
    # Run demonstration
    aco = demo_aco_tsp()
    
    print("\n" + "=" * 70)
    print("PARAMETER EXPLANATION:")
    print("=" * 70)
    print("""
Alpha (α): Controls pheromone importance
  - Higher α = ants rely more on pheromone trails
  - Typical range: 0.5 - 2.0

Beta (β): Controls distance importance (heuristic)
  - Higher β = ants prefer shorter distances
  - Typical range: 2.0 - 5.0

Evaporation Rate (ρ): Rate at which pheromones evaporate
  - Higher ρ = faster exploration, less exploitation
  - Typical range: 0.1 - 0.9

Number of Ants: More ants = more exploration but slower
  - Rule of thumb: Similar to number of cities

Number of Iterations: More iterations = better solutions but slower
  - Depends on problem size and convergence
    """)
