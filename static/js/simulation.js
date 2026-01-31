// ============================================
// Multi-Level Condition Builder for Strategy B
// ============================================

let nodeCounter = 0;

function generateNodeId() {
    return `node_${++nodeCounter}`;
}

/**
 * Initialize the Strategy B builder with a root condition node
 */
function initStrategyBBuilder() {
    const container = document.getElementById('stratBBuilder');
    container.innerHTML = '';
    nodeCounter = 0;

    // Create initial root condition node
    const rootNode = createConditionNode('root', null);
    container.appendChild(rootNode);
}

/**
 * Create a condition node with selectors and branch containers
 * @param {string} nodeId - Unique ID for this node
 * @param {string|null} parentBranchType - 'true' or 'false' if nested, null if root
 */
function createConditionNode(nodeId, parentBranchType) {
    const div = document.createElement('div');
    div.className = 'condition-node';
    div.id = nodeId;
    div.dataset.nodeType = 'branch';

    // Condition header row
    div.innerHTML = `
        <div class="condition-header">
            <span>IF</span>
            <select class="form-select form-select-sm d-inline w-auto" data-field="condType" onchange="onConditionTypeChange('${nodeId}')">
                <option value="suit_length">Suit Length</option>
                <option value="hcp">HCP</option>
            </select>
            <span data-condtype-label="suit_length">
                <select class="form-select form-select-sm d-inline w-auto" data-field="suit">
                    <option value="H">Hearts</option>
                    <option value="S">Spades</option>
                    <option value="D">Diamonds</option>
                    <option value="C">Clubs</option>
                </select>
            </span>
            <select class="form-select form-select-sm d-inline w-auto" data-field="operator">
                <option value=">=">&gt;=</option>
                <option value=">">&gt;</option>
                <option value="==">=</option>
                <option value="<">&lt;</option>
                <option value="<=">&lt;=</option>
            </select>
            <input type="number" class="form-control form-control-sm d-inline w-auto" data-field="value" value="4" style="width: 60px;">
            ${parentBranchType !== null ? `<button type="button" class="btn btn-outline-danger btn-remove-condition" onclick="removeConditionNode('${nodeId}')">✕ Remove</button>` : ''}
        </div>
        
        <!-- TRUE Branch -->
        <div class="branch-container branch-true" id="${nodeId}_true_branch">
            <div class="branch-label">THEN:</div>
            <div class="branch-content" data-branch="true">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <label class="form-check-inline mb-0">
                        <input type="radio" name="${nodeId}_true_type" value="contract" checked onchange="onBranchTypeChange('${nodeId}', 'true')"> Bid
                    </label>
                    <input type="text" class="form-control form-control-sm" data-field="contract" value="2H" style="width: 70px;">
                    <span class="text-muted">by</span>
                    <select class="form-select form-select-sm" data-field="declarer" style="width: 70px;">
                        <option value="N">North</option>
                        <option value="S">South</option>
                    </select>
                    <span class="ms-2">|</span>
                    <label class="form-check-inline mb-0 ms-2">
                        <input type="radio" name="${nodeId}_true_type" value="nested" onchange="onBranchTypeChange('${nodeId}', 'true')"> Add Condition
                    </label>
                </div>
                <div class="nested-condition-container" style="display: none;"></div>
            </div>
        </div>
        
        <!-- FALSE Branch -->
        <div class="branch-container branch-false" id="${nodeId}_false_branch">
            <div class="branch-label">ELSE:</div>
            <div class="branch-content" data-branch="false">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <label class="form-check-inline mb-0">
                        <input type="radio" name="${nodeId}_false_type" value="contract" checked onchange="onBranchTypeChange('${nodeId}', 'false')"> Bid
                    </label>
                    <input type="text" class="form-control form-control-sm" data-field="contract" value="1N" style="width: 70px;">
                    <span class="text-muted">by</span>
                    <select class="form-select form-select-sm" data-field="declarer" style="width: 70px;">
                        <option value="N">North</option>
                        <option value="S">South</option>
                    </select>
                    <span class="ms-2">|</span>
                    <label class="form-check-inline mb-0 ms-2">
                        <input type="radio" name="${nodeId}_false_type" value="nested" onchange="onBranchTypeChange('${nodeId}', 'false')"> Add Condition
                    </label>
                </div>
                <div class="nested-condition-container" style="display: none;"></div>
            </div>
        </div>
    `;

    return div;
}

/**
 * Handle condition type change (suit_length vs hcp)
 */
function onConditionTypeChange(nodeId) {
    const node = document.getElementById(nodeId);
    const condType = node.querySelector('[data-field="condType"]').value;
    const suitLabel = node.querySelector('[data-condtype-label="suit_length"]');

    if (condType === 'suit_length') {
        suitLabel.style.display = 'inline';
    } else {
        suitLabel.style.display = 'none';
    }
}

/**
 * Handle branch type toggle (contract vs nested condition)
 */
