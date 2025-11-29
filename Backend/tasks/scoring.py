from datetime import date
from typing import List, Dict, Set, Any, Optional

# ============================================================================
# SORTING STRATEGIES
# ============================================================================

def calculate_priority(task: Dict[str, Any], strategy: str = "smart_balance", custom_weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate task priority score based on selected strategy.
    Higher score = Higher priority (should be done first)

    Args:
        task: Task dictionary with fields (title, due_date, estimated_hours, importance, dependencies)
        strategy: One of ["smart_balance", "fastest_wins", "high_impact", "deadline_driven"]
        custom_weights: Optional custom weights for smart_balance strategy

    Returns:
        Priority score (float)
    """

    # Validate and sanitize task data
    task = sanitize_task_data(task)

    # Route to appropriate strategy
    if strategy == "fastest_wins":
        return calculate_fastest_wins(task)
    elif strategy == "high_impact":
        return calculate_high_impact(task)
    elif strategy == "deadline_driven":
        return calculate_deadline_driven(task)
    else:  # "smart_balance" (default)
        return calculate_smart_balance(task, custom_weights)


def calculate_smart_balance(task: Dict[str, Any], custom_weights: Optional[Dict[str, float]] = None) -> float:
    """
    Balanced approach considering all factors with configurable weights.
    """
    if custom_weights is None:
        weights = {
            "urgency": 0.35,      # How soon it's due
            "importance": 0.35,   # User-defined importance
            "effort": 0.15,       # Quick wins vs large tasks
            "dependencies": 0.15  # Tasks blocking others
        }
    else:
        weights = custom_weights

    urgency_score = calculate_urgency_score(task)
    importance_score = task.get("importance", 5)
    effort_score = calculate_effort_score(task)
    dependency_score = calculate_dependency_score(task)

    final = (
        urgency_score * weights.get("urgency", 0.35) +
        importance_score * weights.get("importance", 0.35) +
        effort_score * weights.get("effort", 0.15) +
        dependency_score * weights.get("dependencies", 0.15)
    )

    return round(final, 2)


def calculate_fastest_wins(task: Dict[str, Any]) -> float:
    """
    Prioritize quick, easy tasks (low effort).
    Formula: 70% effort + 20% importance + 10% urgency
    """
    effort_score = calculate_effort_score(task)
    importance_score = task.get("importance", 5)
    urgency_score = calculate_urgency_score(task)

    final = (
        effort_score * 0.70 +        # Heavily favor quick tasks
        importance_score * 0.20 +
        urgency_score * 0.10
    )

    return round(final, 2)


def calculate_high_impact(task: Dict[str, Any]) -> float:
    """
    Prioritize high-importance tasks above all else.
    Formula: 80% importance + 10% dependencies + 10% urgency
    """
    importance_score = task.get("importance", 5)
    dependency_score = calculate_dependency_score(task)
    urgency_score = calculate_urgency_score(task)

    final = (
        importance_score * 0.80 +    # Heavily favor important tasks
        dependency_score * 0.10 +
        urgency_score * 0.10
    )

    return round(final, 2)


def calculate_deadline_driven(task: Dict[str, Any]) -> float:
    """
    Prioritize tasks based on deadlines.
    Formula: 80% urgency + 15% importance + 5% effort
    """
    urgency_score = calculate_urgency_score(task)
    importance_score = task.get("importance", 5)
    effort_score = calculate_effort_score(task)

    final = (
        urgency_score * 0.80 +       # Heavily favor urgent tasks
        importance_score * 0.15 +
        effort_score * 0.05
    )

    return round(final, 2)


# ============================================================================
# COMPONENT SCORE CALCULATORS
# ============================================================================

def calculate_urgency_score(task: Dict[str, Any]) -> float:
    """
    Calculate urgency score (0-10) based on due date.
    Handles past due dates with extra urgency.
    """
    due = task.get("due_date")

    if due is None:
        return 3.0  # Default medium-low urgency for tasks without deadlines

    days_left = (due - date.today()).days

    # CRITICAL: Handle overdue tasks with escalating urgency
    if days_left < 0:
        overdue_days = abs(days_left)
        if overdue_days >= 7:
            return 10.0  # Severely overdue
        else:
            # Escalate: 10 for 1 day overdue, approaching 10 as more overdue
            return min(10.0, 10.0 + (overdue_days * 0.1))

    # Normal deadline-based urgency
    if days_left == 0:
        return 10.0
    elif days_left == 1:
        return 9.0
    elif days_left <= 3:
        return 8.0
    elif days_left <= 7:
        return 6.0
    elif days_left <= 14:
        return 4.0
    elif days_left <= 30:
        return 2.0
    else:
        return 1.0


def calculate_effort_score(task: Dict[str, Any]) -> float:
    """
    Calculate effort score (0-10).
    Quick wins get higher scores.
    """
    hours = task.get("estimated_hours", 0)

    if hours == 0:
        return 5.0  # Unknown effort - medium score
    elif hours <= 1:
        return 10.0  # Very quick task
    elif hours <= 3:
        return 8.0   # Quick task
    elif hours <= 6:
        return 6.0   # Medium task
    elif hours <= 12:
        return 4.0   # Large task
    else:
        return 2.0   # Very large task


def calculate_dependency_score(task: Dict[str, Any]) -> float:
    """
    Calculate dependency score (0-10).
    Tasks blocking more tasks get higher scores.
    """
    dep_count = len(task.get("dependencies", []))

    if dep_count == 0:
        return 0.0
    elif dep_count == 1:
        return 3.0
    elif dep_count == 2:
        return 6.0
    elif dep_count == 3:
        return 8.0
    else:
        return 10.0  # Blocking many tasks


# ============================================================================
# DATA VALIDATION & SANITIZATION
# ============================================================================

def sanitize_task_data(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize task data, handling missing or invalid fields.

    Critical considerations:
    - Missing fields get sensible defaults
    - Invalid data types are corrected
    - Edge cases are handled gracefully
    """
    sanitized = task.copy()

    # 1. TITLE: Required field
    if not sanitized.get("title") or not str(sanitized.get("title")).strip():
        sanitized["title"] = "Untitled Task"

    # 2. DUE_DATE: Must be a date object or None
    due_date = sanitized.get("due_date")
    if due_date is not None and not isinstance(due_date, date):
        # If it's a string, this should be handled by serializer
        # If it somehow got through, set to None
        sanitized["due_date"] = None

    # 3. ESTIMATED_HOURS: Must be non-negative number
    hours = sanitized.get("estimated_hours", 0)
    try:
        hours = float(hours)
        if hours < 0:
            hours = 0
        sanitized["estimated_hours"] = hours
    except (ValueError, TypeError):
        sanitized["estimated_hours"] = 0

    # 4. IMPORTANCE: Must be 1-10
    importance = sanitized.get("importance", 5)
    try:
        importance = int(importance)
        importance = max(1, min(10, importance))  # Clamp to 1-10
        sanitized["importance"] = importance
    except (ValueError, TypeError):
        sanitized["importance"] = 5  # Default medium importance

    # 5. DEPENDENCIES: Must be a list
    deps = sanitized.get("dependencies", [])
    if not isinstance(deps, list):
        sanitized["dependencies"] = []
    else:
        # Remove invalid dependencies (non-strings, empty strings)
        sanitized["dependencies"] = [
            str(d).strip() for d in deps
            if d and str(d).strip()
        ]

    return sanitized


# ============================================================================
# CIRCULAR DEPENDENCY DETECTION
# ============================================================================

def detect_circular_dependencies(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect circular dependencies in task list using graph cycle detection.

    Returns:
        {
            "has_circular": bool,
            "cycles": List[List[str]],  # List of circular dependency chains
            "warnings": List[str]        # Human-readable warnings
        }

    Algorithm: Depth-First Search (DFS) with recursion stack
    Time Complexity: O(V + E) where V = tasks, E = dependencies
    """
    # Build task title to task mapping
    task_map = {task["title"]: task for task in tasks}

    # Track visited nodes and recursion stack
    visited = set()
    rec_stack = set()
    cycles = []
    warnings = []

    def dfs(task_title: str, path: List[str]) -> bool:
        """
        DFS to detect cycles. Returns True if cycle found.
        """
        if task_title in rec_stack:
            # Found a cycle!
            cycle_start = path.index(task_title)
            cycle = path[cycle_start:] + [task_title]
            cycles.append(cycle)
            warnings.append(
                f"⚠️ Circular dependency detected: {' → '.join(cycle)}"
            )
            return True

        if task_title in visited:
            return False

        # Mark as visiting (in recursion stack)
        visited.add(task_title)
        rec_stack.add(task_title)

        # Visit all dependencies
        task = task_map.get(task_title)
        if task:
            for dep in task.get("dependencies", []):
                if dep in task_map:  # Only check dependencies that exist
                    if dfs(dep, path + [task_title]):
                        pass  # Continue to find all cycles

        # Remove from recursion stack
        rec_stack.remove(task_title)
        return False

    # Check all tasks for cycles
    for task in tasks:
        task_title = task["title"]
        if task_title not in visited:
            dfs(task_title, [])

    return {
        "has_circular": len(cycles) > 0,
        "cycles": cycles,
        "warnings": warnings
    }


# ============================================================================
# EXPLANATION SYSTEM
# ============================================================================

def explain_choice(task: Dict[str, Any], strategy: str = "smart_balance") -> List[str]:
    """
    Generate human-readable explanations for task priority.
    Explanations vary based on strategy used.
    """
    reasons = []

    due = task.get("due_date")
    importance = task.get("importance", 5)
    hours = task.get("estimated_hours", 0)
    dep_count = len(task.get("dependencies", []))

    # Strategy-specific prefix
    strategy_context = {
        "fastest_wins": "⚡ Quick Win Focus: ",
        "high_impact": "⭐ Impact Focus: ",
        "deadline_driven": "📅 Deadline Focus: ",
        "smart_balance": ""
    }
    prefix = strategy_context.get(strategy, "")

    # URGENCY EXPLANATIONS
    if due is not None:
        days_left = (due - date.today()).days

        if days_left < 0:
            overdue_days = abs(days_left)
            reasons.append(f"⚠️ OVERDUE by {overdue_days} day{'s' if overdue_days > 1 else ''} — needs immediate attention!")
        elif days_left == 0:
            reasons.append("🔥 Due TODAY — extremely urgent!")
        elif days_left == 1:
            reasons.append("⏰ Due TOMORROW — very high urgency")
        elif days_left <= 3:
            reasons.append(f"📅 Due in {days_left} days — high urgency")
        elif days_left <= 7:
            reasons.append(f"📆 Due in {days_left} days — deadline approaching")
        elif days_left <= 14:
            reasons.append(f"Due in {days_left} days — plan ahead")
        elif days_left <= 30:
            reasons.append(f"Due in {days_left} days — moderate urgency")
        else:
            reasons.append(f"Due in {days_left} days — low urgency")
    else:
        reasons.append("No deadline set — lower urgency")

    # IMPORTANCE EXPLANATIONS
    if importance >= 9:
        reasons.append(f"{prefix}⭐ CRITICAL importance (9-10/10)")
    elif importance >= 7:
        reasons.append(f"{prefix}⭐ High importance (7-8/10)")
    elif importance >= 5:
        reasons.append("Medium importance (5-6/10)")
    elif importance >= 3:
        reasons.append("Low importance (3-4/10)")
    else:
        reasons.append("Very low importance (1-2/10)")

    # EFFORT EXPLANATIONS
    if hours == 0:
        reasons.append("⏱️ Effort not estimated")
    elif hours <= 1:
        reasons.append(f"{prefix}⚡ Quick win — only 1 hour or less")
    elif hours <= 3:
        reasons.append(f"{prefix}⚡ Short task — 2-3 hours")
    elif hours <= 6:
        reasons.append("🔨 Medium task — half day of work")
    elif hours <= 12:
        reasons.append("🔨 Large task — 1-2 days of work")
    else:
        reasons.append(f"🏗️ Major project — {hours} hours estimated")

    # DEPENDENCY EXPLANATIONS
    if dep_count > 0:
        reasons.append(f"🔗 Blocking {dep_count} other task{'s' if dep_count > 1 else ''} — unblocks progress!")

    # STRATEGY-SPECIFIC NOTES
    if strategy == "fastest_wins" and hours <= 3:
        reasons.append("💨 Prioritized for quick completion")
    elif strategy == "high_impact" and importance >= 8:
        reasons.append("🎯 Prioritized for maximum impact")
    elif strategy == "deadline_driven" and due and (due - date.today()).days <= 3:
        reasons.append("⏰ Prioritized due to approaching deadline")

    return reasons


# ============================================================================
# STRATEGY METADATA
# ============================================================================

STRATEGIES = {
    "smart_balance": {
        "name": "Smart Balance",
        "description": "Balanced approach considering all factors equally",
        "icon": "⚖️",
        "weights": "35% urgency, 35% importance, 15% effort, 15% dependencies"
    },
    "fastest_wins": {
        "name": "Fastest Wins",
        "description": "Prioritize quick, easy tasks for momentum",
        "icon": "⚡",
        "weights": "70% effort (quick tasks), 20% importance, 10% urgency"
    },
    "high_impact": {
        "name": "High Impact",
        "description": "Focus on most important tasks regardless of difficulty",
        "icon": "⭐",
        "weights": "80% importance, 10% dependencies, 10% urgency"
    },
    "deadline_driven": {
        "name": "Deadline Driven",
        "description": "Prioritize based on due dates and urgency",
        "icon": "📅",
        "weights": "80% urgency, 15% importance, 5% effort"
    }
}


def get_strategy_info(strategy: str) -> Dict[str, str]:
    """Get metadata about a sorting strategy."""
    return STRATEGIES.get(strategy, STRATEGIES["smart_balance"])
