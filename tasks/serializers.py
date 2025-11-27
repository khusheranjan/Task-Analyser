from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    title= serializers.CharField()
    due_date= serializers.DateField(required= False)
    estimated_hours= serializers.FloatField()
    importance= serializers.IntegerField()
    dependencies= serializers.ListField()