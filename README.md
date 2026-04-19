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

## 🛠️ Requisitos e Instalación

1. **Clonar el repositorio** (asegúrate de tener [Git LFS](https://git-lfs.com/) instalado para descargar los modelos):
   ```bash
   git clone https://github.com/Pae14/viewer_project.git
   cd viewer_project
   ```

2. **Instalar dependencias**:
   ```bash
   pip install PyQt6 opencv-python numpy torch torchvision ultralytics scikit-image tensorflow
   ```

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada principal.
- `models/`: Carpeta que contiene los pesos de los modelos (gestionada por Git LFS).
- `workers.py`: Lógica de hilos de fondo para carga e inferencia.
- `ui_components.py`: Widgets y diseño visual.
- `config.py`: Configuración global y rutas.
- `utils_vision.py`: Cálculos de visión computacional y métricas.

## 📖 Uso

Para iniciar la aplicación, ejecuta el script principal:

```bash
python3 main.py
```

### Funcionalidades clave:
- **Modo Offline**: Usa las flechas del teclado para navegar por las imágenes de la carpeta configurada en `config.py`.
- **Modo Online**: Selecciona la cámara y pulsa "Start" para ver la detección en directo.
- **Exportación**: Pulsa `E` o el botón de Snapshot para guardar los resultados analizados.

---
Hecho con ❤️ para la inspección de precisión.
