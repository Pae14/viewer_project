# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas heurísticas de negocio para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🏗️ Arquitectura del Sistema (File Structure)

El software sigue un diseño modular y desacoplado para garantizar la mantenibilidad y el rendimiento en tiempo real:

1.  **`main.py`**: **Orquestador Central**. Gestiona el ciclo de vida de la aplicación y la interfaz principal.
2.  **`models/`**: Carpeta que contiene los pesos de los modelos (gestionada por **Git LFS**).
3.  **`workers.py`**: **Capa de Concurrencia**. Implementa el procesamiento multihilo (`QThread`) para la ejecución asíncrona de la IA.
4.  **`utils_vision.py`**: **Motor Analítico**. Contiene la lógica matemática para metrología y descriptores GLCM.
5.  **`ui_components.py`**: **Framework de UI**. Define la estética *Glassmorphism* y widgets personalizados.
6.  **`config.py`**: **Fuente de Verdad**. Centraliza constantes de calibración y rutas globales.

---

## 🛠️ Desglose Técnico Detallado (Core Modules)

### 📂 `config.py`: Parametrización y Calibración Metrológica
- **Calibración Física**: Define `GS_FOV_W_MM` y `GS_FOV_H_MM`, transformando píxeles en unidades métricas reales.
- **Gestión de Rutas**: Centraliza la localización de los pesos de los 5 modelos integrados.

### 📂 `utils_vision.py`: Metrología y Descriptores de Haralick
- **Metrología Dimensional**: Calcula el área real en **mm²** y el perímetro de cada defecto.
- **Análisis de Textura (GLCM)**: Extrae descriptores de Energía, Homogeneidad y Entropía para caracterizar la severidad táctil.
- **Reglas de Negocio**: Evalúa heurísticamente si un defecto es reparable basándose en su morfología y textura.

### 📂 `workers.py`: Procesamiento Asíncrono
- **`GSThread`**: Gestiona el flujo de la cámara en tiempo real con buffer optimizado para evitar latencia.
- **`ModelLoader`**: Carga asíncrona de modelos PyTorch, Ultralytics y TensorFlow/Keras.
- **`InferenceWorker`**: Ejecuta la segmentación paralela sin bloquear el hilo principal de la UI.

### 📂 `ui_components.py`: Interfaz de Alta Fidelidad
- **Glassmorphism**: Renderizado avanzado con `QPainter` para efectos de transparencia y profundidad.
- **Animaciones**: Uso de `QPropertyAnimation` para una experiencia de usuario fluida y profesional.

---

## 🚀 Requisitos e Instalación

1.  **Clonar el repositorio** (necesario [Git LFS](https://git-lfs.com/) para descargar los pesos):
    ```bash
    git clone https://github.com/Pae14/viewer_project.git
    cd viewer_project
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install PyQt6 opencv-python numpy torch torchvision ultralytics scikit-image tensorflow
    ```

---

## 📖 Guía de Uso

Para iniciar la aplicación, ejecuta el script principal:

```bash
python3 main.py
```

- **Modo Offline**: Navega por datasets locales, aplica filtros de clase y exporta informes técnicos.
- **Modo Online**: Inspección en tiempo real desde el sensor GelSight Mini con visualización de métricas en vivo.
- **Atajos**: Usa `Flechas` para navegar y `E` para exportar capturas analizadas.

---

> **Nota Académica**: Este proyecto ha sido desarrollado como parte de un Trabajo de Fin de Grado (TFG), integrando ingeniería de software avanzada e inteligencia artificial para la industria 4.0.
