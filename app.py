from flask import Flask, render_template, jsonify
from bridge_simulator.hand_generator import BridgeHandGenerator

app = Flask(__name__)
generator = BridgeHandGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate-hand')
def generate_hand():
    """Generate a new bridge hand and return it as JSON."""
    hand = generator.generate_hand()
    return jsonify(hand)

@app.route('/api/hand-summary')
def hand_summary():
    """Get a summary of the current hand."""
    summary = generator.get_hand_summary()
    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