function onBranchTypeChange(nodeId, branchType) {
    const node = document.getElementById(nodeId);
    const branchContainer = node.querySelector(`#${nodeId}_${branchType}_branch .branch-content`);
    const radioValue = branchContainer.querySelector(`input[name="${nodeId}_${branchType}_type"]:checked`).value;
    const nestedContainer = branchContainer.querySelector('.nested-condition-container');
    const contractInputs = branchContainer.querySelectorAll('[data-field="contract"], [data-field="declarer"]');

    if (radioValue === 'nested') {
        // Show nested condition container
        nestedContainer.style.display = 'block';
        contractInputs.forEach(el => el.style.display = 'none');

        // Create nested node if not exists
        if (nestedContainer.children.length === 0) {
            const newNodeId = generateNodeId();
            const nestedNode = createConditionNode(newNodeId, branchType);
            nestedContainer.appendChild(nestedNode);
        }
    } else {
        // Show contract inputs
        nestedContainer.style.display = 'none';
        contractInputs.forEach(el => el.style.display = 'inline-block');
    }
}

/**
 * Remove a nested condition node
 */
function removeConditionNode(nodeId) {
    const node = document.getElementById(nodeId);
    if (!node) return;

    // Find parent branch and toggle back to contract mode
    const parentBranch = node.closest('.branch-content');
    if (parentBranch) {
        const branchType = parentBranch.dataset.branch;
        const parentNode = parentBranch.closest('.condition-node');
        const parentNodeId = parentNode.id;

        // Set radio back to contract
        const contractRadio = parentBranch.querySelector(`input[name="${parentNodeId}_${branchType}_type"][value="contract"]`);
        if (contractRadio) {
            contractRadio.checked = true;
        }

        // Show contract inputs
        const contractInputs = parentBranch.querySelectorAll('[data-field="contract"], [data-field="declarer"]');
        contractInputs.forEach(el => el.style.display = 'inline-block');

        // Hide and clear nested container
        const nestedContainer = parentBranch.querySelector('.nested-condition-container');
        nestedContainer.style.display = 'none';
        nestedContainer.innerHTML = '';
    }
}

/**
 * Recursively build the strategy tree JSON from DOM
 */
function buildStrategyTree(nodeElement) {
    if (!nodeElement) return null;

    const nodeId = nodeElement.id;

    // Get condition fields
    const condType = nodeElement.querySelector('[data-field="condType"]').value;
    const operator = nodeElement.querySelector('[data-field="operator"]').value;
    const value = parseInt(nodeElement.querySelector('[data-field="value"]').value, 10);

    // Build condition object
    const condition = {
        type: condType,
        operator: operator,
        value: value
    };

    if (condType === 'suit_length') {
        condition.suit = nodeElement.querySelector('[data-field="suit"]').value;
    }

    // Build branches
    const trueBranch = buildBranch(nodeElement, nodeId, 'true');
    const falseBranch = buildBranch(nodeElement, nodeId, 'false');

    return {
        type: 'branch',
        condition: condition,
        true_branch: trueBranch,
        false_branch: falseBranch
    };
}

/**
 * Build a single branch (true or false)
 */
function buildBranch(nodeElement, nodeId, branchType) {
    const branchContent = nodeElement.querySelector(`#${nodeId}_${branchType}_branch .branch-content`);
    const radioValue = branchContent.querySelector(`input[name="${nodeId}_${branchType}_type"]:checked`).value;

    if (radioValue === 'nested') {
        // Recursively build nested condition
        const nestedNode = branchContent.querySelector('.nested-condition-container > .condition-node');
        if (nestedNode) {
            return buildStrategyTree(nestedNode);
        }
    }

    // Return contract leaf
    const contract = branchContent.querySelector('[data-field="contract"]').value.toUpperCase();
    const declarer = branchContent.querySelector('[data-field="declarer"]').value;

    return {
        type: 'contract',
        contract: contract,
        declarer: declarer
    };
}

// ============================================
// Main Simulation Runner
// ============================================

async function runSimulation() {
    const statusMsg = document.getElementById('statusMsg');
    statusMsg.classList.remove('d-none', 'alert-danger');
    statusMsg.classList.add('alert-secondary');
    statusMsg.textContent = "Running simulation (100 hands)...";

    // 1. Gather Generator Params
    const params = {
        num_hands: 100,
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
            declarer: 'N'
        }
    };

    // 3. Build Strategy B (Multi-level Conditional) - uses recursive tree builder
    const rootNode = document.getElementById('stratBBuilder').querySelector('.condition-node');
    const stratBRoot = buildStrategyTree(rootNode);

    const stratB = {
        name: document.getElementById('stratBName').value,
        root: stratBRoot
    };

    const payload = {
        generator_params: params,
        strategies: [stratA, stratB],
        num_events: 100
    };

    // Debug: log payload to console
    console.log('Simulation Payload:', JSON.stringify(payload, null, 2));

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

// ============================================
// Initialize on page load
// ============================================
document.addEventListener('DOMContentLoaded', function () {
    initStrategyBBuilder();
});
