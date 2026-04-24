import cv2
import math
import numpy as np
from config import *

# https://scikit-image.org/docs/stable/api/skimage.measure.html
# https://scikit-image.org/docs/stable/api/skimage.feature.html

def _compute_metrics(mask_bool, gray_img):
    h, w = mask_bool.shape
    mm2_per_pixel = (GS_FOV_W_MM * GS_FOV_H_MM) / (w * h)
    mm_per_pixel  = math.sqrt(mm2_per_pixel)

    area_px   = float(np.sum(mask_bool))
    area_mm2  = area_px * mm2_per_pixel

    eccentricity  = 0.0
    perimeter_mm  = 0.0
    compactation  = 0.0
    
    try:
        from skimage.measure import regionprops, label as sklabel
        lbl_img = sklabel(mask_bool.astype(np.uint8))
        props_list = regionprops(lbl_img)
        if props_list:
            props = max(props_list, key=lambda p: p.area)
            eccentricity = float(props.eccentricity)
            perimeter_mm = float(props.perimeter) * mm_per_pixel
            if props.perimeter > 0:
                compactation = (4 * math.pi * props.area) / (props.perimeter ** 2)
    except Exception:
        contours, _ = cv2.findContours(mask_bool.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            perim_px = sum(cv2.arcLength(c, True) for c in contours)
            perimeter_mm = perim_px * mm_per_pixel
            if perim_px > 0:
                compactation = (4 * math.pi * area_px) / (perim_px ** 2)

    glcm_homogeneity = 0.0
    glcm_energy      = 0.0
    glcm_entropy     = 0.0
    
    try:
        from skimage.feature import graycomatrix, graycoprops
        ys, xs = np.where(mask_bool)
        if len(xs) >= 4:
            y1c, y2c = ys.min(), ys.max() + 1
            x1c, x2c = xs.min(), xs.max() + 1
            roi_gray = gray_img[y1c:y2c, x1c:x2c]
            roi_mask = mask_bool[y1c:y2c, x1c:x2c]
            roi_masked = roi_gray.copy()
            roi_masked[~roi_mask] = 0
            roi_small = roi_masked
            maxd = 128
            rh, rw = roi_masked.shape

            if max(rh, rw) > maxd:
                scale = maxd / max(rh, rw)
                roi_small = cv2.resize(roi_masked, (max(1, int(rw * scale)), max(1, int(rh * scale))), interpolation=cv2.INTER_AREA)
            
            glcm = graycomatrix(roi_small, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                                levels=256, symmetric=True, normed=True)
            glcm_homogeneity = float(np.mean(graycoprops(glcm, 'homogeneity')))
            glcm_energy      = float(np.mean(graycoprops(glcm, 'energy')))
            eps = 1e-10
            p_norm = glcm / (glcm.sum(axis=(0, 1), keepdims=True) + eps)
            glcm_entropy = float(-np.mean(np.sum(p_norm * np.log2(p_norm + eps), axis=(0, 1))))
    except Exception:
        pass

    return {
        "area_mm2":         area_mm2,
        "perimeter_mm":     perimeter_mm,
        "eccentricity":     eccentricity,
        "compactation":     compactation,
        "glcm_homogeneity": glcm_homogeneity,
        "glcm_energy":      glcm_energy,
        "glcm_entropy":     glcm_entropy,
    }

def _get_status(has_defect, is_repairable):
    if not has_defect:
        return "NO DEFECTS", (155, 160, 165)
    if is_repairable:
        return "REPAIRABLE", (78, 170, 114)
    return "NON-REPAIRABLE", (217, 79, 79)

def _draw_yolo(bgr, result, names):
    img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).copy()
    h, w = img.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if result.masks is None:
        return img, "NO DEFECTS", (155, 160, 165), None

    is_repairable = True
    has_defect = False
    
    n_list, c_list = [], []
    area_list, perim_list, ecc_list, comp_list = [], [], [], []
    homo_list, ener_list, ent_list = [], [], []
    first_color = (180, 180, 180)

    for cid in np.unique(result.boxes.cls.cpu().numpy()):
        
        if int(cid) == 4:
            continue
        
        idxs = np.where(result.boxes.cls.cpu().numpy() == cid)[0]
        idxs = idxs[np.argsort(-result.boxes.conf.cpu().numpy()[idxs])]
        acc = np.zeros((h, w), dtype=bool)
        
        for j in idxs[:2]:
            mn = cv2.resize(result.masks.data[j].cpu().numpy(), (w, h))
            mb = mn > 0.5
            metrics = _compute_metrics(mb, gray)
            
            area_mm2 = metrics["area_mm2"]
            ecc = metrics["eccentricity"]
            energia = metrics["glcm_energy"]
            entropia = metrics["glcm_entropy"]

            has_defect = True
            defect_repairable = True
            
            if int(cid) == 3:
                defect_repairable = False
            elif int(cid) == 1:
                if ecc > 0.85 and area_mm2 > 5.0:
                    defect_repairable = False
            elif int(cid) in [0, 2]:
                if area_mm2 > 30.0 or energia < 0.05 or entropia > 7.0:
                    defect_repairable = False

            if not defect_repairable:
                is_repairable = False

            if acc.sum() > 0 and (acc & mb).sum() / max((acc | mb).sum(), 1) > 0.7:
                continue
            acc |= mb
            
            col = CLASS_COLORS_RGB.get(int(cid), (180, 180, 180))
            if not n_list: first_color = col
            
            ov = np.zeros_like(img)
            ov[acc] = col
            img = cv2.addWeighted(img, 1.0, ov, 0.40, 0)
            ys, xs = np.where(acc)
            if len(xs):
                x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
                cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)

                lbl_name = CLASS_NAMES_SHORT.get(int(cid), names[int(cid)]).upper()
                lbl_conf = int(float(result.boxes.conf[j]) * 100)
                
                n_list.append(lbl_name)
                c_list.append(f"{lbl_conf}%")
                area_list.append(f"{area_mm2:.1f}")
                perim_list.append(f"{metrics['perimeter_mm']:.1f}")
                ecc_list.append(f"{ecc:.2f}")
                comp_list.append(f"{metrics['compactation']:.2f}")
                homo_list.append(f"{metrics['glcm_homogeneity']:.2f}")
                ener_list.append(f"{energia:.2f}")
                ent_list.append(f"{entropia:.2f}")

    last_metrics = None
    if has_defect and n_list:
        last_metrics = {
            "class_name": " | ".join(n_list),
            "conf": " | ".join(c_list),
            "area_mm2": " | ".join(area_list),
            "perimeter_mm": " | ".join(perim_list),
            "eccentricity": " | ".join(ecc_list),
            "compactation": " | ".join(comp_list),
            "glcm_homogeneity": " | ".join(homo_list),
            "glcm_energy": " | ".join(ener_list),
            "glcm_entropy": " | ".join(ent_list),
            "color": first_color
        }

    st_text, st_col = _get_status(has_defect, is_repairable)
    return img, st_text, st_col, last_metrics


