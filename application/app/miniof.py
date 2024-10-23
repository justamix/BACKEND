from django.conf import settings
from minio import Minio 
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *
import logging

logger = logging.getLogger(name)

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('bmstulab', image_name, file_object, file_object.size)
        return f"http://localhost:9000/bmstulab/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(new_classroom, pic):
    client = Minio(           
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    i = new_classroom.classroom_id
    img_obj_name = f"{i}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})
    result = process_file_upload(pic, client, img_obj_name)
    if 'error' in result:
        return Response(result)

    new_classroom.url = result
    new_classroom.save()
    

    return Response({"message": "success"})


def delete_pic(new_classroom):
    client = Minio(           
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )

    try:
        name_pic = new_classroom.url.split('/')[-1]
        logger.error(name_pic)
        client.remove_object(bucket_name='bmstulab', object_name=name_pic)

        return True
    except:
        return False