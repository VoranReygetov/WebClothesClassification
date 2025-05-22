from ultralytics import YOLO
import os
import uuid

model = YOLO("detection/best.pt") 

def run_detection(image_path):
    run_id = 'run_' + str(uuid.uuid4())[:8]
    results = model.predict(image_path, save=True, project='media/results', name=run_id)
    result_dir = results[0].save_dir
    result_image_name = os.path.basename(image_path).rsplit('.', 1)[0] + ".jpg"
    result_path = os.path.join(result_dir, result_image_name)

    class_names = []
    boxes = []

    for box in results[0].boxes:
        cls_index = int(box.cls[0])
        class_name = model.names[cls_index]
        class_names.append(class_name)
        boxes.append({
            "x": box.xywh[0][0].item(),
            "y": box.xywh[0][1].item(),
            "width": box.xywh[0][2].item(),
            "height": box.xywh[0][3].item(),
            "confidence": round(box.conf[0].item(), 3),
            "class": class_name
        })

    return result_path, class_names, boxes