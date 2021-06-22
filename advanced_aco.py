import numpy as np
import random
import math
from typing import List, Tuple, Dict, Optional, Callable
from enum import Enum

class ACOVariant(Enum):
    """Different ACO algorithm variants."""
    AS = "Ant System"
    ACS = "Ant Colony System"
    MMAS = "Max-Min Ant System"
    RANK = "Rank-based Ant System"

class AdvancedACO:
    """
    Advanced Ant Colony Optimization with multiple variants:
    - Ant Colony System (ACS) with pseudo-random proportional rule
    - Max-Min Ant System (MMAS) with pheromone bounds
    - Rank-based Ant System with weighted pheromone deposits
    - 2-opt local search optimization
    """

    def __init__(self,
                 cities: np.ndarray,
                 variant: ACOVariant = ACOVariant.MMAS,
                 n_ants: int = 20,
                 n_iterations: int = 100,
                 alpha: float = 1.0,
                 beta: float = 3.0,
                 evaporation_rate: float = 0.1,
                 q0: float = 0.9,  # ACS exploitation parameter
                 tau_min: Optional[float] = None,  # MMAS min pheromone
                 tau_max: Optional[float] = None,  # MMAS max pheromone
                 elite_weight: float = 6.0,  # Rank-based elite weight
                 n_elite: int = 5,  # Number of elite ants
                 local_search: bool = True,
                 seed: Optional[int] = None,
                 callback: Optional[Callable] = None):
        """
        Initialize Advanced ACO algorithm.

        Parameters:
        -----------
        cities : np.ndarray
            Array of city coordinates (n_cities x 2)
        variant : ACOVariant
            Algorithm variant to use (AS, ACS, MMAS, RANK)
        n_ants : int
            Number of ants in the colony
        n_iterations : int
            Number of iterations to run
        alpha : float
            Pheromone importance factor
        beta : float
            Distance importance factor
        evaporation_rate : float
            Rate at which pheromones evaporate (0-1)
        q0 : float
            ACS exploitation parameter (0-1)
        tau_min : float
            MMAS minimum pheromone bound
        tau_max : float
            MMAS maximum pheromone bound
        elite_weight : float
            Weight for best solution in rank-based system
        n_elite : int
            Number of elite ants to use for pheromone update
        local_search : bool
            Whether to apply 2-opt local search
        seed : int
            Random seed for reproducibility
        callback : Callable
            Callback function called after each iteration
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.cities = cities
        self.n_cities = len(cities)
        self.variant = variant
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q0 = q0
        self.elite_weight = elite_weight
        self.n_elite = n_elite
        self.local_search = local_search
        self.callback = callback

        # Calculate distance matrix
        self.distances = self._calculate_distances()

        # Initialize pheromone matrix
        # Use a small initial value for better exploration
        initial_pheromone = 1.0 / (self.n_cities * self._nearest_neighbor_heuristic())
        self.pheromones = np.ones((self.n_cities, self.n_cities)) * initial_pheromone

        # MMAS pheromone bounds
        if self.variant == ACOVariant.MMAS:
            if tau_max is None:
                tau_max = 1.0 / (evaporation_rate * self._nearest_neighbor_heuristic())
            if tau_min is None:
                tau_min = tau_max / (2 * self.n_cities)
            self.tau_min = tau_min
            self.tau_max = tau_max
        else:
            self.tau_min = tau_min
            self.tau_max = tau_max

        # Best solution tracking
        self.best_path = None
        self.best_distance = float('inf')
        self.iteration_best_path = None
        self.iteration_best_distance = float('inf')
        self.history = []
        self.current_iteration = 0

        # Statistics
        self.pheromone_history = []

    def _calculate_distances(self) -> np.ndarray:
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

    def _nearest_neighbor_heuristic(self) -> float:
        """Get approximate tour length using nearest neighbor heuristic."""
        unvisited = set(range(1, self.n_cities))
        current = 0
        distance = 0

        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distances[current, x])
            distance += self.distances[current, nearest]
            current = nearest
            unvisited.remove(nearest)

        distance += self.distances[current, 0]
        return distance

    def _calculate_path_distance(self, path: List[int]) -> float:
        """Calculate total distance of a path."""
        distance = 0
        for i in range(len(path) - 1):
            distance += self.distances[path[i], path[i + 1]]
        distance += self.distances[path[-1], path[0]]
        return distance

    def _two_opt(self, path: List[int]) -> List[int]:
        """
        Apply 2-opt local search to improve a path.

        2-opt removes two edges and reconnects the path in a different way
        to eliminate crossing edges and reduce tour length.
        """
        improved = True
        best_path = path[:]
        best_distance = self._calculate_path_distance(best_path)

        while improved:
            improved = False
            for i in range(1, len(path) - 1):
                for j in range(i + 1, len(path)):
                    # Create new path by reversing the segment between i and j
                    new_path = best_path[:i] + best_path[i:j+1][::-1] + best_path[j+1:]
                    new_distance = self._calculate_path_distance(new_path)

                    if new_distance < best_distance:
                        best_path = new_path
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break

        return best_path

    def _select_next_city_as(self, current_city: int, unvisited: List[int]) -> int:
        """
        Standard Ant System probabilistic selection.
        """
        pheromone = np.array([self.pheromones[current_city, city] for city in unvisited])
        heuristic = np.array([1.0 / self.distances[current_city, city]
                             if self.distances[current_city, city] > 0 else 0
                             for city in unvisited])

        pheromone_factor = np.power(pheromone, self.alpha)
        heuristic_factor = np.power(heuristic, self.beta)

        probabilities = pheromone_factor * heuristic_factor
        probabilities = probabilities / probabilities.sum()

        next_city_idx = np.random.choice(len(unvisited), p=probabilities)
        return unvisited[next_city_idx]

    def _select_next_city_acs(self, current_city: int, unvisited: List[int]) -> int:
        """
        ACS pseudo-random proportional rule.
        With probability q0, exploit best option; otherwise explore.
        """
        if np.random.random() < self.q0:
            # Exploitation: choose best option
            pheromone = np.array([self.pheromones[current_city, city] for city in unvisited])
            heuristic = np.array([1.0 / self.distances[current_city, city]
                                 if self.distances[current_city, city] > 0 else 0
                                 for city in unvisited])

            values = np.power(pheromone, self.alpha) * np.power(heuristic, self.beta)
            best_idx = np.argmax(values)
            return unvisited[best_idx]
        else:
            # Exploration: use probabilistic rule
            return self._select_next_city_as(current_city, unvisited)

    def _local_pheromone_update_acs(self, city_i: int, city_j: int):
        """
        ACS local pheromone update during tour construction.
        """
        tau0 = 1.0 / (self.n_cities * self._nearest_neighbor_heuristic())
        self.pheromones[city_i, city_j] = (1 - self.evaporation_rate) * self.pheromones[city_i, city_j] + \
                                           self.evaporation_rate * tau0
        self.pheromones[city_j, city_i] = self.pheromones[city_i, city_j]

    def _construct_solution(self, ant_id: int = 0) -> List[int]:
        """Construct a solution for one ant."""
        start_city = random.randint(0, self.n_cities - 1)
        path = [start_city]
        unvisited = list(range(self.n_cities))
        unvisited.remove(start_city)

        while unvisited:
            current_city = path[-1]

            # Select next city based on variant
            if self.variant == ACOVariant.ACS:
                next_city = self._select_next_city_acs(current_city, unvisited)
                # ACS local pheromone update
                self._local_pheromone_update_acs(current_city, next_city)
            else:
                next_city = self._select_next_city_as(current_city, unvisited)

            path.append(next_city)
            unvisited.remove(next_city)

        # Apply 2-opt local search
        if self.local_search:
            path = self._two_opt(path)

        return path

    def _update_pheromones_as(self, all_paths: List[List[int]], all_distances: List[float]):
        """Standard Ant System pheromone update."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation_rate)

        # Add new pheromones from all ants
        for path, distance in zip(all_paths, all_distances):
            pheromone_amount = 1.0 / distance
            for i in range(len(path) - 1):
                self.pheromones[path[i], path[i + 1]] += pheromone_amount
                self.pheromones[path[i + 1], path[i]] += pheromone_amount
            self.pheromones[path[-1], path[0]] += pheromone_amount
            self.pheromones[path[0], path[-1]] += pheromone_amount

    def _update_pheromones_acs(self, all_paths: List[List[int]], all_distances: List[float]):
        """ACS pheromone update - only best ant deposits pheromones."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation_rate)

        # Only best ant deposits pheromones
        path = self.best_path
        distance = self.best_distance
        pheromone_amount = 1.0 / distance

        for i in range(len(path) - 1):
            self.pheromones[path[i], path[i + 1]] += self.evaporation_rate * pheromone_amount
            self.pheromones[path[i + 1], path[i]] += self.evaporation_rate * pheromone_amount
        self.pheromones[path[-1], path[0]] += self.evaporation_rate * pheromone_amount
        self.pheromones[path[0], path[-1]] += self.evaporation_rate * pheromone_amount

    def _update_pheromones_mmas(self, all_paths: List[List[int]], all_distances: List[float]):
        """MMAS pheromone update with bounds."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation_rate)

        # Only iteration-best or global-best ant deposits pheromones
        # Use iteration-best for first half, global-best for second half
        if self.current_iteration < self.n_iterations // 2:
            path = self.iteration_best_path
            distance = self.iteration_best_distance
        else:
            path = self.best_path
            distance = self.best_distance

        pheromone_amount = 1.0 / distance

        for i in range(len(path) - 1):
            self.pheromones[path[i], path[i + 1]] += pheromone_amount
            self.pheromones[path[i + 1], path[i]] += pheromone_amount
        self.pheromones[path[-1], path[0]] += pheromone_amount
        self.pheromones[path[0], path[-1]] += pheromone_amount

        # Apply bounds
        self.pheromones = np.clip(self.pheromones, self.tau_min, self.tau_max)

    def _update_pheromones_rank(self, all_paths: List[List[int]], all_distances: List[float]):
        """Rank-based pheromone update."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation_rate)

        # Sort ants by distance (best first)
        ranked_indices = np.argsort(all_distances)

        # Elite ants deposit pheromones with decreasing weights
        for rank, idx in enumerate(ranked_indices[:self.n_elite]):
            path = all_paths[idx]
            distance = all_distances[idx]
            weight = self.n_elite - rank
            pheromone_amount = weight / distance

            for i in range(len(path) - 1):
                self.pheromones[path[i], path[i + 1]] += pheromone_amount
                self.pheromones[path[i + 1], path[i]] += pheromone_amount
            self.pheromones[path[-1], path[0]] += pheromone_amount
            self.pheromones[path[0], path[-1]] += pheromone_amount

        # Best-so-far solution gets extra weight
        path = self.best_path
        distance = self.best_distance
        pheromone_amount = self.elite_weight / distance

        for i in range(len(path) - 1):
            self.pheromones[path[i], path[i + 1]] += pheromone_amount
            self.pheromones[path[i + 1], path[i]] += pheromone_amount
        self.pheromones[path[-1], path[0]] += pheromone_amount
        self.pheromones[path[0], path[-1]] += pheromone_amount

    def _update_pheromones(self, all_paths: List[List[int]], all_distances: List[float]):
        """Update pheromones based on selected variant."""
        if self.variant == ACOVariant.AS:
            self._update_pheromones_as(all_paths, all_distances)
        elif self.variant == ACOVariant.ACS:
            self._update_pheromones_acs(all_paths, all_distances)
        elif self.variant == ACOVariant.MMAS:
            self._update_pheromones_mmas(all_paths, all_distances)
        elif self.variant == ACOVariant.RANK:
            self._update_pheromones_rank(all_paths, all_distances)

    def solve(self, verbose: bool = True) -> Tuple[List[int], float]:
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
            self.current_iteration = iteration

            # Construct solutions for all ants
            all_paths = []
            all_distances = []

            # Reset iteration best
            self.iteration_best_distance = float('inf')
            self.iteration_best_path = None

            for ant in range(self.n_ants):
                path = self._construct_solution(ant)
                distance = self._calculate_path_distance(path)

                all_paths.append(path)
                all_distances.append(distance)

                # Update iteration best
                if distance < self.iteration_best_distance:
                    self.iteration_best_distance = distance
                    self.iteration_best_path = path

                # Update global best
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path

            # Update pheromones
            self._update_pheromones(all_paths, all_distances)

            # Track progress
            avg_distance = np.mean(all_distances)
            min_pheromone = np.min(self.pheromones[self.pheromones > 0])
            max_pheromone = np.max(self.pheromones)

            iteration_data = {
                'iteration': iteration,
                'best_distance': self.best_distance,
                'iteration_best': self.iteration_best_distance,
                'avg_distance': avg_distance,
                'min_pheromone': min_pheromone,
                'max_pheromone': max_pheromone,
                'best_path': self.best_path.copy() if self.best_path else None
            }
            self.history.append(iteration_data)

            if verbose and (iteration % 10 == 0 or iteration == self.n_iterations - 1):
                print(f"Iteration {iteration}: Best = {self.best_distance:.2f}, "
                      f"Iter Best = {self.iteration_best_distance:.2f}, "
                      f"Avg = {avg_distance:.2f}")

            # Call callback if provided
            if self.callback:
                self.callback(iteration_data)

        return self.best_path, self.best_distance

    def get_statistics(self) -> Dict:
        """Get algorithm statistics."""
        return {
            'variant': self.variant.value,
            'best_distance': self.best_distance,
            'best_path': self.best_path,
            'n_cities': self.n_cities,
            'n_ants': self.n_ants,
            'n_iterations': self.n_iterations,
            'alpha': self.alpha,
            'beta': self.beta,
            'evaporation_rate': self.evaporation_rate,
            'history': self.history
        }


def generate_random_cities(n_cities: int = 20, width: float = 100,
                          height: float = 100, seed: Optional[int] = None) -> np.ndarray:
    """Generate random city coordinates."""
    if seed is not None:
        np.random.seed(seed)

    cities = np.random.rand(n_cities, 2) * [width, height]
    return cities


def compare_variants(cities: np.ndarray, n_iterations: int = 100):
    """Compare different ACO variants on the same problem."""
    variants = [ACOVariant.AS, ACOVariant.ACS, ACOVariant.MMAS, ACOVariant.RANK]
    results = {}

    print("=" * 80)
    print("COMPARING ACO VARIANTS")
    print("=" * 80)

    for variant in variants:
        print(f"\nRunning {variant.value}...")
        print("-" * 80)

        aco = AdvancedACO(
            cities=cities,
            variant=variant,
            n_ants=30,
            n_iterations=n_iterations,
            alpha=1.0,
            beta=3.0,
            evaporation_rate=0.1,
            q0=0.9,
            local_search=True,
            seed=42
        )

        best_path, best_distance = aco.solve(verbose=False)

        results[variant.value] = {
            'best_distance': best_distance,
            'best_path': best_path,
            'aco': aco
        }

        print(f"Best distance: {best_distance:.2f}")

    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)

    sorted_results = sorted(results.items(), key=lambda x: x[1]['best_distance'])
    for rank, (variant_name, data) in enumerate(sorted_results, 1):
        print(f"{rank}. {variant_name}: {data['best_distance']:.2f}")

    return results


if __name__ == "__main__":
    # Generate test problem
    cities = generate_random_cities(n_cities=25, seed=42)

    # Compare variants
    results = compare_variants(cities, n_iterations=100)
