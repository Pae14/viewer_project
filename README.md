# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas heurísticas de negocio para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🏗️ Arquitectura del Sistema (File Structure)

El software sigue un diseño modular y desacoplado para garantizar la mantenibilidad y el rendimiento en tiempo real:

1.  **`main.py`**: **Orquestador Central**. Gestiona el ciclo de vida de la aplicación, la navegación y la comunicación entre módulos mediante el patrón *Signals & Slots*.
2.  **`workers.py`**: **Capa de Concurrencia**. Implementa el procesamiento multihilo (`QThread`) para la ejecución asíncrona de modelos de IA y la gestión del flujo de cámara.
3.  **`utils_vision.py`**: **Motor Analítico**. Contiene la lógica matemática para metrología, extracción de características texturales y procesado de imágenes.
4.  **`ui_components.py`**: **Framework de UI**. Define la identidad visual avanzada (*Glassmorphism*) y widgets personalizados con renderizado optimizado.
5.  **`config.py`**: **Fuente de Verdad**. Centraliza constantes de calibración, rutas de modelos, paletas estéticas y parámetros globales.

---

## 🛠️ Desglose Técnico Detallado (Core Modules)

### 📂 `config.py`: Parametrización y Calibración Metrológica
Este módulo actúa como el archivo de configuración global. Su importancia reside en la **estandarización de la salida**:
- **Calibración Física**: Define `GS_FOV_W_MM` (14.6 mm) y `GS_FOV_H_MM` (10.9 mm), permitiendo transformar dimensiones de píxeles en unidades métricas reales.
- **Diccionarios de Clases**: Mapea identificadores de red a nombres legibles (Abrasion, Crack, Holes, etc.) y asigna una identidad cromática única (`CLASS_COLORS_RGB`) para la visualización de máscaras.
- **Gestión de Rutas**: Centraliza la localización de los pesos de los 5 modelos integrados, facilitando el despliegue en diferentes entornos.

### 📂 `utils_vision.py`: Metrología y Descriptores de Haralick
Es el núcleo científico del proyecto. La función crítica `_compute_metrics` realiza un análisis exhaustivo de cada defecto segmentado:
- **Metrología Dimensional**: Calcula el área real en **mm²** y el perímetro, permitiendo cuantificar la severidad del defecto más allá de la simple detección visual.
- **Análisis de Textura (GLCM)**: Utiliza la *Gray-Level Co-occurrence Matrix* para extraer descriptores espaciales:
  - **Energía y Homogeneidad**: Miden la uniformidad de la superficie del defecto.
  - **Entropía**: Cuantifica el desorden o complejidad de la textura táctil.
- **Lógica Heurística de Reparabilidad**: Implementa las funciones de dibujo y análisis que aplican reglas de negocio basadas en el área, la excentricidad (forma del defecto) y los valores GLCM para clasificar automáticamente si una prenda es **"REPARABLE"** o **"NON-REPAIRABLE"**.

### 📂 `workers.py`: Procesamiento Asíncrono y Gestión de Modelos
Para mantener una interfaz fluida (30+ FPS), este script traslada la carga computacional a hilos secundarios:
- **`GSThread`**: Gestiona el buffer de la cámara GelSight. Implementa un control de intervalos de inferencia para evitar el *lag* acumulativo en el procesamiento de vídeo en directo.
- **`ModelLoader` & `ClassifyLoader`**: Cargadores especializados que gestionan el estado de carga de redes pesadas. Implementan soluciones para la carga segura de pesos en **PyTorch** (`weights_only=False`) y la reconstrucción de arquitecturas en **Keras/TensorFlow**.
- **`InferenceWorker`**: Ejecuta la lógica de segmentación paralela para los tres modelos principales, permitiendo al usuario comparar el desempeño de YOLOv12, YOLOv26 y RF-DETR de forma simultánea.

### 📂 `ui_components.py`: Interfaz de Usuario de Alta Fidelidad
Este módulo eleva la experiencia de usuario mediante técnicas de diseño modernas:
- **Glassmorphism & QPainter**: Utiliza `QPainter` y gradientes lineales/radiales para crear tarjetas con efectos de transparencia y desenfoque, alineándose con estándares de software industrial premium.
- **Animaciones Dinámicas**: Implementa `QPropertyAnimation` para transiciones de opacidad y `QTimer` para el movimiento fluido de los orbes del fondo animado.
- **Optimización de Renderizado**: Gestión eficiente de `QPixmap` para el dibujo de máscaras de segmentación sobre los frames de cámara, evitando parpadeos de memoria (*flickering*) mediante actualizaciones dobles de buffer.

### 📂 `main.py`: Gestión de Estado y Event Loop
El punto de entrada que une la lógica con la presentación:
- **MainWindow**: Actúa como el controlador principal. Implementa el diseño de dos pestañas:
  - **OfflineTab**: Para la investigación forense de datasets pre-adquiridos, filtrado por clases y exportación de informes técnicos.
  - **OnlineTab**: Para la inspección en línea, controlando el encendido/apagado del sensor y la visualización de métricas en vivo.
- **Signals & Slots**: Utiliza el sistema de comunicación de Qt para enviar métricas de los hilos de visión (`workers`) a las barras de progreso y etiquetas de la UI, garantizando que el hilo principal nunca se bloquee.

---

## 🚀 Tecnologías Utilizadas

- **Interfaz Gráfica**: `PyQt6` (Core framework, QPainter, Animations).
- **Visión Artificial**: `OpenCV` (Procesamiento de imagen), `Scikit-Image` (GLCM, RegionProps).
- **Inteligencia Artificial**:
  - `PyTorch` & `Torchvision` (Arquitectura ResNet18 y RF-DETR).
  - `Ultralytics` (Modelos YOLOv12-seg y YOLOv26-seg).
  - `TensorFlow / Keras` (Clasificador CNN personalizado).
- **Cómputo Numérico**: `NumPy` (Manipulación de arrays de máscaras).

---

> **Nota Académica**: Este proyecto ha sido desarrollado como parte de un Trabajo de Fin de Grado, integrando conceptos de ingeniería de software, inteligencia artificial y metrología industrial en una única herramienta de nivel profesional.
