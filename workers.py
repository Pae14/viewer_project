import os
import time
import cv2
import numpy as np
import threading
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

import config
from config import *
from utils_vision import _draw_yolo, _draw_rfdetr

# Soporte para ROS 2
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
    from sensor_msgs.msg import Image as ROSImage
    from cv_bridge import CvBridge
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False

# https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
# https://docs.python.org/3/library/threading.html
class ModelLoader(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object, object)
    error    = pyqtSignal(str)

    def run(self):
        try:
            self.progress.emit("Loading YOLO12n-seg…")
            from ultralytics import YOLO
            y12 = YOLO(YOLO12_PATH)
            self.progress.emit("Loading YOLO26n-seg…")
            y26 = YOLO(YOLO26_PATH)
            self.progress.emit("Loading RF-DETR…")
            from rfdetr import RFDETRSegPreview
            rf = RFDETRSegPreview(pretrain_weights=RFDETR_PATH)
            rf.optimize_for_inference()
            self.finished.emit(y12, y26, rf)
        except Exception as ex:
            self.error.emit(str(ex))


class InferenceWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, models, ip, conf):
        super().__init__()
        self.models = models; self.ip = ip; self.conf = conf

    def run(self):
        y12, y26, rf = self.models
        bgr = cv2.imread(self.ip)
        if bgr is None: 
            self.finished.emit([None]*4); return
        orig = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        r12 = y12.predict(self.ip, conf=self.conf, imgsz=640, verbose=False)[0]
        r26 = y26.predict(self.ip, conf=self.conf, imgsz=640, verbose=False)[0]
        rrf = rf.predict(self.ip, threshold=self.conf, resolution=672)

        orig_tup = (orig, "", (155, 160, 165), None)
        r12_tup  = _draw_yolo(bgr, r12, list(y12.names.values()))
        r26_tup  = _draw_yolo(bgr, r26, list(y26.names.values()))
        rrf_tup  = _draw_rfdetr(bgr, rrf)

        self.finished.emit([orig_tup, r12_tup, r26_tup, rrf_tup])


class GSThread(QThread):
    frame_ready  = pyqtSignal(np.ndarray)
    result_ready = pyqtSignal(np.ndarray, str, tuple, object)
    det_classes  = pyqtSignal(set)
    status       = pyqtSignal(str)

    def __init__(self, models, conf, midx=0, cam=GELSIGHT_CAM):
        super().__init__()
        self.models = models; self.conf = conf; self.midx = midx; self.cam = cam
        self._run = False; self._mx = QMutex(); self._nc = None; self._nm = None
        self._is_inferring = False

    def set_conf(self, v):
        with QMutexLocker(self._mx): self._nc = v
    def set_model(self, i):
        with QMutexLocker(self._mx): self._nm = i
    def stop(self): 
        self._run = False

    def _do_inference(self, frm, midx, conf):
        y12, y26, rf = self.models
        try:
            tmp = "/tmp/_gs.png"; cv2.imwrite(tmp, frm); det = set()
            if midx == 0:
                r = y12.predict(tmp, conf=conf, imgsz=640, verbose=False)[0]
                if r.boxes is not None: det = {int(c) for c in r.boxes.cls.cpu().numpy()}
                drw, txt, col, mtr = _draw_yolo(frm, r, list(y12.names.values()))
            elif midx == 1:
                r = y26.predict(tmp, conf=conf, imgsz=640, verbose=False)[0]
                if r.boxes is not None: det = {int(c) for c in r.boxes.cls.cpu().numpy()}
                drw, txt, col, mtr = _draw_yolo(frm, r, list(y26.names.values()))
            else:
                r = rf.predict(tmp, threshold=conf, resolution=672)
                if r is not None and len(r) > 0: det = {int(c) for c in r.class_id}
                drw, txt, col, mtr = _draw_rfdetr(frm, r)
            self.result_ready.emit(drw, txt, col, mtr)
            self.det_classes.emit(det)
        except Exception as ex:
            self.status.emit(f"Inference error: {ex}")
        finally:
            self._is_inferring = False

    def run(self):
        self._run = True
        cap = cv2.VideoCapture(self.cam)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not cap.isOpened(): 
            self.status.emit(f"ERROR: Cannot open cam {self.cam}"); return
            
        W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.status.emit(f"GelSight connected — {W}×{H}px")
        fi = 1/STREAM_FPS
        lft = lii = 0.0
        
        while self._run:
            ret, frm = cap.read()
            if not ret: 
                time.sleep(0.05); continue
            now = time.time()
            
            with QMutexLocker(self._mx):
                if self._nc is not None: self.conf = self._nc; self._nc = None
                if self._nm is not None: self.midx = self._nm; self._nm = None
                
            if now - lft >= fi:
                self.frame_ready.emit(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB).copy())
                lft = now
                
            if now - lii >= config.INFER_INTERVAL and not self._is_inferring:
                lii = now
                self._is_inferring = True
                threading.Thread(target=self._do_inference, args=(frm.copy(), self.midx, self.conf), daemon=True).start()
                
        cap.release()
        self.status.emit("Stream stopped.")


