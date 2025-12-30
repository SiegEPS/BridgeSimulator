import unittest
from bridge_simulator.simulator import SimulationRunner
from bridge_simulator.double_dummy import DoubleDummySolver
from redeal.redeal import Deal, Hand

class TestSimulationRunner(unittest.TestCase):
    def test_simulation_run(self):
        """
        Verify that the simulation runner correctly aggregates results.
        """
        runner = SimulationRunner()
        
        # Scenario:
        # Generate South hand with specific shape (balanced)
        # Calculate tricks for 1NT (South) and 2NT (South)
        
        # Callback function
        def callback(deal, solver):
            # Calculate tricks for 1NT by South
            tricks_1nt = solver.get_tricks("1N", "S")
            tricks_2nt = solver.get_tricks("2N", "S")
            return {
                'tricks_1nt': tricks_1nt,
                'tricks_2nt': tricks_2nt,
                'diff': tricks_2nt - tricks_1nt # Should trigger numeric stats, usually 0 difference in tricks taken
            }
            
        generator_params = {
            'smart_stack': {'S': {'shape': 'balanced', 'hcp': (12, 14)}}
        }
        
        # Run 10 simulations
        result = runner.run(callback, num_simulations=10, generator_params=generator_params)
        
        # Verify structure
        self.assertEqual(result['simulations_run'], 10)
        self.assertIn('tricks_1nt', result['stats'])
        self.assertIn('tricks_2nt', result['stats'])
        self.assertIn('diff', result['stats'])
        
        # Verify stats content
        self.assertIn('mean', result['stats']['tricks_1nt'])
        self.assertIn('stdev', result['stats']['tricks_1nt'])
        
        # Verify logic (tricks in 2NT should equal tricks in 1NT for the same hand/strain generally)
        # Note: double dummy tricks are just "max tricks available in strain". 
        # So 1NT vs 2NT is same strain (NT), same declarer (S). Tricks MUST be equal.
        # But score would be different.
        
        min_diff = result['stats']['diff']['min']
        max_diff = result['stats']['diff']['max']
        self.assertEqual(min_diff, 0)
        self.assertEqual(max_diff, 0)

if __name__ == '__main__':
    unittest.main()
