from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TaskSerializer
from .scoring import calculate_priority, explain_choice

@api_view(["POST"])
def analyze_tasks(request):
    tasks= request.data

    serializer= TaskSerializer(data= tasks, many= True)
    serializer.is_valid(raise_exception=True)

    validated_task= serializer.validated_data

    for task in validated_task:
        task["score"]= calculate_priority(task)

    sorted_tasks= sorted(validated_task, key= lambda t: t["score"], reverse=True)

    return Response(sorted_tasks)


@api_view(["POST"])
def suggest_tasks(request):
    tasks = request.data

    # Validate input
    serializer = TaskSerializer(data=tasks, many=True)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    # Score tasks
    for t in validated:
        t["score"] = calculate_priority(t)
        t["reasons"] = explain_choice(t)

    # Sort and pick top 3
    top_three = sorted(validated, key=lambda x: x["score"], reverse=True)[:3]

    return Response(top_three)
