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
    classrooms = Classrooms.objects.filter(status=1).filter(name__icontains=query)
    serializer = ClassroomsSerializer(classrooms, many=True)
    draft_booking = GetDraftBooking()
    response = {
        "classrooms": serializer.data,
        "draft_booking": draft_booking.app_id if draft_booking else None
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
@api_view(["GET"])
def get_classroom_image(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    response = requests.get(classroom.url.replace("localhost", "minio"))
    return HttpResponse(response, content_type="image/png")
#4
@api_view(["PUT"])
def update_classroom(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    image = request.data.get("image")
    if image is not None:
        classroom.url = image
        classroom.save()
    serializer = ClassroomsSerializer(classroom, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)
#5
@api_view(["PUT"])
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
#6
@api_view(["DELETE"])
def delete_classroom(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    classroom = Classrooms.objects.get(classroom_id=classroom_id)
    classroom.status = 2
    classroom.save()
    classrooms = Classrooms.objects.filter(status=1)
    serializer = ClassroomsSerializer(classrooms, many=True)
    return Response(serializer.data)
#7
@api_view(["POST"])
def create_classroom(request):
    Classrooms.objects.create()
    classrooms = Classrooms.objects.filter(status=1)
    serializer = ClassroomsSerializer(classrooms, many=True)
    return Response(serializer.data)
#8
@api_view(["POST"])
def add_classroom_to_event(request, classroom_id):
    if not Classrooms.objects.filter(classroom_id=classroom_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    classroom = Classrooms.objects.get(classroom_id=classroom_id)

    draft_booking = GetDraftBooking()

    if draft_booking is None:
        draft_booking =Applications.objects.create()
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
#9

#10

#11

#12

#13

#14

#15

#16

#17

#18

#19



# def GetClassrooms1(request):
#     """АУДИТОРИИ"""
#     #обработка поиска
#     search_address = request.GET.get('адрес аудитории', '')
#     classrooms = Classrooms.objects.filter(address__icontains=search_address, status='active')

#     #словарь с данными
#     context = {
#         'search_address' : search_address,  #запоминание ввода для поиска
#         'classrooms' : classrooms           
#     }
#     #проверка наличия черновика
#     draft_booking = GetDraftBooking()
#     if draft_booking:
#         context['len'] = len(draft_booking.GetClassrooms())
#         context['draft_booking'] = draft_booking
#     else:
#         context['draft_booking'] = None

#     return render(request, 'classrooms.html', context)



# def GetEventById(request, id):
#     """СТРАНИЦА КОРЗИНЫ"""
#     draft_booking = GetDraftBooking(id)
#     context = {
#         'id': id,
#         'event_name': draft_booking.event_name,
#         'fio': draft_booking.creator.username,
#         'date': draft_booking.event_date.strftime('%Y-%m-%d') if draft_booking.event_date else '',
#         'time_start': draft_booking.start_event_time.strftime('%H:%M') if draft_booking.start_event_time else '',
#         'classrooms': GetBooking(id),
#         'status': draft_booking.status
#     }

#     return render(request, 'event.html', context)

# def GetLongDescription(request, id):
#     """ПОДРОБНОЕ ОПИСАНИЕ"""
#     classroom = Classrooms.objects.get(classroom_id=id)
#     classroom.description = classroom.description.split('t')  
#     return render(request, 'long_description.html', { 'classroom' : classroom })



# def AddClassroomToDraftBooking(request, classroom_id):
#     """ДОБАВЛЕНИЕ АУДИТОРИИ В ЧЕРНОВИК ЗАЯВКИ"""
#     classroom = Classrooms.objects.get(classroom_id=classroom_id)
#     draft_booking = GetDraftBooking()
#     if draft_booking is None:
#         draft_booking = Applications.objects.create(
#             created_at=timezone.now(),
#             creator=GetCurrentUser(),
#             status=1
#         )
#         draft_booking.save()
#     if ApplicationClassrooms.objects.filter(app=draft_booking, classroom=classroom).exists():
#         return redirect("/")
#     ApplicationClassrooms.objects.create( 
#         app=draft_booking,
#         classroom=classroom
#     )
#     return redirect("/")
    
# def DeleteBooking(request, booking_id):
#     """УДАЛЕНИЕ ЧЕРНОВИКА БРОНИРОВАНИЯ"""
#     if request.method == "POST": 
#         submitted_time = timezone.now()
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "UPDATE Applications SET status = 2, submitted_at = %s WHERE app_id = %s",
#                 [submitted_time, booking_id]
#             )
#     return redirect("/")