@echo off
cd /d "%~dp0\.."
".venv-train\Scripts\yolo.exe" detect train model=backend/models/best.pt data=dataset/data.yaml imgsz=640 batch=16 epochs=100 patience=30 name=topi_dasi_full_640
