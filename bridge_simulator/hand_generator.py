import redeal
from typing import Dict, List, Tuple
from redeal.redeal import Hand, Card, Suit, Rank, Deal

# Define the suits in order of importance (from highest to lowest)
SUITS = ['S', 'H', 'D', 'C']

# Define the ranks in order of importance (from highest to lowest)
RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

class BridgeHandGenerator:
    def __init__(self):
        self.deals = []

    def generate_hands(self, num_hands: int = 100,
                       suit_holding: Dict[str, Dict[str, int]] = None,
                       hcp: Dict[str, Tuple[int, int]] = None,
                       hand_shape: Dict[str, List[int]] = None,
                       hand_losers: Dict[str, Tuple[int, int]] = None,
                       controls: Dict[str, Tuple[int, int]] = None,
                       predeal: Dict[str, str] = None,
                       max_attempts_param: int = None
                       ) -> List[Dict[str, Dict[str, List[str]]]]:
        """
        Generate multiple bridge hands using redeal's simulation capabilities,
        with optional constraints for each hand.

        Args:
            num_hands: Number of hands to generate (default: 100).
            suit_holding: Optional. Dictionary specifying minimum suit length for a hand.
                          Example: {'N': {'S': 5}} means North must have at least 5 spades.
                          Suit characters are 'S', 'H', 'D', 'C'.
            hcp: Optional. Dictionary specifying HCP range (min, max) for a hand.
                 Example: {'N': (11, 15)} means North has 11-15 HCP.
            hand_shape: Optional. Dictionary specifying exact hand shape (lengths of S,H,D,C).
                        Example: {'N': [5,4,3,1]} for North.
            hand_losers: Optional. Dictionary specifying loser count range (min, max) for a hand.
                         Example: {'S': (6, 7)} means South has 6-7 losers.
            controls: Optional. Dictionary specifying controls range (min, max) for a hand.
                      Example: {'E': (4, 6)} means East has 4-6 controls.
            
        Returns:
            List[Dict]: List of dictionaries containing cards for each player, organized by suit.
        """
        
        # Helper to get suit attribute from hand object (e.g., deal.north.spades)
        def get_suit_attr(hand_obj, suit_char):
            if suit_char == 'S': return hand_obj.spades
            if suit_char == 'H': return hand_obj.hearts
            if suit_char == 'D': return hand_obj.diamonds
            if suit_char == 'C': return hand_obj.clubs
            return []

        def accept(deal) -> bool:
            """
            Accept a deal if it meets all the specified criteria.
            """
            # Create a dictionary of player hands
            player_hands = {
                'N': deal.north,
                'E': deal.east,
                'S': deal.south,
                'W': deal.west
            }

            # Check suit holding requirements
            if suit_holding:
                for player, suits in suit_holding.items():
                    hand = player_hands.get(player)
                    if not hand: continue
                    for suit_char, min_len in suits.items():
                        suit = {'S': Suit.S, 'H': Suit.H, 'D': Suit.D, 'C': Suit.C}[suit_char]
                        # Get cards in the suit directly
                        if len([card for card in hand.cards() if card.suit == suit]) < min_len:
                            return False

            # Check hand shape requirements
            if hand_shape:
                for player, shape in hand_shape.items():
                    hand = player_hands.get(player)
                    if not hand: continue
                    # Get the shape as a list of lengths in redeal's order (S,H,D,C)
                    actual_shape = list(hand.shape)
                    if actual_shape != shape:
                        return False

            # Check HCP requirements
            if hcp:
                for player, (min_hcp, max_hcp) in hcp.items():
                    hand = player_hands.get(player)
                    if not hand: continue
                    if not (min_hcp <= hand.hcp <= max_hcp):
                        return False

            # Check controls requirements
            if controls:
                for player, (min_controls, max_controls) in controls.items():
                    hand = player_hands.get(player)
                    if not hand: continue
                    # Use redeal's direct 'controls' property
                    if not (min_controls <= hand.controls <= max_controls):
                        return False

            # For losers checks (currently disabled)
            # if hand_losers:
            #     for player, losers_range in hand_losers.items():
            #         hand = player_hands.get(player)
            #         # Ensure _calculate_losers is accessible or use hand.losers if available
            #         # current_losers = self._calculate_losers(hand) # This would cause error if accept is nested
            #         # For now, assuming hand_losers constraint is not actively used or will be fixed later
            #         pass # Placeholder if hand_losers logic needs to be re-evaluated

            return True

        # Prepare the predeal dictionary
        predeal_dict = predeal or {player: "- - - -" for player in ['N', 'E', 'S', 'W']}
        
        # Validate predeal format
        for direction, hand_str in predeal_dict.items():
            if direction not in ['N', 'E', 'S', 'W']:
                raise ValueError(f"Invalid direction: {direction}. Must be one of N, E, S, W")
            # Validate hand string format
            suits = hand_str.split()
            if len(suits) != 4:
                raise ValueError(f"Invalid hand format for {direction}: {hand_str}. Must have 4 suits.")
            for suit in suits:
                if suit != '-' and not all(c in 'AKQJT98765432' for c in suit):
                    raise ValueError(f"Invalid cards in {direction}: {suit}. Must be valid card ranks.")
        
        # Convert predeal strings to Hand objects
        predeal_hands = {}
        for direction, hand_str in predeal_dict.items():
            predeal_hands[direction] = Hand.from_str(hand_str)
        
        dealer = Deal.prepare(predeal_hands)
        
        formatted_hands = []
        generated_count = 0
        generation_attempts = 0

        DEFAULT_MAX_ATTEMPTS_WITH_CONSTRAINTS = 20000  # Default if constraints/predeal and no param provided
        
        actual_max_attempts = max_attempts_param
        if actual_max_attempts is None:
            # Check if any significant constraints or non-empty predeals are active
            # predeal_hands is guaranteed to be a dict by prior logic
            is_predeal_effectively_empty = all(str(hand) == "- - - -" for hand in predeal_hands.values())
            has_any_constraints = bool(suit_holding or hcp or hand_shape or hand_losers or controls)

            if not has_any_constraints and is_predeal_effectively_empty:
                # If no constraints and predeal is empty, max_attempts is num_hands (or 1 if num_hands is 0 to allow loop for validation if needed)
                actual_max_attempts = num_hands if num_hands > 0 else 1
            else:
                # Constraints or significant predeal exist, use a higher default
                actual_max_attempts = DEFAULT_MAX_ATTEMPTS_WITH_CONSTRAINTS
        
        if num_hands == 0:
            return formatted_hands # Return immediately if 0 hands are requested

        while generated_count < num_hands and generation_attempts < actual_max_attempts:
            deal = dealer()  # Generate one deal using the prepared dealer
            generation_attempts += 1
            if accept(deal): # Use the accept function defined within generate_hands
                formatted_hands.append(self._format_hand(deal))
                generated_count += 1
        
        return formatted_hands

    def generate_hand(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Generate a new bridge hand using redeal's simulation capabilities.
        
        Returns:
            Dict: A dictionary containing the cards for each player, organized by suit.
        """
        # Create a predeal dictionary with empty hands
        predeal = {player: "- - - -" for player in ['N', 'E', 'S', 'W']}
        
        # Prepare the dealer with the predeal
        dealer = Deal.prepare(predeal)
        
        # Create a deal with the prepared dealer
        deal = dealer()  # Call the partial function to create the deal
        
        # Define an accept function that accepts any valid deal
        def accept(d):
            return True  # Accept any valid deal
        
        # Add the accept function to the deal
        deal.accept = accept
        
        # Store the deal
        self.deal = deal
        
        return self._format_hand(deal)

    def _calculate_controls(self, hand: Hand) -> int:
        """
        Calculate controls for a hand using redeal's Hand class.
        """
        return hand.controls

    def _calculate_losers(self, hand: Hand) -> int:
        """
        Calculate losers for a hand using redeal's Hand class.
        
        Note: This method is currently commented out due to issues with redeal's implementation.
        """
        # return round(sum(holding.newltc for holding in hand))
        return 0  # Placeholder return value

    # def _calculate_losers(self, hand: Hand) -> int:
    #     """
    #     Calculate losers for a hand using redeal's Hand class.
    #     """
    #     return round(hand.newltc)

    def _format_hand(self, deal):
        """
        Format a deal into a more user-friendly structure using redeal's built-in formatting.
        
        Args:
            deal: Deal object to format
            
        Returns:
            Dict: A dictionary containing the cards for each player, organized by suit.
        """
        formatted_hand = {}
        
        # Map our suit symbols to redeal's suit order
        suit_map = {
            'S': Suit.S,  # Spades
            'H': Suit.H,  # Hearts
            'D': Suit.D,  # Diamonds
            'C': Suit.C   # Clubs
        }
        
        # Create dictionary for each player
        for player in ['N', 'E', 'S', 'W']:
            formatted_hand[player] = {}
            
            # Get the player's hand using Deal's tuple indexing
            player_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}[player]
            hand = deal[player_idx]
            
            # Get cards for each suit
            for suit_char, suit in suit_map.items():
                # Initialize suit as empty list
                formatted_hand[player][suit_char] = []
                
                # Get cards in this suit using Hand's cards() method
                for card in hand.cards():
                    if card.suit == suit:
                        formatted_hand[player][suit_char].append(str(card.rank))
                
                # Sort cards within each suit by rank if we have any cards
                if formatted_hand[player][suit_char]:
                    formatted_hand[player][suit_char].sort(
                        key=lambda x: RANKS.index(x),
                        reverse=True
                    )
        
        return formatted_hand

    def get_hand_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get a summary of each player's hand showing the number of cards in each suit using redeal's shape property.

        Returns:
            Dict: A dictionary containing the number of cards in each suit for each player.
        """
        summary = {}
        for player in ['N', 'E', 'S', 'W']:
            # Get the player's hand using Deal's tuple indexing
            player_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}[player]
            hand = self.deal[player_idx]
            
            # Get the shape (lengths of each suit)
            shape = hand.shape
            
            # Map our suit symbols to redeal's suit order
            suit_map = {
                '♠': 0,  # Spades
                '♥': 1,  # Hearts
                '♦': 2,  # Diamonds
                '♣': 3   # Clubs
            }
            
            # Create summary using redeal's shape
            summary[player] = {}
            for suit in SUITS:
                summary[player][suit] = shape[suit_map[suit]]
        
        return summary
