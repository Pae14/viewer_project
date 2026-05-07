# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas de negocio basadas en estudios estadísticos para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🏗️ Arquitectura del Sistema (File Structure)

El software sigue un diseño modular y desacoplado para garantizar la mantenibilidad y el rendimiento en tiempo real:

1.  **`main.py`**: **Orquestador Central**. Gestiona el ciclo de vida de la aplicación y la interfaz principal.
2.  **`models/`**: Carpeta que contiene los pesos de los modelos.
3.  **`workers.py`**: **Capa de Concurrencia e Integración**. Implementa el procesamiento multihilo y la comunicación con **ROS 2**.
4.  **`utils_vision.py`**: **Motor Analítico**. Contiene la lógica matemática para metrología y criterios de reparabilidad.
5.  **`ui_components.py`**: **Framework de UI**. Define la estética *Glassmorphism* y widgets personalizados.
6.  **`config.py`**: **Fuente de Verdad**. Centraliza constantes de calibración y rutas globales.

---

## 🛠️ Desglose Técnico Detallado (Core Modules)

### 📂 `utils_vision.py`: Metrología y Lógica de Reparabilidad
- **Metrología Dimensional**: Calcula el área real en **mm²**, perímetro, excentricidad y compactación.
- **Análisis de Textura (GLCM)**: Extrae descriptores de Energía y Entropía para caracterizar la severidad táctil.
- **Criterios de Reparabilidad Estrictos**: Evalúa si un defecto es **NON-REPAIRABLE** basándose en umbrales estadísticos (Medias/Máximos):
    - **Hole**: Área > 20.5 mm² o Perímetro > 18.6 mm.
    - **Crack**: Área > 6.67 mm², Perímetro > 14.13 mm, Excentricidad < 0.98 o Entropía > 9.28.
    - **Abrasion**: Energía < 0.12 o Entropía > 8.46.
    - **Friction**: Energía < 0.06 o Entropía > 8.75.

### 📂 `workers.py`: Procesamiento Asíncrono e Integración ROS 2
- **`GSThread`**: Gestiona el flujo de la cámara local (USB) en tiempo real.
- **`ROS2Thread`**: Implementa un nodo de **ROS 2** que se suscribe a topics de imagen (`sensor_msgs/Image`). 
    - Soporte para frecuencias bajas (optimizado para 1Hz).
    - Compatibilidad de QoS (**Best Effort**) para redes inestables o drones.
    - Conversión mediante `cv_bridge`.
- **`ModelLoader`**: Carga asíncrona de modelos PyTorch, Ultralytics y TensorFlow/Keras.

---

## 🤖 Integración con ROS 2 (Robot Operating System)

La aplicación actúa como un nodo nativo de ROS 2, permitiendo la integración con brazos robóticos gestionados por **MoveIt** y simulaciones en **Gazebo**.

- **Selección de Origen**: Permite conmutar dinámicamente entre cámara local y cualquier Topic de ROS 2 desde la interfaz.
- **Configuración Dinámica**: El nombre del topic se puede definir en tiempo de ejecución sin modificar el código.

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
    # Para soporte ROS 2:
    sudo apt install ros-<distro>-cv-bridge
    ```

---

## 📖 Guía de Uso

Para iniciar la aplicación, ejecuta el script principal:

```bash
python3 main.py
```

- **Modo Offline**: Navega por datasets locales, aplica filtros de clase y exporta informes técnicos.
- **Modo Online**: Inspección en tiempo real (USB o ROS 2) con visualización de métricas y estado de reparabilidad en vivo.
- **Atajos**: Usa `Flechas` para navegar y `E` para exportar capturas analizadas.

---

> **Nota Académica**: Este proyecto ha sido desarrollado como parte de un Trabajo de Fin de Grado (TFG), integrando ingeniería de software avanzada e inteligencia artificial para la industria 4.0.
