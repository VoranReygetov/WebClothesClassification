from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from detection.inference import run_detection
from detection.video import analyze_video
from django.shortcuts import render, redirect
import os, json
import logging

logger = logging.getLogger(__name__)

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


def detect_video(request):
    context = {}

    if request.method == 'POST':
        if 'video' in request.FILES:
            video = request.FILES['video']
            fs = FileSystemStorage()
            filename = fs.save(video.name, video)
            video_path = fs.path(filename)

            result = analyze_video(video_path)
            summary_data = result
            result_path = result["video_path"]

            table_data = []
            for class_name, total in summary_data['summary'].items():
                row = {
                    'class': class_name,
                    'total_presence': total,
                    'frames': []
                }
                for chunk in summary_data['chunks']:
                    if class_name in chunk['presence']:
                        row['frames'].append({
                            'start': chunk['start'],
                            'end': chunk['end'],
                            'presence': chunk['presence'][class_name]
                        })
                table_data.append(row)

            rel_path = os.path.relpath(result_path, settings.MEDIA_ROOT)
            context['video_url'] = settings.MEDIA_URL + rel_path.replace('\\', '/')
            context['summary'] = table_data
            context['summary_json'] = json.dumps(summary_data, indent=2, ensure_ascii=False)

    return render(request, 'video_result.html', context)


def stream_video(request):
    return render(request, 'stream.html')
