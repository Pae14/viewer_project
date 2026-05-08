# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 🔍🤖

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación trasciende la visión convencional al capturar la topografía microscópica de las superficies, permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** de última generación (YOLOv12, YOLOv26, RF-DETR) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas de negocio basadas en estudios estadísticos para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## 🏗️ Arquitectura de Software y Concurrencia (Multi-threading)

Para garantizar un rendimiento de grado industrial y una experiencia de usuario fluida, la aplicación implementa una arquitectura **multihilo asíncrona** basada en `QThread` y `threading`:

1.  **Hilo de Interfaz de Usuario (UI Thread)**: Gestiona el renderizado de la GUI, las animaciones *Glassmorphism* y la interacción con el usuario. Al estar desacoplado del procesamiento, la interfaz nunca se "congela".
2.  **Hilo de Adquisición y Comunicaciones (`GSThread` / `ROS2Thread`)**: Gestiona la entrada de datos en tiempo real. En el modo ROS 2, este hilo mantiene la suscripción activa y realiza la conversión de mensajes mediante `cv_bridge` de forma independiente.
3.  **Hilo de Inferencia de IA (Inference Thread)**: Los modelos YOLOv12/26 y RF-DETR se ejecutan en hilos paralelos de corta duración. Esto permite que el sistema analice un frame mientras el hilo de comunicaciones ya está recibiendo el siguiente, maximizando el rendimiento del hardware.
4.  **Hilos de Carga Asíncrona (`ModelLoaders`)**: Permiten que la aplicación arranque instantáneamente mientras los modelos de IA (que pueden pesar cientos de MB) se cargan en segundo plano en la memoria de la GPU/CPU.

---

## 🤖 Funcionamiento del Nodo de ROS 2

La aplicación actúa como un **nodo nativo de ROS 2**, permitiendo una integración fluida con brazos robóticos (MoveIt) y simuladores (Gazebo).

### 🛰️ Comunicación y Suscripción Dinámica
- **Interfaz Flexible**: El usuario puede definir el nombre del topic (ej. `/uav/camera/image_raw`) en tiempo real.
- **Protocolo de Comunicación**: Suscripción a mensajes `sensor_msgs/Image`.
- **Gestión de QoS (Best Effort)**: Utiliza un perfil de **Calidad de Servicio (QoS)** optimizado para telemetría robótica, priorizando los datos más recientes y garantizando la compatibilidad con sensores en redes inalámbricas.
- **Optimización de Frecuencia**: Arquitectura adaptativa capaz de procesar flujos desde **1 Hz** hasta **30 Hz** sin pérdida de frames ni latencia acumulada.

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
