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
