# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas de negocio basadas en estudios estadísticos para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🏗️ Arquitectura del Sistema (File Structure)

El software sigue un diseño modular y desacoplado para garantizar la mantenibilidad y el rendimiento en tiempo real:

1.  **`main.py`**: **Orquestador Central**. Gestiona el ciclo de vida de la aplicación, la navegación entre pestañas (Offline/Online) y la interfaz principal PyQt6.
2.  **`workers.py`**: **Capa de Concurrencia e Integración**. Implementa el procesamiento multihilo (`QThread`) y el nodo de **ROS 2** para la suscripción a sensores externos.
3.  **`utils_vision.py`**: **Motor Analítico**. Contiene los algoritmos de metrología, los descriptores de textura GLCM y la lógica de decisión de reparabilidad.
4.  **`ui_components.py`**: **Framework de UI**. Define la estética *Glassmorphism*, los widgets personalizados y el sistema de animaciones.
5.  **`config.py`**: **Fuente de Verdad**. Centraliza constantes de calibración (mm/px), rutas globales de modelos y parámetros de red.
6.  **`export_metrics.py`**: **Herramienta de Reporting**. Script para el procesamiento por lotes y generación de informes CSV estadísticos.

---

## 🏗️ Concurrencia y Rendimiento (Multi-threading)

Para garantizar un rendimiento de grado industrial y una experiencia de usuario fluida, la aplicación implementa una arquitectura **multihilo asíncrona**:

- **UI Thread**: Renderizado de GUI y animaciones sin bloqueos.
- **Acquisition Thread (`ROS2Thread`)**: Nodo de ROS 2 dedicado a la escucha y conversión de imágenes mediante `cv_bridge`.
- **Inference Thread**: Ejecución paralela de modelos de IA, permitiendo el análisis de un frame mientras se recibe el siguiente.
- **Async Loaders**: Carga de modelos pesados en segundo plano durante el inicio de la app.

---

## 🤖 Integración con ROS 2 (Robot Operating System)

La aplicación actúa como un **nodo nativo de ROS 2**, ideal para entornos con brazos robóticos (MoveIt) y simuladores (Gazebo).

- **Suscripción Dinámica**: Configuración del topic en tiempo real desde la interfaz gráfica.
- **Gestión de QoS (Best Effort)**: Optimizado para telemetría robótica y drones, garantizando compatibilidad y baja latencia.
- **Robustez**: Soporte nativo para frecuencias de imagen bajas (hasta **1 Hz**) sin afectar la estabilidad de la UI.

---

## 🛠️ Lógica de Reparabilidad (Umbrales Estadísticos)

El sistema evalúa automáticamente si un defecto es **NON-REPAIRABLE** basándose en métricas dimensionales y texturales:

- **Hole**: Área > 20.5 mm² o Perímetro > 18.6 mm.
- **Crack**: Área > 6.67 mm², Perímetro > 14.13 mm, Excentricidad < 0.98 o Entropía > 9.28.
- **Abrasion**: Energía < 0.12 o Entropía > 8.46.
- **Friction**: Energía < 0.06 o Entropía > 8.75.

---

## 🚀 Requisitos e Instalación

1.  **Instalar ROS 2** (Humble, Foxy o compatible).
2.  **Instalar dependencias**:
    ```bash
    pip install PyQt6 opencv-python numpy torch ultralytics scikit-image tensorflow
    sudo apt install ros-${ROS_DISTRO}-cv-bridge
    ```
3.  **Ejecución**:
    ```bash
    source /opt/ros/${ROS_DISTRO}/setup.bash
    python3 main.py
    ```

---

> **Nota Académica**: Este proyecto ha sido desarrollado como parte de un Trabajo de Fin de Grado (TFG), integrando ingeniería de software avanzada e inteligencia artificial para la industria 4.0.
