import unittest
from redeal.redeal import Deal, Hand
from bridge_simulator.strategies import DecisionStrategy

class TestDecisionStrategy(unittest.TestCase):
    def setUp(self):
        # Create a mock deal
        # North: 5 Spades, 2 Hearts (S AKxxx H xx ...)
        n_hand = Hand.from_str("AKJ84 53 K52 A83")
        self.deal_spades = Deal.prepare({'N': n_hand})()
        
        # North: 2 Spades, 5 Hearts (S xx H AKxxx ...)
        n_hand_hearts = Hand.from_str("53 AKJ84 K52 A83")
        self.deal_hearts = Deal.prepare({'N': n_hand_hearts})()

    def test_simple_branching(self):
        """
        Test: If Spades >= 5 Bid 2S, Else Bid 2H
        """
        strategy_json = {
            "name": "Simple Major",
            "root": {
                "type": "branch",
                "condition": {"type": "suit_length", "suit": "S", "operator": ">=", "value": 5},
                "true_branch": {"type": "contract", "contract": "2S", "declarer": "N"},
                "false_branch": {"type": "contract", "contract": "2H", "declarer": "N"}
            }
        }
        
        strategy = DecisionStrategy(strategy_json)
        
        # Test Spades Hand -> Should match True branch (2S)
        result = strategy.evaluate(self.deal_spades)
        self.assertEqual(result['contract'], '2S')
        
        # Test Hearts Hand -> Should match False branch (2H)
        result = strategy.evaluate(self.deal_hearts)
        self.assertEqual(result['contract'], '2H')

    def test_nested_branching(self):
        """
        Test: If Spades >= 5 Bid 2S. 
              Else (If Hearts >= 5 Bid 2H, Else Bid 1NT)
        """
        strategy_json = {
            "name": "Nested",
            "root": {
                "type": "branch",
                "condition": {"type": "suit_length", "suit": "S", "operator": ">=", "value": 5},
                "true_branch": {"type": "contract", "contract": "2S", "declarer": "N"},
                "false_branch": {
                    "type": "branch",
                    "condition": {"type": "suit_length", "suit": "H", "operator": ">=", "value": 5},
                    "true_branch": {"type": "contract", "contract": "2H", "declarer": "N"},
                    "false_branch": {"type": "contract", "contract": "1N", "declarer": "N"}
                }
            }
        }
        
        strategy = DecisionStrategy(strategy_json)
        
        # Spades Hand
        self.assertEqual(strategy.evaluate(self.deal_spades)['contract'], '2S')
        
        # Hearts Hand
        self.assertEqual(strategy.evaluate(self.deal_hearts)['contract'], '2H')
        
        # Balanced Hand (2 Spades, 2 Hearts)
        n_hand_bal = Hand.from_str("53 42 AKJ84 A83")
        deal_bal = Deal.prepare({'N': n_hand_bal})()
        self.assertEqual(strategy.evaluate(deal_bal)['contract'], '1N')

if __name__ == '__main__':
    unittest.main()
