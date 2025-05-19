import redeal
from typing import Dict, List, Tuple

# Define the suits in order of importance (from highest to lowest)
SUITS = ['♠', '♥', '♦', '♣']

# Define the ranks in order of importance (from highest to lowest)
RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

class BridgeHandGenerator:
    def __init__(self):
        self.deal = None

    def generate_hand(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Generate a new bridge hand using redeal's simulation capabilities.
        
        Returns:
            Dict: A dictionary containing the cards for each player, organized by suit.
        """
        # Create a predeal dictionary with empty hands
        predeal = {player: "- - - -" for player in ['N', 'E', 'S', 'W']}
        
        # Prepare the dealer with the predeal
        dealer = redeal.Deal.prepare(predeal)
        
        # Create a deal with the prepared dealer
        deal = dealer()  # Call the partial function to create the deal
        
        # Define an accept function that accepts any valid deal
        def accept(d):
            return True  # Accept any valid deal
        
        # Add the accept function to the deal
        deal.accept = accept
        
        # Store the deal
        self.deal = deal
        
        return self._format_hand()

    def _format_hand(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Format the generated deal into a more user-friendly structure.

        Returns:
            Dict: A dictionary containing the cards for each player, organized by suit.
        """
        # Map players to their index in the deal tuple
        player_map = {
            'N': 0,  # North
            'E': 1,  # East
            'S': 2,  # South
            'W': 3   # West
        }
        
        formatted_hand = {}
        players = ['N', 'E', 'S', 'W']
        
        for player in players:
            formatted_hand[player] = {}
            for suit in SUITS:
                formatted_hand[player][suit] = []
            
            # Get the player's hand using index
            player_hand = self.deal[player_map[player]]
            
            # Map redeal's suit symbols to our symbols
            suit_map = {
                'S': '♠',
                'H': '♥',
                'D': '♦',
                'C': '♣'
            }
            
            # Add cards to their respective suits
            for suit_idx, holding in enumerate(player_hand):
                suit = SUITS[suit_idx]
                for rank in holding:
                    formatted_hand[player][suit].append(rank.name)
            
            # Sort cards within each suit by rank
            for suit in SUITS:
                formatted_hand[player][suit].sort(
                    key=lambda x: RANKS.index(x),
                    reverse=True
                )
        
        return formatted_hand

    def get_hand_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get a summary of each player's hand showing the number of cards in each suit.

        Returns:
            Dict: A dictionary containing the number of cards in each suit for each player.
        """
        summary = {}
        players = ['N', 'E', 'S', 'W']
        
        for player in players:
            summary[player] = {}
            for suit in SUITS:
                summary[player][suit] = len(self._format_hand()[player][suit])
        
        return summary
