async function runSimulation() {
    const statusMsg = document.getElementById('statusMsg');
    statusMsg.classList.remove('d-none');
    statusMsg.textContent = "Running simulation (100 hands)...";

    // 1. Gather Generator Params
    const params = {
        num_hands: 100, // Small default for responsiveness in UI
        predeal: {
            'S': document.getElementById('southHand').value.trim()
        },
        smart_stack: {
            'N': {
                'shape': document.getElementById('northShape').value,
                'hcp': [
                    parseInt(document.getElementById('minHcp').value),
                    parseInt(document.getElementById('maxHcp').value)
                ]
            }
        }
    };

    // 2. Build Strategy A (Baseline - Fixed)
    const stratA = {
        name: document.getElementById('stratAName').value,
        root: {
            type: 'contract',
            contract: document.getElementById('stratAContract').value.toUpperCase(),
            declarer: 'N' // Simplifying assumption
        }
    };

    // 3. Build Strategy B (Conditional)
    // currently simple 1-level for demo
    const stratB = {
        name: document.getElementById('stratBName').value,
        root: {
            type: 'branch',
            condition: {
                type: 'suit_length',
                suit: document.getElementById('condSuit').value,
                operator: '>=',
                value: 4
            },
            true_branch: {
                type: 'contract',
                contract: document.getElementById('trueBid').value.toUpperCase(),
                declarer: 'N'
            },
            false_branch: {
                type: 'contract',
                contract: document.getElementById('falseBid').value.toUpperCase(),
                declarer: 'N'
            }
        }
    };

    const payload = {
        generator_params: params,
        strategies: [stratA, stratB],
        num_events: 100
    };

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.error) {
            statusMsg.textContent = "Error: " + data.error;
            statusMsg.classList.add('alert-danger');
            return;
        }

        displayResults(data, stratA.name, stratB.name);

    } catch (e) {
        statusMsg.textContent = "Network Error: " + e;
        statusMsg.classList.add('alert-danger');
    }
}

function displayResults(data, nameA, nameB) {
    const statusMsg = document.getElementById('statusMsg');
    statusMsg.classList.add('d-none');
    document.getElementById('statsRow').style.display = 'flex';

    // Calculate Stats
    const stats = data.stats;
    const diffKey = `diff_${nameA}_minus_${nameB}`;

    // Note: diff is A - B. If positive, A is better. If negative, B is better.
    // We typically want to show "Improvement of B over A" if B is the new strategy.
    // Let's show B - A.

    let avgDiff = 0;
    if (stats[diffKey]) {
        avgDiff = -(stats[diffKey].mean); // Invert to show B - A
    }

    const diffEl = document.getElementById('statDiff');
    diffEl.textContent = (avgDiff > 0 ? "+" : "") + avgDiff.toFixed(2);
    diffEl.style.color = avgDiff > 0 ? "green" : (avgDiff < 0 ? "red" : "black");

    // Chart
    const resultScoresA = stats[`${nameA}_score`].mean;
    const resultScoresB = stats[`${nameB}_score`].mean;

    // Destroy old chart if exists
    const canvas = document.getElementById('resultsChart');
    if (window.myChart) window.myChart.destroy();

    window.myChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: [nameA, nameB],
            datasets: [{
                label: 'Average Score',
                data: [resultScoresA, resultScoresB],
                backgroundColor: ['#6c757d', '#198754']
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Raw Output dump for detail
    document.getElementById('rawOutput').textContent = JSON.stringify(stats, null, 2);
}
