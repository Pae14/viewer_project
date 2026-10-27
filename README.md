# Tactile Defect Inspection System: Advanced Metrology & AI Analysis 

Este proyecto presenta una solución integral de **inspección visual-táctil** diseñada para la detección, segmentación y clasificación de defectos superficiales en entornos industriales. Utilizando el sensor biomimético **GelSight Mini**, la aplicación captura la topografía de las superficies permitiendo un análisis de metrología dimensional y textural de alta precisión.

La herramienta integra algoritmos de **Deep Learning** (YOLOv12, YOLOv26, RF-DETR, ResNet18 y CNN) con técnicas de **Visión Artificial clásica** (GLCM de Haralick) y reglas de negocio basadas en estudios estadísticos para determinar de forma autónoma la integridad de los componentes inspeccionados.

---

## Arquitectura del Sistema (File Structure)

El software sigue un diseño modular y desacoplado para garantizar la mantenibilidad y el rendimiento en tiempo real:

| Archivo / Carpeta | Función |
| --- | --- |
| **`main.py`** | **Orquestador Central**. Ciclo de vida de la aplicación, navegación entre pestañas (Offline/Online) y lógica general de la GUI en PyQt6. |
| **`workers.py`** | **Capa de Concurrencia e Integración**. Hilos de adquisición (`GSThread` para cámara local, `ROS2Thread` para topic ROS 2), cargadores asíncronos y ejecución de inferencia en GPU/CPU (`DEVICE`). |
| **`utils_vision.py`** | **Motor Analítico**. Métricas dimensionales (área, perímetro, excentricidad), descriptores texturales GLCM y reglas heurísticas de reparabilidad. |
| **`ui_components.py`** | **Framework de UI**. Estética *Glassmorphism*, paneles de visualización, botones animados y tarjetas de métricas. |
| **`config.py`** | **Fuente de Verdad**. Rutas de modelos, calibración GelSight (mm/px), umbrales de confianza, cámara e intervalo de inferencia. |
| **`export_metrics.py`** | **Herramienta de Reporting**. Script para procesamiento por lotes y generación de informes CSV estadísticos. |
| **`models/`** | Directorio donde residen los pesos y checkpoints entrenados. |
| **`exports/`** | Carpeta de salida para capturas de pantalla, reportes y métricas. |

---

## Concurrencia y Rendimiento (Multi-threading)

Para garantizar un rendimiento de grado industrial y una experiencia de usuario fluida, la aplicación implementa una arquitectura **multihilo asíncrona**:

- **UI Thread**: Renderizado de GUI y animaciones sin bloqueos.
- **Acquisition Thread (`ROS2Thread`)**: Nodo de ROS 2 dedicado a la escucha y conversión de imágenes mediante `cv_bridge`.
- **Inference Thread**: Ejecución paralela de modelos de IA, permitiendo el análisis de un frame mientras se recibe el siguiente.
- **Async Loaders**: Carga de modelos pesados en segundo plano durante el inicio de la app.

---

## Modelos y Gestión de Pesos (`models/`)

La aplicación requiere los siguientes pesos preentrenados dentro de la carpeta `models/`:

| Modelo / Tarea | Archivo en el Host | Tamaño aprox. | Descripción |
| --- | --- | --- | --- |
| **YOLO12n-seg** | `models/yolo12/best.pt` | ~5.8 MB | Segmentación de instancias ligera y de alta velocidad. |
| **YOLO26n-seg** | `models/yolo26/best.pt` | ~6.3 MB | Segmentación de instancias de defectología táctil. |
| **RF-DETR** | `models/checkpoint_best_ema.pt` | ~389 MB | Detector Transformer de alta precisión para defectos complejos. |
| **ResNet18** | `models/checkpoint_epoch_49.pth.tar` | ~129 MB | Clasificador convolucional multiclase de defectos superficiales. |
| **CNN Keras** | `models/best_model.weights.h5` | ~191 MB | Modelo convolucional alternativo entrenado en TensorFlow/Keras. |

### Comprobación de integridad de los pesos (Git LFS)

Si el proyecto ha sido clonado mediante Git, verifique que los archivos pesados sean archivos binarios reales y no punteros de texto generados por Git LFS:

```bash
# Comprobar si algún archivo contiene punteros LFS sin descargar:
grep -rn "version https://git-lfs" models/
```

- Si el comando anterior **no devuelve nada**, los pesos están completos y listos para usarse.
- Si devuelve coincidencias, ejecute:
  ```bash
  git lfs install
  git lfs pull
  ```
- O verifique los tamaños con:
  ```bash
  ls -lh models/ models/yolo12/ models/yolo26/
  ```

---

## Despliegue con Docker (Recomendado)

El despliegue con Docker aísla todas las dependencias del sistema operativo, proveyendo **ROS 2 Humble**, compatibilidad con **GPU NVIDIA (CUDA 12.1)** y las librerías gráficas de PyQt6.

### 1. Requisitos Previos en el Host

- **Docker Engine** y **Docker Compose v2** instalados.
- Para aceleración por hardware: **NVIDIA Driver** y **NVIDIA Container Toolkit** instalados.
- Sesión gráfica **X11** activa para desplegar la ventana de la aplicación.
- Habilitar permisos de visualización X11:
  ```bash
  xhost +si:localuser:root
  ```

### 2. Compilación de la Imagen

Desde la raíz del proyecto (`/home/aurova/Desktop/paula/viewer_project`):

