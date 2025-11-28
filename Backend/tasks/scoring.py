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


def explain_choice(task):
    reasons = []

    if task["due_date"]:
        # urgency reason
        days_left = (task["due_date"] - date.today()).days
        if days_left < 0:
            reasons.append("Past due — extremely urgent.")
        elif days_left <= 2:
            reasons.append("Due very soon — high urgency.")
        elif days_left <= 7:
            reasons.append("Deadline approaching within a week.")
    
    # importance reason
    if task["importance"] >= 8:
        reasons.append("Highly important task.")
    elif task["importance"] <= 3:
        reasons.append("Low importance task.")

    # effort reason
    if task["estimated_hours"] <= 2:
        reasons.append("Quick win — requires low effort.")
    elif task["estimated_hours"] >= 8:
        reasons.append("Large task — requires significant time.")

    # dependency reason
    dep_count = len(task.get("dependencies", []))
    if dep_count > 0:
        reasons.append(f"This task is blocking {dep_count} other tasks.")

    # no reasons
    if not reasons:
        reasons.append("Balanced task with no extreme factors.")

    return reasons
