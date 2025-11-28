from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TaskSerializer
from .scoring import calculate_priority

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