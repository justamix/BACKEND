from rest_framework import serializers
from models import *
from django.contrib.auth.models import User

class ApplicationsSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    classrooms = serializers.SerializerMethodField()

    def get_creator(self, expedition):
        return expedition.owner.username

    class Meta:
        model = Applications
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'password', 'username']
    
class ApplicationClassroomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationClassrooms
        fields = "__all__"

class ClassroomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classrooms
        fields = "__all__"