def _draw_rfdetr(bgr, preds):
    img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).copy()
    h, w = img.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if preds is None or len(preds) == 0 or preds.mask is None:
        return img, "NO DEFECTS", (155, 160, 165), None

    is_repairable = True
    has_defect = False
    
    n_list, c_list = [], []
    area_list, perim_list, ecc_list, comp_list = [], [], [], []
    homo_list, ener_list, ent_list = [], [], []
    first_color = (180, 180, 180)

    for cid in np.unique(preds.class_id):

        if int(cid) == 4:
            continue
        
        idxs = np.where(preds.class_id == cid)[0]
        idxs = idxs[np.argsort(-preds.confidence[idxs])]
        acc = np.zeros((h, w), dtype=bool)
        for i in idxs[:2]:
            mask = preds.mask[i].astype(bool)
            if mask.shape[:2] != (h, w):
                mask = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
            metrics = _compute_metrics(mask, gray)
            
            area_mm2 = metrics["area_mm2"]
            ecc = metrics["eccentricity"]
            energia = metrics["glcm_energy"]
            entropia = metrics["glcm_entropy"]

            has_defect = True
            defect_repairable = True
            
            if int(cid) == 3:
                defect_repairable = False
            elif int(cid) == 1:
                if ecc > 0.85 and area_mm2 > 5.0:
                    defect_repairable = False
            elif int(cid) in [0, 2]:
                if area_mm2 > 30.0 or energia < 0.05 or entropia > 7.0:
                    defect_repairable = False

            if not defect_repairable:
                is_repairable = False

            if acc.sum() > 0 and (acc & mask).sum() / max((acc | mask).sum(), 1) > 0.7:
                continue
            acc |= mask
            
            col = CLASS_COLORS_RGB.get(int(cid), (180, 180, 180))
            if not n_list: first_color = col
            
            ov = np.zeros_like(img)
            ov[acc] = col
            img = cv2.addWeighted(img, 1.0, ov, 0.40, 0)
            ys, xs = np.where(acc)
            if len(xs):
                x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
                cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)

                lbl_name = CLASS_NAMES_SHORT.get(int(cid), str(int(cid))).upper()
                lbl_conf = int(float(preds.confidence[i]) * 100)
                
                n_list.append(lbl_name)
                c_list.append(f"{lbl_conf}%")
                area_list.append(f"{area_mm2:.1f}")
                perim_list.append(f"{metrics['perimeter_mm']:.1f}")
                ecc_list.append(f"{ecc:.2f}")
                comp_list.append(f"{metrics['compactation']:.2f}")
                homo_list.append(f"{metrics['glcm_homogeneity']:.2f}")
                ener_list.append(f"{energia:.2f}")
                ent_list.append(f"{entropia:.2f}")

    last_metrics = None
    if has_defect and n_list:
        last_metrics = {
            "class_name": " | ".join(n_list),
            "conf": " | ".join(c_list),
            "area_mm2": " | ".join(area_list),
            "perimeter_mm": " | ".join(perim_list),
            "eccentricity": " | ".join(ecc_list),
            "compactation": " | ".join(comp_list),
            "glcm_homogeneity": " | ".join(homo_list),
            "glcm_energy": " | ".join(ener_list),
            "glcm_entropy": " | ".join(ent_list),
            "color": first_color
        }

    st_text, st_col = _get_status(has_defect, is_repairable)
    return img, st_text, st_col, last_metrics