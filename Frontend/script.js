let tasks = [];
let strategies = {};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('taskForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        addTask();
    });

    // Load strategies
    loadStrategies();

    // Update strategy description on change
    document.getElementById('strategy').addEventListener('change', updateStrategyDescription);

    updateTaskPreview();
});

// Load available strategies from backend
async function loadStrategies() {
    try {
        const res = await fetch("http://localhost:8000/api/tasks/strategies/");
        strategies = await res.json();
        updateStrategyDescription();
    } catch (error) {
        console.error('Error loading strategies:', error);
    }
}

// Update strategy description
function updateStrategyDescription() {
    const strategy = document.getElementById('strategy').value;
    const description = document.getElementById('strategyDescription');

    if (strategies[strategy]) {
        const info = strategies[strategy];
        description.innerHTML = `
            <strong>${info.icon} ${info.name}</strong><br>
            ${info.description}<br>
            <small>Weights: ${info.weights}</small>
        `;
    }
}

// Show alert messages
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Add task to the list
function addTask() {
    const title = document.getElementById("title").value;
    const dueDate = document.getElementById("due_date").value || null;
    const hours = document.getElementById("hours").value;
    const importance = document.getElementById("importance").value;
    const dependencies = document.getElementById("dependencies").value;

    // Validation
    if (!title.trim()) {
        showAlert('Please enter a task title', 'error');
        return;
    }

    if (!importance || importance < 1 || importance > 10) {
        showAlert('Importance must be between 1 and 10', 'error');
        return;
    }

    const task = {
        title: title.trim(),
        due_date: dueDate,
        estimated_hours: hours ? Number(hours) : 0,
        importance: Number(importance),
        dependencies: dependencies
            ? dependencies.split(",").map(s => s.trim()).filter(s => s)
            : []
    };

    tasks.push(task);
    showAlert(`Task "${task.title}" added successfully!`, 'success');

    // Clear form
    document.getElementById('taskForm').reset();

    // Update preview
    updateTaskPreview();
}

// Update task preview list
function updateTaskPreview() {
    const preview = document.getElementById('taskListPreview');

    if (tasks.length === 0) {
        preview.innerHTML = '';
        return;
    }

    let html = '<h3 style="color: #333; margin-top: 20px; margin-bottom: 12px;">Added Tasks (' + tasks.length + ')</h3>';
    html += '<ul class="task-list">';

    tasks.forEach((task, index) => {
        html += `
            <li class="task-item">
                <div class="task-info">
                    <h3>${task.title}</h3>
                    <div class="task-meta">
                        ${task.due_date ? `Due: ${formatDate(task.due_date)}` : 'No due date'} |
                        ${task.estimated_hours}h |
                        Priority: ${task.importance}/10
                        ${task.dependencies.length > 0 ? ` | Deps: ${task.dependencies.join(', ')}` : ''}
                    </div>
                </div>
                <div class="task-actions">
                    <button onclick="removeTask(${index})" style="background: #dc3545;">Remove</button>
                </div>
            </li>
        `;
    });

    html += '</ul>';
    preview.innerHTML = html;
}

// Remove task from list
function removeTask(index) {
    const task = tasks[index];
    tasks.splice(index, 1);
    showAlert(`Task "${task.title}" removed`, 'error');
    updateTaskPreview();
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Analyze and sort tasks
async function analyze() {
    // Validate we have tasks
    if (!tasks || tasks.length === 0) {
        showAlert('Please add tasks first', 'error');
        return;
    }

    // Get selected strategy
    const strategy = document.getElementById('strategy').value;

    // Get the analyze button and add loading state
    const analyzeBtn = event?.target;
    const originalText = analyzeBtn?.textContent;
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading"></span>Analyzing...';
    }

    try {
        const res = await fetch("http://localhost:8000/api/tasks/analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();

        // Display warnings if any
        if (data.warnings && data.warnings.length > 0) {
            data.warnings.forEach(warning => {
                showAlert(warning, 'error');
            });
        }

        // Display results
        displayResults(data.tasks, data.strategy);

        showAlert(`Tasks analyzed using ${data.strategy.name} strategy!`, 'success');

        // Show and scroll to results
        const resultsCard = document.getElementById('resultsCard');
        resultsCard.style.display = 'block';
        resultsCard.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });

    } catch (error) {
        console.error('Error analyzing tasks:', error);
        showAlert(`Error: ${error.message}. Make sure the backend server is running.`, 'error');
    } finally {
        // Restore button state
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = originalText;
        }
    }
}

// Display sorted results
function displayResults(sortedTasks, strategyInfo) {
    const resultsDiv = document.getElementById('results');

    if (!sortedTasks || sortedTasks.length === 0) {
        resultsDiv.innerHTML = '<p style="color: #999; text-align: center;">No tasks to display</p>';
        return;
    }

    let html = '';

    // Strategy info banner
    if (strategyInfo) {
        html += `
            <div class="strategy-banner">
                <span class="strategy-icon">${strategyInfo.icon}</span>
                <div class="strategy-info">
                    <strong>${strategyInfo.name}</strong>
                    <p>${strategyInfo.description}</p>
                    <small>${strategyInfo.weights}</small>
                </div>
            </div>
        `;
    }

    html += '<div class="sorted-task-list">';

    sortedTasks.forEach((task, index) => {
        // Priority 1 is highest, priority 10 is lowest
        const priority = index + 1;
        const priorityClass = priority <= 3 ? 'high-priority' : priority <= 7 ? 'medium-priority' : 'low-priority';
        const priorityLabel = priority <= 3 ? 'High' : priority <= 7 ? 'Medium' : 'Low';

        html += `
            <div class="sorted-task-item ${priorityClass}">
                <div class="task-rank">P${priority}</div>
                <div class="sorted-task-content">
                    <div class="sorted-task-header">
                        <h3>${task.title}</h3>
                        <div class="task-score ${priorityClass}">
                            <span class="score-label">${priorityLabel} Priority</span>
                            <span class="score-value">P${priority}</span>
                        </div>
                    </div>

                    <div class="sorted-task-meta">
                        ${task.due_date ? `<span class="meta-item"><strong>Due:</strong> ${formatDate(task.due_date)}</span>` : ''}
                        <span class="meta-item"><strong>Hours:</strong> ${task.estimated_hours}h</span>
                        <span class="meta-item"><strong>Importance:</strong> ${task.importance}/10</span>
                        ${task.dependencies && task.dependencies.length > 0 ? `<span class="meta-item"><strong>Dependencies:</strong> ${task.dependencies.join(', ')}</span>` : ''}
                    </div>

                    ${task.reasons && task.reasons.length > 0 ? `
                        <div class="task-reasons">
                            <strong>Why this priority:</strong>
                            <ul>
                                ${task.reasons.map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsDiv.innerHTML = html;
}

// Clear all tasks
function clearAllTasks() {
    if (tasks.length === 0) return;

    if (confirm(`Clear all ${tasks.length} tasks?`)) {
        tasks = [];
        updateTaskPreview();
        showAlert('All tasks cleared', 'error');
    }
}
