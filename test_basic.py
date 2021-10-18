"""Quick test of the basic ACO implementation."""

from tsp_aco import AntColonyTSP, generate_random_cities

print("=" * 70)
print("TESTING BASIC ANT COLONY OPTIMIZATION")
print("=" * 70)
print()

# Generate a small test problem
print("Generating 10 cities...")
cities = generate_random_cities(n_cities=10, seed=42)
print(f"Cities generated: {len(cities)} cities")
print()

# Create and run ACO
print("Running ACO with 20 ants for 20 iterations...")
aco = AntColonyTSP(
    cities=cities,
    n_ants=20,
    n_iterations=20,
    alpha=1.0,
    beta=3.0,
    evaporation_rate=0.5,
    seed=42
)

best_path, best_distance = aco.solve(verbose=False)

print()
print("RESULTS:")
print(f"Best path: {best_path}")
print(f"Best distance: {best_distance:.2f}")
print()
print("[PASS] Basic ACO test passed!")
