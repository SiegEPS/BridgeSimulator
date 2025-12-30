import unittest
import json
from app import app

class TestSimulationAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_simulation_endpoint(self):
        """
        Test /api/simulate with a simple strategy scenario.
        """
        # Scenario: South has some hand (dummy string for predeal, engine handles parsing)
        # Using a valid hand string to avoid errors
        s_hand = "AKQJ AKQJ AK AK" # 26 HCP
        
        payload = {
            "num_events": 10,
            "generator_params": {
                "predeal": {"S": s_hand},
                "smart_stack": {"N": {"shape": "balanced", "hcp": [0, 5]}}
            },
            "strategies": [
                {
                    "name": "Bid7NT", 
                    "root": {"type": "contract", "contract": "7N", "declarer": "S"}
                },
                {
                    "name": "Bid1NT", 
                    "root": {"type": "contract", "contract": "1N", "declarer": "S"}
                }
            ]
        }
        
        response = self.app.post('/api/simulate', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        
        # Verify structure
        self.assertIn('simulations_run', data)
        self.assertEqual(data['simulations_run'], 10)
        self.assertIn('stats', data)
        
        # Verify scores exist
        stats = data['stats']
        self.assertIn('Bid7NT_score', stats)
        self.assertIn('Bid1NT_score', stats)
        self.assertIn('diff_Bid7NT_minus_Bid1NT', stats)
        
        # 7NT with 26+ HCP should score much higher than 1NT
        # Just checking generated keys, logic verified in engine tests
        
if __name__ == '__main__':
    unittest.main()
