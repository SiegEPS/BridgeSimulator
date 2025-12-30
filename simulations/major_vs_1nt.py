import sys
import os

# Ensure we can import bridge_simulator
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bridge_simulator.simulator import SimulationRunner

def major_vs_1nt_callback(deal, solver):
    """
    Simulation Callback for comparing 1NT vs Weak Major Suit Stayman.
    
    Scenario:
    - South holds: K842 QT72 986 52 (4-4 Majors, 5 HCP).
    - North holds: 15-17 NT Balanced.
    - Comparison: 1NT (North) vs Strategy of bidding Stayman.
    
    Strategy Logic:
    1. Bid 2C (Stayman).
    2. If North bids 2S (4 spades): We play 2S (North Declarer).
    3. If North bids 2H (4 hearts): We play 2H (North Declarer).
       (Note: If North has 4S and 4H, system usually bids 2H first or has priority.
        User specified: "if there major length is equal we will be in 2H not 2S".)
    4. If North bids 2D (no major): We play 2D (South passes 2D? or North Declarer?).
       Usually Stayman responses are by Opener (N). 2D is N. South passes.
       So contract is 2D by North.
    """
    
    # 1. Determine Contract for "Strategy B" (Stayman)
    north_hand = deal.north
    n_spades = len(north_hand.spades)
    n_hearts = len(north_hand.hearts)
    
    stayman_contract = "2D" # Placeholder
    stayman_declarer = "N"
    
    # Priority: 2H if 4+ Hearts (even if 4 Spades, per user rule "equal -> 2H")
    if n_hearts >= 4:
        stayman_contract = "2H"
        stayman_declarer = "N" # North bids 2H
    elif n_spades >= 4:
        stayman_contract = "2S"
        stayman_declarer = "N" # North bids 2S
    else:
        # North bids 2D (No 4-card Major)
        # User Rule: "if North bids 2D, we still play 2H (unless N has 3 spades and 2 hearts, in which case they will play 2S)"
        
        # South bids 2H or 2S over 2D. South is Declarer.
        if n_spades == 3 and n_hearts == 2:
            stayman_contract = "2S"
            stayman_declarer = "N"
        else:
            stayman_contract = "2H"
            stayman_declarer = "S"
        
    # 2. Compare Scores
    # Vulnerability: False (Simplifying assumption, or could be random)
    
    score_1nt = solver.get_score("1N", "N", vulnerable=False)
    score_stayman = solver.get_score(stayman_contract, stayman_declarer, vulnerable=False)
    
    return {
        'score_1nt': score_1nt,
        'score_stayman': score_stayman,
        'contract_stayman': stayman_contract, # Track distribution of contracts
        'stayman_gain': score_stayman - score_1nt,
        'stayman_beats_1nt': 1 if score_stayman > score_1nt else 0,
        '1nt_beats_stayman': 1 if score_1nt > score_stayman else 0,
        'push': 1 if score_1nt == score_stayman else 0
    }

def run():
    print("Running Simulation: 1NT vs Stayman (Selected Hand)")
    print("South: K842 QT72 986 52")
    print("North: 15-17 Balanced")
    print("-" * 40)
    
    runner = SimulationRunner()
    
    # Exact South Hand
    # S: K842, H: QT72, D: 986, C: 52
    south_hand_str = "K842 QT72 986 52"
    
    params = {
        'smart_stack': {
            'N': {'shape': 'balanced', 'hcp': (15, 17)}
        },
        'predeal': {
            'S': south_hand_str
        }
    }
    
    results = runner.run(major_vs_1nt_callback, num_simulations=1000, generator_params=params)
    
    stats = results['stats']
    n_sims = results['simulations_run']
    
    print(f"Simulations Run: {n_sims}")
    print(f"1NT Mean Score: {stats['score_1nt']['mean']:.2f}")
    print(f"Stayman Mean Score: {stats['score_stayman']['mean']:.2f}")
    print(f"Avg Gain from Stayman: {stats['stayman_gain']['mean']:.2f} points")
    print("-" * 40)
    
    win_pct = (stats['stayman_beats_1nt']['mean'] * 100)
    loss_pct = (stats['1nt_beats_stayman']['mean'] * 100)
    push_pct = (stats['push']['mean'] * 100)
    
    print(f"Stayman Wins: {win_pct:.1f}%")
    print(f"1NT Wins (Stayman Loss): {loss_pct:.1f}%")
    print(f"Push (Equal): {push_pct:.1f}%")
    
    print("-" * 40)
    print("Contract Distribution (Stayman):")
    contracts = stats['contract_stayman']
    for contract, count in sorted(contracts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {contract}: {count} ({count/n_sims*100:.1f}%)")

if __name__ == "__main__":
    run()
