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

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Run a simulation based on params and strategies.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    generator_params = data.get('generator_params', {})
    
    # Remove num_hands if present in generator_params to avoid duplicate argument error
    # because SimulationRunner.run passes num_simulations as num_hands to yield_deals
    if 'num_hands' in generator_params:
        generator_params.pop('num_hands')
    
    # Fix list to tuple for hcp
    if 'smart_stack' in generator_params:
        for p, config in generator_params['smart_stack'].items():
            if 'hcp' in config and isinstance(config['hcp'], list):
                config['hcp'] = tuple(config['hcp'])

    num_simulations = int(data.get('num_events', 100))
    strategies_json = data.get('strategies', [])
    
    from bridge_simulator.strategies import DecisionStrategy
    from bridge_simulator.simulator import SimulationRunner
    
    strategies = [DecisionStrategy(s) for s in strategies_json]
    runner = SimulationRunner()
    
    def simulation_callback(deal, solver):
        result = {}
        scores = {}
        for strategy in strategies:
            decision = strategy.evaluate(deal)
            contract = decision['contract']
            declarer = decision['declarer']
            score = solver.get_score(contract, declarer, vulnerable=False)
            result[f"{strategy.name}_contract"] = contract
            result[f"{strategy.name}_score"] = score
            scores[strategy.name] = score

        if len(strategies) == 2:
            s1 = strategies[0].name
            s2 = strategies[1].name
            diff = scores[s1] - scores[s2]
            result[f"diff_{s1}_minus_{s2}"] = diff
            
            # Track winner for win percentage display
            if diff > 0:
                result["winner"] = "A_wins"
            elif diff < 0:
                result["winner"] = "B_wins"
            else:
                result["winner"] = "tie"
            
        return result

    try:
        report = runner.run(simulation_callback, num_simulations=num_simulations, generator_params=generator_params)
        return jsonify(report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Bridge Simulator API Running. <br><a href='/simulation'>Go to Simulation Lab</a>"

@app.route('/simulation')
def simulation_ui():
    from flask import send_from_directory
    return send_from_directory('templates', 'simulation.html')

@app.route('/static/<path:path>')
def send_static(path):
    from flask import send_from_directory
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
