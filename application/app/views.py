from django.contrib.auth import authenticate
from django.utils.dateparse import parse_datetime
from django.core.cache import cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import redis
import uuid
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .serializers import *
from .miniof import *
from random import randint


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def GetDraftBooking(request, id=None):
    """ПОЛУЧЕНИЕ ЧЕРНОВИКА ЗАЯВКИ"""
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    current_user = User.objects.get(username=username)
    if id is not None:
        return Applications.objects.filter(creator=current_user, app_id=id).first() 
    else:
        return Applications.objects.filter(creator=current_user, status=1).first() #так как у пользователя только один черновик, то берем первый элемент, иначе None

@api_view(["GET"])
def search_classrooms(request):
    query = request.query_params.get("name", "")
    classrooms = Classrooms.objects.filter(status='active', name__icontains=query)
    serializer = ClassroomsSerializer(classrooms, many=True)
    draft = GetDraftBooking(request)
    if draft:
        draft_count = ApplicationClassrooms.objects.filter(app=draft.app_id)
    response = {
        "classrooms" : serializer.data,
        "draft_event" : draft.app_id if draft else None,
        "classrooms_count" : draft_count.count() if draft else None
    }
    return Response(response)
#2
@api_view(["GET"])
def get_classroom_by_id(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    serializer = ClassroomsSerializer(classroom, many=False)
    return Response(serializer.data)
#3
@swagger_auto_schema(method='post', request_body=ClassroomsSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def create_classroom(request):
    classroom = Classrooms.objects.create()
    serializer = ClassroomsSerializer(classroom, many=False)
    return Response(serializer.data)
#4
@swagger_auto_schema(method='put', request_body=ClassroomsSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_classroom(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    name = request.data.get("name")
    if name is not None:
        classroom.name = name
        classroom.save()
    address = request.data.get("address")
    if address is not None:
        classroom.address = address
        classroom.save()
    description = request.data.get("description")
    if description is not None:
        classroom.description = description
        classroom.save()
    serializer = ClassroomsSerializer(classroom, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)
#5
@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_classroom(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    classroom.status = 'inactive'
    classroom.save()
    classrooms = Classrooms.objects.filter(status='active')
    serializer = ClassroomsSerializer(classrooms, many=True)
    return Response(serializer.data)
#6
@swagger_auto_schema(method='post', request_body=ApplicationsSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_classroom_to_event(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    draft_booking = GetDraftBooking(request)
    if draft_booking is None:
        draft_booking = Applications.objects.create()
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
        user = User.objects.get(username=username)
        draft_booking.creator = user
        draft_booking.created_at = timezone.now()
        draft_booking.save()
    if ApplicationClassrooms.objects.filter(app=draft_booking, classroom=classroom).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    item = ApplicationClassrooms.objects.create()
    item.app = draft_booking
    item.classroom = classroom
    item.save()
    serializer =ApplicationsSerializer(draft_booking, many=False)
    return Response(serializer.data)
#7
@swagger_auto_schema(method='post', request_body=ClassroomsSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def update_classroom_image(request, classroom_id):
    classroom = get_object_or_404(Classrooms, classroom_id = classroom_id)
    delete_pic(classroom) 
    new_pic = request.FILES.get('url')
    serializer = ClassroomsSerializer(classroom)
    pic_result = add_pic(classroom, new_pic)
    if 'error' in pic_result.data:
        return pic_result
    return Response(serializer.data, status=status.HTTP_201_CREATED)
#8
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def events_list(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    apps = Applications.objects.all()
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)

    if not user.is_staff:
        apps = apps.filter(creator=user)

    if status > 0:
        apps = apps.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        apps = apps.filter(created_at__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        apps = apps.filter(created_at__lt=parse_datetime(date_formation_end))

    serializer = ApplicationsSerializer(apps, many=True)
    return Response(serializer.data)
#9
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_event_by_id(request, event_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id, creator=user)
    serializer = ApplicationsSerializer(app, many=False)
    return Response(serializer.data)
#10
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_event_by_id(request, event_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id, creator=user)
    serializer = ApplicationsSerializer(app, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)
#11
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, event_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id, creator=user)
    if app.status == 1:
        app.status = 2
        app.submitted_at = timezone.now()
        app.save()
        serializer = ApplicationsSerializer(app, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#12
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.data["status"]
    if stat not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    app = Applications.objects.get(app_id=event_id)
    if app.status == 2:
        app.completed_at = timezone.now()
        #рассчетное поле
        if stat == 3:
            app.held_an_event = True if randint(1, 2) == 1 else False
        
        app.status = stat
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
        user = User.objects.get(username=username)
        app.moderator = user
        app.save()
        serializer = ApplicationsSerializer(app, many=False)
        return Response(serializer.data)
    else: 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#13
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_event(request, event_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id, creator=user)
    if app.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    app.status = 5
    app.submitted_at = timezone.now()
    app.save()
    return Response(status=status.HTTP_200_OK)
#14
@swagger_auto_schema(method='put', request_body=ApplicationClassroomsSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_classroom_in_event(request, event_id, classroom_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    if not ApplicationClassrooms.objects.filter(app_id=event_id, classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    item = ApplicationClassrooms.objects.get(app_id=event_id, classroom_id=classroom_id)
    finish_time = request.data.get("finish_time")
    if finish_time:
        try:
            parsed_time = timezone.datetime.strptime(finish_time, '%H:%M').time()
            item.finish_time = parsed_time
        except ValueError:
            return Response({"error": "Invalid time format. Use 'HH:MM'."}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ApplicationClassroomsSerializer(item, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#15
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_classroom_from_event(request, event_id, classroom_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not Applications.objects.filter(app_id=event_id, creator=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    if not ApplicationClassrooms.objects.filter(app_id=event_id, classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    item = ApplicationClassrooms.objects.get(app_id=event_id, classroom_id=classroom_id)
    item.delete()
    app = Applications.objects.get(app_id=event_id)
    serializer = ApplicationsSerializer(app, many=False)
    classrooms = serializer.data["classrooms"]
    if not len(classrooms):
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(classrooms)


#16
@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8')
    user = User.objects.get(username=username)
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


#17
@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request): 
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        if User.objects.filter(username = request.data['username']).exists(): 
            return Response({'status': 'Exist'}, status=400)
        serializer = UserRegisterSerializer(data=request.data) 
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

#18
@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        username = str(request.data["username"]) 
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        logger.error(user)
        if user is not None:
            random_key = str(uuid.uuid4()) 
            session_storage.set(random_key, username)

            response = Response({'status': f'{username} успешно вошел в систему'})
            response.set_cookie("session_id", random_key)

            return response
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
#19
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
        logout(request._request)
        response = Response({'Message': f'{username} вышел из системы'})
        response.delete_cookie('session_id')
        return response
    except:
        return Response({"Message":"Нет авторизованных пользователей"})

