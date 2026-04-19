# Defect Detector Viewer 🔍

Una aplicación avanzada de inspección visual basada en **PyQt6** para la detección y clasificación de defectos utilizando sensores **GelSight Mini** y modelos de Deep Learning de última generación.

## 🚀 Características

- **Detección Multi-Modelo**: Comparación en tiempo real entre YOLO12, YOLO26 y RF-DETR.
- **Modos de Operación**:
  - **Online**: Streaming en vivo desde la cámara GelSight con inferencia inmediata.
  - **Offline**: Navegación por datasets locales, filtrado por clases y exportación de resultados.
- **Análisis de Métricas**: Cálculo automático de área (mm²), perímetro, excentricidad y métricas de textura (GLCM) sobre las segmentaciones.
- **Clasificación**: Segundo nivel de análisis con ResNet18 y modelos CNN personalizados.
- **Interfaz Moderna**: Estética "Glassmorphism" con animaciones fluidas y paleta de colores pastel.

## 🛠️ Requisitos

Asegúrate de tener instaladas las siguientes dependencias:

```bash
pip install PyQt6 opencv-python numpy torch torchvision ultralytics scikit-image tensorflow
```

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada y gestión de la interfaz principal.
- `workers.py`: Lógica de hilos de fondo para carga de modelos e inferencia.
- `ui_components.py`: Widgets personalizados (botones, tarjetas, paneles de imagen).
- `config.py`: Configuración de rutas de modelos, colores y parámetros del sensor.
- `utils_vision.py`: Utilidades para dibujo de máscaras y cálculo de métricas físicas.

## 🔧 Configuración

Los modelos deben estar ubicados en el directorio superior (`..`) siguiendo las rutas en `config.py`:

- `checkpoint_best_ema.pt` (RF-DETR)
- `yolo12n_run2/weights/best.pt`
- `yolo26n_run5/weights/best.pt`
- `checkpoint_epoch_49.pth.tar` (ResNet18)
- `best_model.weights.h5` (CNN)

## 📖 Uso

Para iniciar la aplicación:

```bash
python3 main.py
```

### Atajos de Teclado (Modo Offline)
- `Flecha Derecha`: Siguiente imagen.
- `Flecha Izquierda`: Imagen anterior.
- `Ctrl + F`: Buscar por nombre de archivo.
- `E`: Exportar comparación actual a PNG.

---

