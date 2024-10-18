from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from collections import OrderedDict


class ApplicationsSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    classrooms_count = serializers.SerializerMethodField()
    
    def get_creator(self, obj):
        return obj.creator.username
    
    def get_moderator(self, application):
        if application.moderator:
            return application.moderator.username

    def get_classrooms(self, app):
        classrooms = ApplicationClassrooms.objects.filter(app=app)
        return ClassroomsSerializer(classrooms, many=True).data
    
    def get_classrooms_count(self, obj):
        return ApplicationClassrooms.objects.filter(app=obj).count()
    
    class Meta:
        model = Applications
        fields = ['app_id', 'creator', 'moderator',  'created_at', 'submitted_at', 'completed_at', 'event_date', 'event_name', 'start_event_time', 'status', 'classrooms_count']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'password', 'username']
    
class ApplicationClassroomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationClassrooms
        fields = "__all__"

class ClassroomsSerializer(serializers.ModelSerializer):
    # classrooms_count = serializers.SerializerMethodField()

    # def get_classrooms_count(self, obj):
    #     return Classrooms.objects.filter(status='active').count()
    
    class Meta:
        model = Classrooms
        fields = "__all__"

    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 


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

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)