from typing import Callable, Any, Dict, List
import statistics
from .hand_generator import BridgeHandGenerator
from .double_dummy import DoubleDummySolver

class SimulationRunner:
    def __init__(self):
        self.generator = BridgeHandGenerator()

    def run(self, 
            simulation_callback: Callable[[Any, DoubleDummySolver], Dict[str, Any]], 
            num_simulations: int = 100,
            generator_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a Monte Carlo simulation.

        Args:
            simulation_callback: A function that takes (deal, solver) and returns a dict of results.
                                 Example: lambda deal, solver: {'score_1nt': solver.solve(deal, '1NT', 'N')}
            num_simulations: Number of deals to simulate.
            generator_params: Dictionary of arguments to pass to BridgeHandGenerator (e.g., constraints).

        Returns:
            Dict containing aggregated statistics (mean, stdev) for numeric results, 
            and raw counts for non-numeric results.
        """
        if generator_params is None:
            generator_params = {}

        results_accumulator = {}
        
        # Use yield_deals for efficient generation
        deal_iterator = self.generator.yield_deals(num_hands=num_simulations, **generator_params)
        
        count = 0
        for deal in deal_iterator:
            solver = DoubleDummySolver(deal)
            
            # Run the user-defined callback
            # Note: DoubleDummySolver.solve is static but we instantiate it for convenient methods if needed.
            # But the static 'solve' takes dicts. The object methods work on 'deal'.
            # We pass the solver OBJECT which wraps the deal.
            
            try:
                result = simulation_callback(deal, solver)
                
                # Accumulate results
                for key, value in result.items():
                    if key not in results_accumulator:
                        results_accumulator[key] = []
                    results_accumulator[key].append(value)
                
                count += 1
            except Exception as e:
                print(f"Error in simulation iteration {count}: {e}")
                continue

        # Aggregate results
        aggregated_stats = {
            'simulations_run': count,
            'stats': {}
        }

        for key, values in results_accumulator.items():
            if not values:
                continue
                
            # Check if values are numeric
            if isinstance(values[0], (int, float)):
                mean = statistics.mean(values)
                stdev = statistics.stdev(values) if len(values) > 1 else 0.0
                aggregated_stats['stats'][key] = {
                    'mean': mean,
                    'stdev': stdev,
                    'min': min(values),
                    'max': max(values)
                }
            else:
                # Frequency count for non-numeric
                # Convert to string to be safe for counting
                counts = {}
                for v in values:
                    v_str = str(v)
                    counts[v_str] = counts.get(v_str, 0) + 1
                aggregated_stats['stats'][key] = counts

        return aggregated_stats
