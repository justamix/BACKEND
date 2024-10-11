from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class ApplicationsSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    classrooms = serializers.SerializerMethodField()

    def get_creator(self, application):
        return application.creator.username
    
    def get_moderator(self, application):
        if application.moderator:
            return application.moderator.username

    def get_classrooms(self, app):
        classrooms = ApplicationClassrooms.objects.filter(app=app)
        return ClassroomsSerializer(classrooms, many=True).data
    
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


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
            user = User.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user