from flask import Flask, request, jsonify
from bridge_simulator.hand_generator import BridgeHandGenerator

app = Flask(__name__)
generator = BridgeHandGenerator()

@app.route('/api/generate-hands')
def generate_hands():
    """Generate bridge hands with optional constraints."""
    # Get query parameters
    num_hands = int(request.args.get('num_hands', 1))
    
    # Parse constraints
    constraints = {}
    
    # HCP constraints
    hcp_str = request.args.get('hcp')
    if hcp_str:
        constraints['hcp'] = {}
        try:
            for player_str in hcp_str.split(','):  # Format: N:12-14,E:15-17
                if ':' not in player_str:
                    continue
                player, range_str = player_str.split(':')
                min_hcp, max_hcp = map(int, range_str.split('-'))
                constraints['hcp'][player] = (min_hcp, max_hcp)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid HCP format. Expected format: N:12-14,E:15-17"}), 400
    
    # Suit holding constraints
    suit_holding_str = request.args.get('suit_holding')
    if suit_holding_str:
        constraints['suit_holding'] = {}
        try:
            for player_str in suit_holding_str.split(','):  # Format: N:S6,H5,E:D7
                if ':' not in player_str:
                    continue
                player, suit_str = player_str.split(':')
                constraints['suit_holding'][player] = {}
                for suit_str in suit_str.split(','):  # Format: S6,H5
                    if len(suit_str) < 2:
                        continue
                    suit, length = suit_str[0], int(suit_str[1:])
                    constraints['suit_holding'][player][suit] = length
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid suit holding format. Expected format: N:S6,H5,E:D7"}), 400
    
    # Hand shape constraints
    shape_str = request.args.get('hand_shape')
    if shape_str:
        constraints['hand_shape'] = {}
        try:
            for player_str in shape_str.split(','):  # Format: N:5332,S:4432
                if ':' not in player_str:
                    continue
                player, shape = player_str.split(':')
                constraints['hand_shape'][player] = list(map(int, shape))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid hand shape format. Expected format: N:5332,S:4432"}), 400
    
    # Controls constraints
    controls_str = request.args.get('controls')
    if controls_str:
        constraints['controls'] = {}
        try:
            for player_str in controls_str.split(','):  # Format: N:6-8,E:4-6
                if ':' not in player_str:
                    continue
                player, range_str = player_str.split(':')
                min_controls, max_controls = map(int, range_str.split('-'))
                constraints['controls'][player] = (min_controls, max_controls)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid controls format. Expected format: N:6-8,E:4-6"}), 400
    
    # Generate hands with constraints
    hands = generator.generate_hands(num_hands=num_hands, **constraints)
    return jsonify(hands)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
