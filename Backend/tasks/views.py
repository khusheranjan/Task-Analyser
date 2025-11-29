from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskSerializer
from .scoring import (
    calculate_priority,
    explain_choice,
    detect_circular_dependencies,
    STRATEGIES,
    get_strategy_info
)

@api_view(["POST"])
def analyze_tasks(request):
    """
    Analyze and sort tasks based on selected strategy.

    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance" | "fastest_wins" | "high_impact" | "deadline_driven",
        "custom_weights": {...} (optional, for smart_balance)
    }
    """
    # Extract parameters
    if isinstance(request.data, list):
        # Backward compatibility: if just array sent, assume smart_balance
        tasks_data = request.data
        strategy = "smart_balance"
        custom_weights = None
    else:
        tasks_data = request.data.get("tasks", [])
        strategy = request.data.get("strategy", "smart_balance")
        custom_weights = request.data.get("custom_weights")

    # Validate tasks
    serializer = TaskSerializer(data=tasks_data, many=True)
    serializer.is_valid(raise_exception=True)
    validated_tasks = serializer.validated_data

    # Check for circular dependencies
    dependency_check = detect_circular_dependencies(validated_tasks)

    # Calculate scores and explanations
    for task in validated_tasks:
        task["score"] = calculate_priority(task, strategy, custom_weights)
        task["reasons"] = explain_choice(task, strategy)

    # Sort by score (highest first)
    sorted_tasks = sorted(validated_tasks, key=lambda t: t["score"], reverse=True)

    # Prepare response
    response_data = {
        "tasks": sorted_tasks,
        "strategy": get_strategy_info(strategy),
        "warnings": dependency_check["warnings"] if dependency_check["has_circular"] else [],
        "circular_dependencies": dependency_check["cycles"] if dependency_check["has_circular"] else []
    }

    return Response(response_data)


@api_view(["POST"])
def suggest_tasks(request):
    """
    Get top 3 recommended tasks using smart_balance strategy.
    """
    tasks = request.data

    # Validate input
    serializer = TaskSerializer(data=tasks, many=True)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    # Score tasks using smart_balance
    for t in validated:
        t["score"] = calculate_priority(t, "smart_balance")
        t["reasons"] = explain_choice(t, "smart_balance")

    # Sort and pick top 3
    top_three = sorted(validated, key=lambda x: x["score"], reverse=True)[:3]

    return Response(top_three)


@api_view(["GET"])
def get_strategies(request):
    """
    Get available sorting strategies and their descriptions.
    """
    return Response(STRATEGIES)
