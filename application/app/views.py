from django.shortcuts import render, redirect
from datetime import date
from app.models import Classrooms, Applications, ApplicationClassrooms
from django.utils import timezone
from django.contrib.auth.models import User

def GetClassrooms(id=None):
    classrooms = Classrooms.objects.all()
    arr = []
    for classroom in classrooms:
        arr.append(dict(id=classroom.classroom_id, name=classroom.name, image=classroom.url, short_description=classroom.address, description=classroom.description))
    return arr if id is None else arr[id-1]

def GetBooking():
    bookings = {
        'bookings' : [
            {
                'id' : '1', 
                'event_name' : 'Хакатон',
                'ФИО' : 'Фролов Максим Кириллович',
                'date' : '09.20.2024',
                'time_start' : '13:00', 
                'classrooms' : [
                    {
                        'info' : GetClassrooms(1),
                        'time_end' : '14:00'    
                    },
                    {
                        'info' : GetClassrooms(2),
                        'time_end' : '15:00'
                    },
                    {
                        'info' : GetClassrooms(3),
                        'time_end' : '16:00'
                    },
                    {
                        'info' : GetClassrooms(4),
                        'time_end' : '17:00'
                    }
                ]
            }
        ]
    }
    return bookings




def GetClassrooms1(request):
    """АУДИТОРИИ"""
    #обработка поиска
    search_address = request.GET.get('адрес аудитории', '')
    classrooms = Classrooms.objects.filter(address__icontains=search_address, status='active')

    #словарь с данными
    context = {
        'search_address' : search_address,  #запоминание ввода для поиска
        'classrooms' : classrooms           #массив с доступными аудиториями
    }
    #проверка наличия черновика
    draft_booking = GetDraftBooking()
    if draft_booking:
        context['len'] = len(draft_booking.GetClassrooms())
        context['draft_booking'] = draft_booking

    return render(request, 'classrooms.html', context)



def GetCartById(request, id):
    booking = GetBooking()
    current_booking = None

    for b in booking['bookings']:
        if b['id'] == str(id):
            current_booking = b
            break

    event_name = request.GET.get('event_name', current_booking['event_name'])
    fio = request.GET.get('fio', current_booking['ФИО'])
    time_start = request.GET.get('time_start', current_booking['time_start'])
    date_value = request.GET.get('date', current_booking['date'])

    context = {
        'id': id,
        'event_name': event_name,
        'ФИО': fio,
        'date': date_value,
        'time_start': time_start,
        'classrooms': current_booking['classrooms']  # Аудитории в рамках текущей заявки
    }

    return render(request, 'cart.html', context)



def GetLongDescription(request, id):
    """ПОДРОБНОЕ ОПИСАНИЕ"""
    classroom = Classrooms.objects.get(classroom_id=id)
    classroom.description = classroom.description.split('t')  
    return render(request, 'long_description.html', { 'classroom' : classroom })

def GetDraftBooking():
    """ПОЛУЧЕНИЕ ЧЕРНОВИКА ЗАЯВКИ"""
    return Applications.objects.filter(status='черновик').first() #так как у пользователя только один черновик, то берем первый элемент, иначе None

def GetCurrentUser():
    """ВЫБОР ПОЛЬЗОВАТЕЛЯ"""
    return User.objects.filter(is_superuser=False).first()

def AddClassroomToDraftBooking(request, classroom_id):
    """ДОБАВЛЕНИЕ АУДИТОРИИ В ЧЕРНОВИК"""
    classroom = Classrooms.objects.filter(classroom_id=classroom_id)

    draft_booking = GetDraftBooking()

    if draft_booking is None:
        draft_booking = Applications.objects.create()
        draft_booking.created_at = timezone.now()
        draft_booking.creator = GetCurrentUser()
        draft_booking.save()                                #сохранение в бд

    if ApplicationClassrooms.objects.filter(app_id=draft_booking.app_id, classroom_id=classroom_id).exists():
        return redirect("/")
    
    application_classrooms = ApplicationClassrooms.objects.create()
    application_classrooms.app_id = draft_booking
    application_classrooms.classroom_id = draft_booking
    application_classrooms.save()

    return redirect("/")

