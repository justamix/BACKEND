from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/classrooms/search/', search_classrooms),  # 1 GET список с фильтрацией
    path('api/classrooms/<int:classroom_id>/', get_classroom_by_id),  # 2 GET одна запись
    path('api/classrooms/create/', create_classroom), # 3 POST добавление (без изображения)
    path('api/classrooms/<int:classroom_id>/update/', update_classroom),  # 4 PUT изменение
    path('api/classrooms/<int:classroom_id>/delete/', delete_classroom), # 5 DELETE удаление
    path('api/classrooms/<int:classroom_id>/add_to_event/', add_classroom_to_event),  # 6 POST добавления в заявку-черновик.
    path('api/classrooms/<int:classroom_id>/update_image/', update_classroom_image), # 7 POST добавление изображения. 
    
]