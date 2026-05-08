# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas de negocio basadas en estudios estadísticos para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🤖 Funcionamiento del Nodo de ROS 2

La aplicación ha sido diseñada para actuar como un **nodo nativo de ROS 2**, permitiendo una integración fluida con brazos robóticos (MoveIt) y simuladores (Gazebo).

### 🛰️ Comunicación y Suscripción Dinámica
A diferencia de otros sistemas con configuraciones rígidas, esta interfaz permite una **sintonización dinámica de topics**:
- **Interfaz Flexible**: El usuario puede escribir el nombre del topic (ej. `/uav/camera/image_raw`) directamente en la interfaz. Al pulsar "Start", el sistema crea una suscripción en tiempo real a ese canal específico.
- **Protocolo de Comunicación**: El nodo actúa como un *Subscriber* que escucha mensajes de tipo `sensor_msgs/Image`.
- **Gestión de QoS (Best Effort)**: Para garantizar la visualización incluso en redes inalámbricas o con drones (donde puede haber pérdida de paquetes), se utiliza un perfil de **Calidad de Servicio (QoS) de tipo "Best Effort"**. Esto permite recibir datos de forma asíncrona y robusta.

### 🌉 El Puente: `cv_bridge`
La magia de la integración reside en la conversión de datos. ROS 2 transporta las imágenes en un formato binario optimizado para robótica. La interfaz utiliza **`cv_bridge`** para traducir estos mensajes a matrices de **OpenCV (NumPy arrays)** en tiempo real, permitiendo que los modelos de Inteligencia Artificial procesen la imagen como si viniera de una cámara local.

### ⏱️ Optimización para Bajas Frecuencias
El sistema está optimizado para trabajar con streams de baja frecuencia (como **1 Hz**). Gracias a su arquitectura multihilo, la interfaz no se bloquea esperando datos; en cuanto llega un frame, se procesa, se analiza su reparabilidad y se muestra en pantalla instantáneamente.

---

## 🏗️ Arquitectura del Sistema (File Structure)

1.  **`main.py`**: Orquestador Central y gestión de la interfaz PyQt6.
2.  **`workers.py`**: Capa de Concurrencia. Contiene la clase `ROS2Thread` que gestiona el ciclo de vida del nodo y la comunicación.
3.  **`utils_vision.py`**: Motor Analítico. Contiene la lógica de metrología y los umbrales de reparabilidad.
4.  **`config.py`**: Fuente de Verdad para calibración y rutas de modelos.

---

## 🛠️ Lógica de Reparabilidad (Umbrales Estadísticos)

El sistema evalúa automáticamente si un defecto es **NON-REPAIRABLE** basándose en las medias y máximos de los parámetros analizados:

- **Hole**: Área > 20.5 mm² o Perímetro > 18.6 mm.
- **Crack**: Área > 6.67 mm², Perímetro > 14.13 mm, Excentricidad < 0.98 o Entropía > 9.28.
- **Abrasion**: Energía < 0.12 o Entropía > 8.46.
- **Friction**: Energía < 0.06 o Entropía > 8.75.

---

## 🚀 Requisitos e Instalación

1.  **Instalar ROS 2** (Humble, Foxy o compatible).
2.  **Instalar dependencias de Python y ROS**:
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
