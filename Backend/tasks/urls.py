from django.urls import path
from .views import analyze_tasks, suggest_tasks, get_strategies

urlpatterns = [
    path('analyze/', analyze_tasks),
    path("suggest/", suggest_tasks),
    path("strategies/", get_strategies),
]
