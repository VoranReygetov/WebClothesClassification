from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from detection.inference import run_detection
import os

def home(request):
    return render(request, 'home.html')

def detect(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.path(filename)
        image_url = fs.url(filename)

        # Запуск YOLO
        result_path, class_names, boxes = run_detection(image_path)

        # JSON API-вивід
        if 'json_output' in request.POST:
            return JsonResponse({
                'image': os.path.basename(result_path),
                'predictions': [
                    {
                        "x": box['x'],
                        "y": box['y'],
                        "width": box['width'],
                        "height": box['height'],
                        "confidence": box['confidence'],
                        "class": box['class']
                    }
                    for box in boxes
                ]
            })

        # HTML-рендерінг
        context['image_url'] = image_url
        context['result_url'] = '/' + result_path.replace('\\', '/')
        context['class_names'] = class_names
        context['predictions'] = boxes

    return render(request, 'result.html', context)
