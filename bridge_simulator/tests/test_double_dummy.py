import unittest
from redeal.redeal import Deal, Hand
from bridge_simulator.double_dummy import DoubleDummySolver

class TestDoubleDummySolver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Deal where each player has all 13 cards of one suit.
        # N: All Spades, S: All Hearts, E: All Diamonds, W: All Clubs
        predeal_dict = {
            'N': Hand.from_str("AKQJT98765432 - - -"),
            'S': Hand.from_str("- AKQJT98765432 - -"),
            'E': Hand.from_str("- - AKQJT98765432 -"),
            'W': Hand.from_str("- - - AKQJT98765432")
        }
        cls.dealer = Deal.prepare(predeal_dict)
        cls.deal = cls.dealer()
        cls.solver = DoubleDummySolver(cls.deal)

    def test_initialization(self):
        """Test successful initialization and error handling for invalid input."""
        self.assertIsNotNone(self.solver)
        self.assertIsInstance(self.solver.deal, Deal)

        with self.assertRaises(TypeError):
            DoubleDummySolver("not a deal object")

    def test_get_tricks_valid(self):
        """Test get_tricks with valid contracts and declarers."""
        # North has all Spades
        self.assertEqual(self.solver.get_tricks("7N", 'N'), 0) # North has only spades, 0 tricks in NT
        self.assertEqual(self.solver.get_tricks("7S", 'N'), 13) # North has all spades, 13 tricks in Spades
        self.assertEqual(self.solver.get_tricks("1S", 'N'), 13)
        self.assertEqual(self.solver.get_tricks("4H", 'N'), 13) # No hearts, DDS might use longest suit (Spades)

        # South has all Hearts
        self.assertEqual(self.solver.get_tricks("7H", 'S'), 13)
        self.assertEqual(self.solver.get_tricks("1D", 'S'), 0) # No diamonds

        # East has all Diamonds
        self.assertEqual(self.solver.get_tricks("6D", 'E'), 13) # East has all Diamonds

        # West has all Clubs
        self.assertEqual(self.solver.get_tricks("3C", 'W'), 13) # West has all Clubs

    def test_get_tricks_invalid_declarer(self):
        """Test get_tricks with an invalid declarer."""
        with self.assertRaises(ValueError):
            self.solver.get_tricks("4H", 'X')

    def test_get_score_valid_non_vulnerable(self):
        """Test get_score with valid contracts, non-vulnerable."""
        # North makes 7S (13 tricks), non-vulnerable
        # Score for 7S making 7: 30*7 (tricks) + 500 (game) + 500 (grand slam) = 210 + 500 + 500 = 1210 (redeal: 1440)
        # redeal score for 7S by N, non-vul: 1440
        self.assertEqual(self.solver.get_score("7S", 'N', vulnerable=False), 1510) # 7S making 7 non-vul (210 + 300 game + 1000 grand)

        # West makes 1C (13 tricks), non-vulnerable (1C+6)
        # Score for 1C by W making 13 tricks (1C+6), non-vul: 20 + 6*20 + 300 (game) = 440
        self.assertEqual(self.solver.get_score("1C", 'W', vulnerable=False), 190) # 1C+6 non-vul (20 contract + 120 OT + 50 partscore bonus)

        # East plays 4H (0 tricks), non-vulnerable, so down 10 (contract is 4H, needs 10 tricks)
        # Score for 4H by E, down 10, non-vul: -50 * 10 = -500
        self.assertEqual(self.solver.get_score("4H", 'E', vulnerable=False), -500)

    def test_get_score_valid_vulnerable(self):
        """Test get_score with valid contracts, vulnerable."""
        # South makes 7H (13 tricks), vulnerable
        # redeal score for 7H by S, vul: 2210
        self.assertEqual(self.solver.get_score("7H", 'S', vulnerable=True), 2210)

        # East plays 4S (0 tricks), vulnerable, so down 10
        # Score for 4S by E, down 10, vul: -100 * 10 = -1000
        self.assertEqual(self.solver.get_score("4S", 'E', vulnerable=True), -1000)

    def test_get_score_invalid_declarer(self):
        """Test get_score with an invalid declarer."""
        with self.assertRaises(ValueError):
            self.solver.get_score("4H", 'X', vulnerable=False)

    def test_solve_from_dictionary(self):
        """Test the ability to solve a deal provided as a dictionary (API format)."""
        # Dictionary format matching what hand_generator returns
        # N has all Spades, S has all Hearts, E Diamonds, W Clubs
        hand_dict = {
            'N': {'S': ['A','K','Q','J','T','9','8','7','6','5','4','3','2'], 'H': [], 'D': [], 'C': []},
            'S': {'S': [], 'H': ['A','K','Q','J','T','9','8','7','6','5','4','3','2'], 'D': [], 'C': []},
            'E': {'S': [], 'H': [], 'D': ['A','K','Q','J','T','9','8','7','6','5','4','3','2'], 'C': []},
            'W': {'S': [], 'H': [], 'D': [], 'C': ['A','K','Q','J','T','9','8','7','6','5','4','3','2']}
        }
        
        # Use the static method provided by the plan (or expected implementation)
        # Verify 7S by North makes 13 tricks
        tricks = DoubleDummySolver.solve(hand_dict, "7S", "N")
        self.assertEqual(tricks, 13)

if __name__ == '__main__':
    unittest.main()