class ROS2Thread(QThread):
    frame_ready  = pyqtSignal(np.ndarray)
    result_ready = pyqtSignal(np.ndarray, str, tuple, object)
    det_classes  = pyqtSignal(set)
    status       = pyqtSignal(str)

    def __init__(self, models, conf, midx=0, topic='/camera/image_raw'):
        super().__init__()
        self.models = models; self.conf = conf; self.midx = midx; self.topic = topic
        self._run = False; self._mx = QMutex(); self._nc = None; self._nm = None
        self._is_inferring = False
        self._bridge = None
        if ROS2_AVAILABLE:
            self._bridge = CvBridge()

    def set_conf(self, v):
        with QMutexLocker(self._mx): self._nc = v
    def set_model(self, i):
        with QMutexLocker(self._mx): self._nm = i
    def stop(self): 
        self._run = False

    def _do_inference(self, frm, midx, conf):
        y12, y26, rf = self.models
        try:
            tmp = "/tmp/_ros2_gs.png"; cv2.imwrite(tmp, frm); det = set()
            if midx == 0:
                r = y12.predict(tmp, conf=conf, imgsz=640, verbose=False)[0]
                if r.boxes is not None: det = {int(c) for c in r.boxes.cls.cpu().numpy()}
                drw, txt, col, mtr = _draw_yolo(frm, r, list(y12.names.values()))
            elif midx == 1:
                r = y26.predict(tmp, conf=conf, imgsz=640, verbose=False)[0]
                if r.boxes is not None: det = {int(c) for c in r.boxes.cls.cpu().numpy()}
                drw, txt, col, mtr = _draw_yolo(frm, r, list(y26.names.values()))
            else:
                r = rf.predict(tmp, threshold=conf, resolution=672)
                if r is not None and len(r) > 0: det = {int(c) for c in r.class_id}
                drw, txt, col, mtr = _draw_rfdetr(frm, r)
            self.result_ready.emit(drw, txt, col, mtr)
            self.det_classes.emit(det)
        except Exception as ex:
            self.status.emit(f"Inference error: {ex}")
        finally:
            self._is_inferring = False

    def run(self):
        if not ROS2_AVAILABLE:
            self.status.emit("ERROR: ROS 2 (rclpy) not found.")
            return

        try:
            if not rclpy.ok():
                rclpy.init()
            node = Node('defect_detector_ui')
            self.status.emit(f"ROS 2 Node started — Subscribing to {self.topic}")
            
            def image_callback(msg):
                if not self._run: return
                
                try:
                    # 1. Convertimos la imagen de ROS a OpenCV
                    frm = self._bridge.imgmsg_to_cv2(msg, 'bgr8')
                    
                    # 2. Sincronizamos configuración de la interfaz
                    with QMutexLocker(self._mx):
                        if self._nc is not None: self.conf = self._nc; self._nc = None
                        if self._nm is not None: self.midx = self._nm; self._nm = None

                    # 3. ENVIAMOS A PANTALLA INMEDIATAMENTE (sin esperar a 30fps)
                    self.frame_ready.emit(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB).copy())
                        
                    # 4. Lanzamos la IA si no está ocupada con otro frame
                    if not self._is_inferring:
                        self._is_inferring = True
                        threading.Thread(target=self._do_inference, args=(frm.copy(), self.midx, self.conf), daemon=True).start()
                except Exception as e:
                    self.status.emit(f"ROS Callback error: {e}")

            qos_profile = QoSProfile(
                reliability=ReliabilityPolicy.BEST_EFFORT,
                history=HistoryPolicy.KEEP_LAST,
                depth=1
            )
            node.create_subscription(ROSImage, self.topic, image_callback, qos_profile=qos_profile)
            self._run = True
            
            while self._run:
                rclpy.spin_once(node, timeout_sec=0.1)
                
            node.destroy_node()
            self.status.emit("ROS 2 Subscription stopped.")
        except Exception as ex:
            self.status.emit(f"ROS 2 Error: {ex}")


