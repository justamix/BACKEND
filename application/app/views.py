from django.shortcuts import render
from datetime import date
from app.models import Classrooms


def GetClassrooms(id=None):
    arr = [
        {
            'name': 'Зал заседаний', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr1.png', 
            'short_description': 'УАК 1, 1.05', 
            'id': '1',
            'description': 'До 150 посадочных мест t Проектор, ноутбук (Linux, Р7 Офис) t Звуковое сопровождение'
        },
        {
            'name': 'Переговорная', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr2.png', 
            'short_description': 'УАК 1, 2.05', 
            'id': '2',
            'description': 'До 15 посадочных мест t Система видеоконференцсвязи (ВКС) t Проектор, компьютер (Linux, Р7 Офис) t МФУ (А4/А3 цвет.)'
        },
        {
            'name': 'Кабинет группы поддержки', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr3.png', 
            'short_description': 'УАК 1, 3.11', 
            'id': '3',
            'description': '5 рабочих мест (Linux, Р7 Офис) t Веб-камеры, гарнитуры, колонки t МФУ (А4/А3 ч/б)'
        },
        {
            'name': 'Лекционная аудитория', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr4.png', 
            'short_description': 'УАК 2, 2.60', 
            'id': '4',
            'description': '40 посадочных мест t Проектор, компьютер (Linux, Р7 Офис)'
        },
        {
            'name': 'Лекционная аудитория', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr5.png', 
            'short_description': 'УАК 2, 2.65', 
            'id': '5',
            'description': '40 посадочных мест t Проектор, компьютер (Linux, Р7 Офис)'
        },
        {
            'name': 'Холл', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr6.png', 
            'short_description': 'МОАЗ, 1 этаж', 
            'id': '6',
            'description': 'Вместимость до 400 человек t Возможна установка проектора t Возможна установка плазменной панели (50") t Возможно звуковое сопровождение'
        },
        {
            'name': 'Зал столовой', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr7.png', 
            'short_description': 'МОАЗ, 2 этаж', 
            'id': '7',
            'description': 'Вместимость до 468 человек t Возможна установка проектора t Возможна установка плазменной панели (50") t Возможно звуковое сопровождение'
        },
        {
            'name': 'Выставочные кабинеты', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr8.png', 
            'short_description': 'МОАЗ, 2 этаж', 
            'id': '8',
            'description': '7 доступных кабинетов t Общая вместимость до 60 человек t Возможна установка проектора t Возможна установка плазменной панели (50")'
        }
    ]
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
    if request.method == 'GET':
        search_query = request.GET.get('адрес аудитории', '')
        classrooms = GetClassrooms()
        booking_data = GetBooking()  # Получаем данные заявки
        first_booking_id = booking_data['bookings'][0]['id'] if booking_data['bookings'] else None  # Проверяем наличие заявок

        if search_query:
            classrooms = list(filter(lambda x: search_query.lower() in x['short_description'].lower(), classrooms))
        
        return render(request, 'classrooms.html', {
            'data': {
                'classrooms': classrooms,
                'booking': booking_data,
                'first_booking_id': first_booking_id,  # Добавляем первый ID заявки в контекст
                'booking_counter': len(booking_data['bookings']),
                'value': search_query,
                'len': len(booking_data['bookings'][0]['classrooms']) if first_booking_id else 0
            }
        })
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
    a = {
        'data' : GetClassrooms(id)
        }
    a['data']['description'] = a['data']['description'].split('t')
    return render(request, 'long_description.html', a)