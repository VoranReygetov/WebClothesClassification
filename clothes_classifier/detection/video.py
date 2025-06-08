import os
import cv2
import uuid
from collections import defaultdict
import logging
from ultralytics import YOLO
import torch

logger = logging.getLogger(__name__)

model = YOLO("D:\\Program Files\\KPI\\WebClothesClassification\\clothes_classifier\\detection\\best.pt")


def analyze_video(video_path, output_dir='media/results'):
    run_id = f"video_{uuid.uuid4().hex[:8]}"
    save_dir = os.path.join(output_dir, run_id)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_video_path = os.path.join(save_dir, os.path.basename(video_path))
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(out_video_path, fourcc, fps, (width, height))

    frame_index = 0
    presence_counter = defaultdict(int)
    time_chunks = defaultdict(lambda: defaultdict(int))
    total_detections = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, verbose=False)[0]
        boxes = results.boxes
        if boxes:
            for box in boxes:
                cls = int(box.cls[0].item())
                label = model.names[cls]
                conf = box.conf[0].item()
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                # Малюємо прямокутник та назву
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Лічильники
                presence_counter[label] += 1
                chunk_index = int((frame_index / fps) // 10)
                time_chunks[chunk_index][label] += 1
                total_detections += 1

        out.write(frame)
        frame_index += 1

    cap.release()
    out.release()

    # Розрахунок відсотків присутності
    summary_percent = {
        k: round((v / total_detections) * 100, 2)
        for k, v in presence_counter.items()
    }

    # Статистика по фреймах
    chunk_stats = []
    for chunk, classes in sorted(time_chunks.items()):
        chunk_total = sum(classes.values())
        percent = {
            k: round((v / chunk_total) * 100, 2)
            for k, v in classes.items()
        }
        chunk_stats.append({
            "start": chunk * 10,
            "end": (chunk + 1) * 10,
            "presence": percent
        })

    return {
        "video_name": os.path.basename(out_video_path),
        "video_path": out_video_path,
        "summary": summary_percent,
        "chunks": chunk_stats
    }