from django.shortcuts import render
from datetime import date

def hello(request):
    return render(request, 'index.html', { 'data' : {
        'current_date': date.today(),
        'list': ['python', 'django', 'html']
    }})

def GetInfo(id=None):
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
    return {'id' : '1', 
            'event_name' : 'Хакатон',
            'ФИО' : 'Фролов Максим Кириллович',
            'date' : '09-20-2024',
            'time_start' : '13:00', 
            'classrooms' : [{
            'name': 'Зал заседаний', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr1.png', 
            'short_description': 'УАК 1, 1.05', 
            'time_end' : '19:00',
            'id': '1',
            'description': 'До 150 посадочных мест t Проектор, ноутбук (Linux, Р7 Офис) t Звуковое сопровождение'
        },
        {
            'name': 'Переговорная', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr2.png', 
            'short_description': 'УАК 1, 2.05',
            'time_end' : '12:00',
            'id': '2',
            'description': 'До 15 посадочных мест t Система видеоконференцсвязи (ВКС) t Проектор, компьютер (Linux, Р7 Офис) t МФУ (А4/А3 цвет.)'
        },
        {
            'name': 'Кабинет группы поддержки', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr3.png', 
            'short_description': 'УАК 1, 3.11', 
            'time_end' : '21:00',
            'id': '3',
            'description': '5 рабочих мест (Linux, Р7 Офис) t Веб-камеры, гарнитуры, колонки t МФУ (А4/А3 ч/б)'
        },
        {
            'name': 'Лекционная аудитория', 
            'image': 'http://127.0.0.1:9000/bmstulab/cr4.png', 
            'short_description': 'УАК 2, 2.60', 
            'time_end' : '19:00',
            'id': '4',
            'description': '40 посадочных мест t Проектор, компьютер (Linux, Р7 Офис)'
        }]}

def GetClassrooms(request):
    if request.method == 'GET':
        search_query = request.GET.get('адрес аудитории', '')
        classrooms = GetInfo()
        if search_query:
            classrooms = list(filter(lambda x: search_query.lower() in x['short_description'].lower(), classrooms))
        return render(request, 'classrooms.html', {
            'data': {
                'classrooms': classrooms,
                'booking': GetBooking(),
                'booking_counter': 0,
                'value': search_query,
                'len': len(GetBooking()['classrooms'])
            }
        })

def GetCartById(request, id):
    booking = GetBooking()
    event_name = request.GET.get('event_name', booking['event_name'])
    fio = request.GET.get('fio', booking['ФИО'])
    time_start = request.GET.get('time_start', booking['time_start'])
    date_value = request.GET.get('date', booking['date'])
    context = {
        'id': id,
        'event_name': event_name,
        'ФИО': fio,
        'date': date_value,
        'time_start': time_start,
        'classrooms': booking['classrooms']
    }
    
    return render(request, 'cart.html', context)
def GetLongDescription(request, id):
    a = {'data': GetInfo(id)}
    a['data']['description'] = a['data']['description'].split('t')
    return render(request, 'long_description.html', a)