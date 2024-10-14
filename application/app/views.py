import requests
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response 

from .serializers import *

def GetDraftBooking(id=None):
    """ПОЛУЧЕНИЕ ЧЕРНОВИКА ЗАЯВКИ"""
    current_user = GetUser()
    if id is not None:
        return Applications.objects.filter(creator=current_user.id, app_id=id).first() 
    else:
        return Applications.objects.filter(creator=current_user.id, status=1).first() #так как у пользователя только один черновик, то берем первый элемент, иначе None
def GetUser():
    """ВЫБОР ПОЛЬЗОВАТЕЛЯ"""
    return User.objects.filter(is_superuser=False).first()
def get_moderator():
    return User.objects.filter(is_superuser=True).first()
def GetBooking(id):
    """Информация об аудиториях в бронировании"""
    draft_booking = GetDraftBooking(id)
    # Получаем все аудитории, связанные с черновиком заявки
    application_classrooms = ApplicationClassrooms.objects.filter(app=draft_booking)
    classrooms = []
    for item in application_classrooms:
        classroom = {
            'info': Classrooms.objects.get(classroom_id=item.classroom_id),  # Получаем объект аудитории
            'finish_time': item.finish_time.strftime('%H:%M') if item.finish_time else ''# Время окончания
        }
        classrooms.append(classroom)
    return classrooms
#1
@api_view(["GET"])
def search_classrooms(request):
    query = request.GET.get("адрес аудитории", "")
    classrooms = Classrooms.objects.filter(status='active', name__icontains=query)
    serializer = ClassroomsSerializer(classrooms, many=True)
    draft = GetDraftBooking()
    response = {
        "classrooms" : serializer.data,
        "draft_event" : draft.app_id if draft else None,
        "classrooms_count" : classrooms.count()
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
@api_view(["POST"])
def create_classroom(request):
    Classrooms.objects.create()
    classrooms = Classrooms.objects.filter(status='active')
    serializer = ClassroomsSerializer(classrooms, many=True)
    return Response(serializer.data)
#4
@api_view(["PUT"])
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
@api_view(["POST"])
def add_classroom_to_event(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    draft_booking = GetDraftBooking()
    if draft_booking is None:
        draft_booking = Applications.objects.create()
        draft_booking.creator = GetUser()
        draft_booking.created_at = timezone.now()
        draft_booking.save()
    if ApplicationClassrooms.objects.filter(app=draft_booking, classroom=classroom).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    item = ApplicationClassrooms.objects.create()
    item.app = draft_booking
    item.classroom = classroom
    item.save()
    serializer =ApplicationsSerializer(draft_booking, many=False)
    return Response(serializer.data["classrooms"])
#7
@api_view(["POST"])
def update_classroom_image(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    image = request.data.get("image")
    if image is not None:
        classroom.url = image
        classroom.save()
    serializer = ClassroomsSerializer(classroom)
    return Response(serializer.data)
#8
@api_view(["GET"])
def events_list(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    apps = Applications.objects.all()

    if date_formation_start and parse_datetime(date_formation_start):
        apps = apps.filter(created_at__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        apps = apps.filter(created_at__lt=parse_datetime(date_formation_end))

    serializer = ApplicationsSerializer(apps, many=True)
    

    return Response(serializer.data)
#9
@api_view(["GET"])  
def get_event_by_id(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id)
    serializer = ApplicationsSerializer(app, many=False)
    return Response(serializer.data)
#10
@api_view(["PUT"])
def update_event_by_id(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id)
    event_date = request.data.get("event_date")
    if event_date is not None:
        app.event_date = event_date
        app.save()
    event_name = request.data.get("event_name")
    if event_name is not None:
        app.event_name = event_name
        app.save()
    start_event_time = request.data.get("start_event_time")
    if start_event_time is not None:
        app.start_event_time = start_event_time
        app.save()
    serializer = ApplicationsSerializer(app, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)
#11
@api_view(["PUT"])
def update_status_user(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id)
    if app.status == 1:
        app.status = 2
        app.submitted_at = timezone.now()
        app.save()
        serializer = ApplicationsSerializer(app, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#12
@api_view(["PUT"])
def update_status_admin(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.data["status"]
    if stat not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    app = Applications.objects.get(app_id=event_id)
    if app.status == 2:
        app.completed_at = timezone.now()
        app.status = stat
        app.moderator = get_moderator()
        app.save()
        serializer = ApplicationsSerializer(app, many=False)
        return Response(serializer.data)
    else: 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#13
@api_view(["DELETE"])
def delete_event(request, event_id):
    if not Applications.objects.filter(app_id=event_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    app = Applications.objects.get(app_id=event_id)
    if app.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    app.status = 5
    app.submitted_at = timezone.now()
    app.save()
    serializer = ApplicationsSerializer(app, many=False)
    return Response(serializer.data)
#14
@api_view(["PUT"])
def update_classroom_in_event(request, event_id, classroom_id):
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
def delete_classroom_from_event(request, event_id, classroom_id):
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
@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)
#17
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)