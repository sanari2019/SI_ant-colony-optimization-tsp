"""Test all advanced ACO variants."""

from advanced_aco import AdvancedACO, ACOVariant, generate_random_cities, compare_variants
import numpy as np

print("=" * 70)
print("TESTING ADVANCED ANT COLONY OPTIMIZATION")
print("=" * 70)
print()

# Generate test problem
print("Generating 15 cities...")
cities = generate_random_cities(n_cities=15, seed=42)
print(f"Cities generated: {len(cities)} cities")
print()

# Test each variant
variants = [
    (ACOVariant.AS, "Ant System (AS)"),
    (ACOVariant.ACS, "Ant Colony System (ACS)"),
    (ACOVariant.MMAS, "Max-Min Ant System (MMAS)"),
    (ACOVariant.RANK, "Rank-based Ant System")
]

results = {}

for variant, name in variants:
    print(f"\nTesting {name}...")
    print("-" * 70)

    aco = AdvancedACO(
        cities=cities,
        variant=variant,
        n_ants=20,
        n_iterations=30,
        alpha=1.0,
        beta=3.0,
        evaporation_rate=0.1,
        local_search=True,
        seed=42
    )

    best_path, best_distance = aco.solve(verbose=False)
    results[name] = best_distance

    print(f"Best distance: {best_distance:.2f}")
    print(f"Path length: {len(best_path)} cities")
    print(f"[PASS] {name} completed successfully")

print()
print("=" * 70)
print("COMPARISON RESULTS")
print("=" * 70)

sorted_results = sorted(results.items(), key=lambda x: x[1])
for rank, (variant_name, distance) in enumerate(sorted_results, 1):
    print(f"{rank}. {variant_name}: {distance:.2f}")

print()
print("[PASS] All advanced ACO variants tested successfully!")
