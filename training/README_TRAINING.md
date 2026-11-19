# Training YOLO untuk Topi dan Dasi

Letakkan dataset hasil labeling ke folder `dataset/`.

Struktur dataset:

```text
dataset/
├── images/train
├── images/valid
├── images/test
├── labels/train
├── labels/valid
├── labels/test
└── data.yaml
```

Contoh perintah training YOLOv5:

```bash
python train.py --img 640 --batch 16 --epochs 100 --data dataset/data.yaml --weights yolov5s.pt --name topi_dasi
```

Setelah selesai, ambil file:

```text
runs/train/topi_dasi/weights/best.pt
```

Lalu letakkan ke:

```text
backend/models/best.pt
```
