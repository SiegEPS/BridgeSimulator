from redeal.redeal import Deal

class DoubleDummySolver:
    """A solver for performing double dummy analysis on a bridge deal."""

    def __init__(self, deal: Deal):
        """
        Initializes the DoubleDummySolver with a bridge deal.

        Args:
            deal: A redeal.redeal.Deal object.
        """
        if not isinstance(deal, Deal):
            raise TypeError("Input must be a redeal.redeal.Deal object.")
        self.deal = deal

    def get_tricks(self, contract_str: str, declarer_char: str) -> int:
        """
        Gets the number of tricks that can be made for a given contract and declarer.
        The contract string should not include the declarer (e.g., "4H", "3N", "1C").

        Args:
            contract_str: The contract string (e.g., "4H", "3N").
            declarer_char: The declarer as a character ('N', 'E', 'S', 'W').

        Returns:
            The number of tricks the declarer can make.
        """
        declarer = declarer_char.upper()
        if declarer not in ['N', 'E', 'S', 'W']:
            raise ValueError("Invalid declarer. Must be one of 'N', 'E', 'S', 'W'.")
        
        contract_with_declarer = f"{contract_str}{declarer}"
        return self.deal.dd_tricks(contract_with_declarer)

    def get_score(self, contract_str: str, declarer_char: str, vulnerable: bool = False) -> int:
        """
        Gets the double dummy score for a given deal, contract, and vulnerability.
        The contract string should not include the declarer (e.g., "4H", "3N", "1C").

        Args:
            contract_str: The contract string (e.g., "4H", "3N").
            declarer_char: The declarer as a character ('N', 'E', 'S', 'W').
            vulnerable: Boolean indicating if the declaring side is vulnerable.

        Returns:
            The score for the contract.
        """
        declarer = declarer_char.upper()
        if declarer not in ['N', 'E', 'S', 'W']:
            raise ValueError("Invalid declarer. Must be one of 'N', 'E', 'S', 'W'.")
            
        contract_with_declarer = f"{contract_str}{declarer}"
        return self.deal.dd_score(contract_with_declarer, vul=vulnerable)

    def get_tricks_for_all_leads(self, strain_char: str, leader_char: str) -> dict:
        """
        Gets the number of tricks for all leads for a given strain and leader.
        
        Args:
            strain_char: The strain ('S', 'H', 'D', 'C', 'N').
            leader_char: The leader ('N', 'E', 'S', 'W').
            
        Returns:
            dict: Mapping of redeal.Card to int (number of tricks).
        """
        # redeal expects strain as 'S' or 'N', etc.
        # leader as Seat 'N', etc.
        # redeal.Deal.dd_all_tricks arguments: (strain, leader)
        # However, looking at redeal source, dd_all_tricks expects strain as Strain obj?
        # Actually dd_tricks takes "4S N". 
        # dd_all_tricks takes (strain, leader).
        # Let's check how redeal handles it. It seems to expect Strain/Seat enums or strings if flexible.
        # From source: dds.solve_all(self, strain, leader)
        # dds.solve_all calls Strain[strain] and Seat[leader]
        # So we can pass strings if dds module handles it, OR we pass enums.
        # redeal.redeal.Deal.dd_all_tricks docstring says "Compute declarer's number..."
        
        # Let's try passing strings first, as redeal often handles them.
        # If not, we might need to import Strain/Seat.
        
        # Actually re-reading redeal.py: 
        # def dd_all_tricks(self, strain, leader): return dds.solve_all(self, strain, leader)
        # dds.py: def solve_all(deal, strain, leader): ... Strain[strain], Seat[leader]
        # So dds.py expects 'strain' to be a key in Strain enum? No, likely Strain[strain] does lookup.
        # redeal.redeal.Deal.dd_all_tricks returns a dictionary of {Card: int}.
        # However, checking the implementation in dds.py, solve_all returns raw scores, while solve returns (13 - score).
        # This implies dd_all_tricks returns tricks for the LEADER (Defense), not Declarer.
        # We want to return Declarer's tricks to be consistent.
        
        raw_results = self.deal.dd_all_tricks(strain_char, leader_char)
        
        # Invert scores: Declarer Tricks = 13 - Defense Tricks
        return {card: 13 - tricks for card, tricks in raw_results.items()}

    def get_par(self, dealer_char: str, nsvul: bool, ewvul: bool) -> list:
        """
        Gets the double dummy par for the deal.
        
        Args:
            dealer_char: Dealer ('N', 'E', 'S', 'W').
            nsvul: Boolean, True if NS vulnerable.
            ewvul: Boolean, True if EW vulnerable.
            
        Returns:
            list: List of ScoredContract objects representing the par.
        """
        return self.deal.par(dealer_char, nsvul, ewvul)

    @staticmethod
    def solve(hands: dict, contract_str: str, declarer_char: str) -> int:
        """
        Static method to solve a deal provided in dictionary format (API format).
        
        Args:
            hands: Dictionary of hands { 'N': {'S': [...], ...}, ... }
            contract_str: Contract string (e.g., "4S", "3NT")
            declarer_char: Declarer ('N', 'E', 'S', 'W')
            
        Returns:
            int: Number of tricks
        """
        # Convert dictionary to redeal.redeal.Hand objects
        from redeal.redeal import Hand
        
        predeal_dict = {}
        for player, suits in hands.items():
            # Reconstruct hand string "S H D C"
            # Suits from dict might be lists of ranks
            # redeal expects space-separated suits usually, but Hand.from_str parses standard string
            # Let's construct standard string "AK... ... ... ..."
            
            # Ensure order Spades, Hearts, Diamonds, Clubs
            s_cards = "".join(sorted(suits.get('S', []), key=lambda r: "AKQJT98765432".index(r) if r in "AKQJT98765432" else 99))
            h_cards = "".join(sorted(suits.get('H', []), key=lambda r: "AKQJT98765432".index(r) if r in "AKQJT98765432" else 99))
            d_cards = "".join(sorted(suits.get('D', []), key=lambda r: "AKQJT98765432".index(r) if r in "AKQJT98765432" else 99))
            c_cards = "".join(sorted(suits.get('C', []), key=lambda r: "AKQJT98765432".index(r) if r in "AKQJT98765432" else 99))
            
            # Hand.from_str expects "S H D C" (space separated)
            # If a suit is empty, it uses "-"
            s_cards = s_cards if s_cards else "-"
            h_cards = h_cards if h_cards else "-"
            d_cards = d_cards if d_cards else "-"
            c_cards = c_cards if c_cards else "-"
            
            hand_str = f"{s_cards} {h_cards} {d_cards} {c_cards}"
            predeal_dict[player] = Hand.from_str(hand_str)
            
        # Create Deal
        dealer = Deal.prepare(predeal_dict)
        deal = dealer()
        
        # Solve
        solver = DoubleDummySolver(deal)
        return solver.get_tricks(contract_str, declarer_char)
