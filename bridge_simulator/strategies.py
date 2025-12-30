from typing import Dict, Any, Optional
from redeal.redeal import Deal, Suit

class DecisionNode:
    """
    Represents a node in the decision tree.
    Can be a 'branch' (condition) or a 'leaf' (final contract).
    """
    def __init__(self, data: Dict[str, Any]):
        self.type = data.get('type')
        self.data = data
        
        # Branch properties
        self.condition = data.get('condition')
        self.true_branch = None
        self.false_branch = None
        
        # Leaf properties
        self.contract = data.get('contract')
        self.declarer = data.get('declarer')
        
        if self.type != 'contract':
            if 'true_branch' in data:
                self.true_branch = DecisionNode(data['true_branch'])
            if 'false_branch' in data:
                self.false_branch = DecisionNode(data['false_branch'])

    def evaluate(self, deal: Deal) -> Dict[str, str]:
        """
        Recursively evaluate the tree against a deal.
        Returns {'contract': str, 'declarer': str}
        """
        if self.type == 'contract':
            return {'contract': self.contract, 'declarer': self.declarer}
        
        # Evaluate condition
        if self.check_condition(deal, self.condition):
            if self.true_branch:
                return self.true_branch.evaluate(deal)
        else:
            if self.false_branch:
                return self.false_branch.evaluate(deal)
        
        # Fallback if branch missing (shouldn't happen in valid tree)
        return {'contract': 'PASS', 'declarer': 'N'}

    def check_condition(self, deal: Deal, condition: Dict[str, Any]) -> bool:
        """
        Check a single condition against the deal.
        Supported types: 'suit_length', 'hcp'
        """
        cond_type = condition.get('type')
        
        if cond_type == 'suit_length':
            suit_char = condition.get('suit')
            operator = condition.get('operator')
            value = condition.get('value')
            
            # Assuming checking North's hand for now (System usually defined for N/S pair)
            # Todo: Make player configurable in condition? Defaulting to North (Opener)
            hand = deal.north
            
            length = 0
            if suit_char == 'S': length = len(hand.spades)
            elif suit_char == 'H': length = len(hand.hearts)
            elif suit_char == 'D': length = len(hand.diamonds)
            elif suit_char == 'C': length = len(hand.clubs)
            
            return self.compare(length, operator, value)

        elif cond_type == 'hcp':
            operator = condition.get('operator')
            value = condition.get('value')
            hand = deal.north 
            return self.compare(hand.hcp, operator, value)
            
        return False

    def compare(self, distinct_val, operator, target_val):
        if operator == '>': return distinct_val > target_val
        if operator == '>=': return distinct_val >= target_val
        if operator == '<': return distinct_val < target_val
        if operator == '<=': return distinct_val <= target_val
        if operator == '==': return distinct_val == target_val
        return False

class DecisionStrategy:
    """
    Wrapper for a full decision tree strategy.
    """
    def __init__(self, json_data: Dict[str, Any]):
        self.name = json_data.get('name', 'Unnamed Strategy')
        self.root = DecisionNode(json_data.get('root'))

    def evaluate(self, deal: Deal) -> Dict[str, str]:
        return self.root.evaluate(deal)