class ClassifyWorker(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, rn, cnn, img_path):
        super().__init__(); self._rn = rn; self._cnn = cnn; self._p = img_path
    
    def _run_resnet(self, bgr):
        try:
            import torch
            rgb  = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype("float32") / 255.0
            img  = cv2.resize(rgb, (160, 128))
            x    = torch.from_numpy(img).permute(2,0,1).unsqueeze(0)
            with torch.no_grad(): probs = torch.softmax(self._rn(x)[0], 0).numpy()
            idx = int(probs.argmax())
            return RESNET_CLASS_NAMES.get(idx, str(idx)), float(probs[idx])
        except Exception: return "Error", 0.0
        
    def _run_cnn(self, bgr):
        try:
            import tensorflow as tf
            rgb   = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); img = cv2.resize(rgb, (160, 128)).astype("float32") / 255.0
            probs = self._cnn.predict(img[np.newaxis], verbose=0)[0]
            idx   = int(probs.argmax())
            return CLASS_NAMES.get(idx, str(idx)), float(probs[idx])
        except Exception: return "Error", 0.0
        
    def run(self):
        bgr = cv2.imread(self._p)
        if bgr is None: 
            self.finished.emit({"resnet":("—",0.), "cnn":("—",0.)}); return
        res = {
            "resnet": self._run_resnet(bgr) if self._rn  else ("Not loaded", 0.),
            "cnn":    self._run_cnn(bgr)    if self._cnn else ("Not loaded", 0.),
        }
        self.finished.emit(res)


class ClassifyLoader(QThread):
    progress = pyqtSignal(str); finished = pyqtSignal(object, object); error = pyqtSignal(str)
    
    def run(self):
        rn = cnn = None
        
        try:
            import torch, torchvision.models as tvm, torch.nn as nn
            self.progress.emit("Loading ResNet18…")
            rn = tvm.resnet18(weights=None)
            rn.fc = nn.Linear(rn.fc.in_features, 7)
            ck = torch.load(RESNET_PATH, map_location="cpu", weights_only=False)
            state_dict = ck.get("state_dict", ck)
            clean_dict = {k.replace("model.", "") if k.startswith("model.") else k: v for k, v in state_dict.items()}
            rn.load_state_dict(clean_dict, strict=True)
            rn.eval()
        except Exception as ex: 
            self.progress.emit(f"ResNet load error: {ex}")
            
        try:
            import tensorflow as tf
            self.progress.emit("Loading CNN…")
            try:
                cnn = tf.keras.models.load_model(CNN_CLS_PATH, compile=False)
            except Exception:
                cnn = tf.keras.models.Sequential([
                    tf.keras.layers.Input(shape=(128,160,3)),
                    tf.keras.layers.Conv2D(32,(5,5),activation='relu',input_shape=(128,160,3)), tf.keras.layers.MaxPooling2D((2,2)),
                    tf.keras.layers.Conv2D(64,(3,3),activation='relu'), tf.keras.layers.MaxPooling2D((2,2)),
                    tf.keras.layers.Conv2D(128,(3,3),activation='relu'), tf.keras.layers.Flatten(),
                    tf.keras.layers.Dense(128,activation='relu'), tf.keras.layers.Dropout(0.5), tf.keras.layers.Dense(5,activation='softmax')
                ])
                cnn.build((None, 128, 160, 3))
                cnn.load_weights(CNN_CLS_PATH)
        except Exception as ex: 
            self.progress.emit(f"CNN load error: {ex}")
            
        self.finished.emit(rn, cnn)