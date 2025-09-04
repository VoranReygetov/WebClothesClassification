from ultralytics import YOLO

# Завантажуємо треновану модель
model = YOLO("best.pt")

# Експортуємо в onnx з потрібним розміром інпуту
model.export(format="onnx", opset=12, imgsz=640, simplify=True)