```bash
docker compose build
```

### 3. Verificación de la GPU (NVIDIA CUDA)

Para comprobar que el contenedor detecta la tarjeta gráfica NVIDIA y la versión de PyTorch con CUDA 12.1:

```bash
docker compose run --rm viewer python3 -c "import torch; print('CUDA disponible:', torch.cuda.is_available(), '| Dispositivo:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```
*(Deberá mostrar `CUDA disponible: True | Dispositivo: NVIDIA GeForce RTX 3060`)*

### 4. Arranque de la Interfaz Gráfica

```bash
xhost +si:localuser:root
docker compose up --remove-orphans
```

> **Nota sobre dispositivos de cámara**: Si utiliza una cámara local USB física que esté en un puerto diferente de `/dev/video0`, puede indicarlo al arrancar:
> ```bash
> CAMERA_DEVICE=/dev/video2 docker compose up --remove-orphans
> ```

> **Nota para ordenadores sin tarjeta NVIDIA (Modo solo CPU)**:
> Si se ejecuta en un equipo que no dispone de GPU NVIDIA, comenta las líneas `deploy:` en `docker-compose.yml` para que Docker no solicite el driver de NVIDIA. La aplicación e inferencia funcionarán en CPU de forma automática.

---

## Conexión mediante Topic de ROS 2

El contenedor incluye el paquete **`vb_tactile_sensors`** precompilado en `/ros2_ws` y está configurado con `network_mode: host`, lo que permite que el middleware DDS de ROS 2 comparta el mismo espacio de red que el host y otros contenedores.

### 1. Iniciar el Publicador del Sensor (con Docker)

Desde una terminal en `/home/aurova/Desktop/paula/viewer_project`:

```bash
docker compose run --rm viewer ros2 run vb_tactile_sensors gs_image_depth
```

> **Nodos ejecutables disponibles en `vb_tactile_sensors`**:
> - `gs_image_depth`: Publica imagen (`/gs_mini_img`), imagen de profundidad (`/gs_depth_image`) y nube 3D (`/gs_mini_pcd`) del GelSight Mini con aceleración GPU (CUDA).
> - `gs_image`: Publica únicamente la imagen del GelSight Mini en `/gs_mini_img`.
> - `digit_image`: Publica la imagen del sensor DIGIT en `/digit_img`.
> - `digit_image_depth`: Publica imagen y mapa de profundidad para el sensor DIGIT.

### 2. Iniciar el Visor (GUI en otra terminal)

En una segunda terminal, arranca la interfaz gráfica:

```bash
cd /home/aurova/Desktop/paula/viewer_project
xhost +si:localuser:root
docker compose up --remove-orphans
```

### 3. Conectar la Interfaz al Topic

1. En la aplicación, navega a la pestaña **Online**.
2. En el menú desplegable **Source Selection**, selecciona **ROS 2 Topic**.
3. El campo **Topic Name** vendrá por defecto con `/gs_mini_img` (puedes cambiarlo si usas `/digit_img` o cualquier otro topic).
4. Pulsa **▶ Start**.
5. El indicador pasará a **⬤ Streaming** (verde) al recibir los frames y procesará la inferencia en tiempo real en la GPU NVIDIA.

### 4. Diagnóstico de Topics

Para inspeccionar o depurar los topics activos desde el entorno ROS 2:

```bash
# Listar los ejecutables del paquete sensor
docker compose run --rm viewer ros2 pkg executables vb_tactile_sensors

# Listar topics activos
docker compose run --rm viewer ros2 topic list

# Comprobar frecuencia de publicación (Hz)
docker compose run --rm viewer ros2 topic hz /gs_mini_img
```

---

## Ejecución Nativa en el Host (sin Docker)

Si dispone de un entorno Ubuntu con **ROS 2 Humble** y drivers de NVIDIA instalados directamente en el sistema:

1. **Crear y activar entorno virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar PyTorch con soporte CUDA**:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Instalar dependencias del proyecto**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar dependencias de ROS 2 para Python**:
   ```bash
   sudo apt update
   sudo apt install ros-humble-cv-bridge ros-humble-sensor-msgs ros-humble-std-msgs
   ```

5. **Compilar el paquete sensor en el host (opcional)**:
   ```bash
   colcon build --packages-select vb_tactile_sensors --symlink-install
   source install/setup.bash
   ```

6. **Iniciar la aplicación**:
   ```bash
   source /opt/ros/humble/setup.bash
   python3 main.py
   ```

---

## Lógica de Reparabilidad (Umbrales Estadísticos)

El sistema analiza en tiempo real las regiones segmentadas y evalúa de forma heurística si un defecto se clasifica como **REPAIRABLE** o **NON-REPAIRABLE**:

- **Material loss - Holes**: `Área > 20.5 mm²` o `Perímetro > 18.6 mm`.
- **Crack**: `Área > 6.67 mm²`, `Perímetro > 14.13 mm`, `Excentricidad < 0.98` o `Entropía > 9.28`.
- **Scratch - Abrasion**: `Energía GLCM < 0.12` o `Entropía GLCM > 8.46`.
- **Scratch - Friction**: `Energía GLCM < 0.06` o `Entropía GLCM > 8.75`.

Las métricas dimensionales y texturales calculadas se muestran en la tarjeta lateral derecha de la interfaz y se actualizan dinámicamente con cada frame analizado.
