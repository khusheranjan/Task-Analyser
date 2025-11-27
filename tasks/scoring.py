from datetime import date

def calculate_priority(task, weights=None):
    if weights is None:
        weights = {
            "urgency": 0.4,
            "importance": 0.4,
            "effort": 0.1,
            "dependencies": 0.1
        }

    # Urgency
    due = task.get("due_date")
    if due is None:
        urgency_score = 0
    else:
        days_left = (due - date.today()).days
        if days_left < 0:
            urgency_score = 10
        else:
            urgency_score = max(0, 10 - days_left)

    # Importance
    importance_score = task.get("importance", 5)

    # Effort
    hours = task.get("estimated_hours", 1)
    effort_score = 10 / (hours + 1)

    # Dependencies
    dependency_score = len(task.get("dependencies", []))

    # Weighted score
    final = (
        urgency_score * weights["urgency"] +
        importance_score * weights["importance"] +
        effort_score * weights["effort"] +
        dependency_score * weights["dependencies"]
    )

    return round(final, 2)
