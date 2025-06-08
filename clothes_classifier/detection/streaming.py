from channels.generic.websocket import WebsocketConsumer
import cv2
import numpy as np
import base64
import json
import logging
from collections import defaultdict
import os
import time
logger = logging.getLogger(__name__)

# Initialize YOLO model
try:
    from ultralytics import YOLO
    model_path = "D:\\Program Files\\KPI\\WebClothesClassification\\clothes_classifier\\detection\\best.pt"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    model = YOLO(model_path)
    import torch
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    raise RuntimeError(f"Failed to load model: {e}")

# ... (збережено попередні імпорти та ініціалізацію моделі)

def run_detection_stream(frame, presence_counter=None, total_detections=0):
    if presence_counter is None:
        presence_counter = defaultdict(int)

    if frame is None or frame.size == 0:
        logger.error("Invalid frame received, shape: %s, size: %d", str(frame.shape) if frame is not None else "None", frame.size if frame is not None else 0)
        return frame, presence_counter, total_detections, {}, {}

    try:
        results = model.predict(frame, verbose=False)[0]
        boxes = results.boxes
        frame_detections = defaultdict(int)
        annotations = []

        logger.info(f"Detected {len(boxes)} boxes")
        if boxes:
            for box in boxes:
                cls = int(box.cls[0].item())
                label = model.names[cls]
                conf = box.conf[0].item()
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                x = x1
                y = y1
                width = x2 - x1
                height = y2 - y1
                annotations.append({
                    'x': float(x),
                    'y': float(y),
                    'width': float(width),
                    'height': float(height),
                    'class': label,
                    'confidence': float(conf)
                })
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                presence_counter[label] += 1
                frame_detections[label] += 1
                total_detections += 1

        summary = {k: round((v / total_detections) * 100, 2) if total_detections > 0 else 0 for k, v in presence_counter.items()}
        frame_total = sum(frame_detections.values())
        frame_presence = {k: round((v / frame_total) * 100, 2) if frame_total > 0 else 0 for k, v in frame_detections.items()}

        return frame, presence_counter, total_detections, summary, frame_presence, annotations
    except Exception as e:
        logger.error(f"Error in run_detection_stream: {e}")
        return frame, presence_counter, total_detections, {}, {}, []

class VideoStreamConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("WebSocket connected")
        self.accept()
        self.presence_counter = defaultdict(int)
        self.total_detections = 0

    def disconnect(self, close_code):
        logger.info(f"WebSocket closed with code: {close_code}")

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                logger.info(f"Received data length: {len(text_data)} bytes")
                img_data = base64.b64decode(text_data)
                np_arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    logger.error("Failed to decode frame. Data length: %d bytes", len(img_data))
                    self.send(text_data=json.dumps({"error": "Failed to decode frame"}))
                    return

                start = time.time()
                annotated_frame, self.presence_counter, self.total_detections, summary, frame_presence, annotations = run_detection_stream(
                    frame, self.presence_counter, self.total_detections
                )
                logger.info(f"Inference time: {time.time() - start:.2f}s")

                ret, buffer = cv2.imencode(".jpg", annotated_frame)
                if not ret:
                    logger.error("Failed to encode frame")
                    self.send(text_data=json.dumps({"error": "Failed to encode frame"}))
                    return

                self.send(bytes_data=buffer.tobytes())

                stats = {"summary": summary, "frame": {"presence": frame_presence}, "annotations": annotations}
                logger.info(f"Sending stats: {stats}")
                self.send(text_data=json.dumps(stats))

            except base64.binascii.Error as e:
                logger.error(f"Base64 decode error: {e}")
                self.send(text_data=json.dumps({"error": "Invalid base64 data"}))
            except Exception as e:
                logger.error(f"Error processing frame: {e}")
                self.send(text_data=json.dumps({"error": str(e)}))