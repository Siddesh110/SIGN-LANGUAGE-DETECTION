import os
import cv2
import mediapipe as mp
import numpy as np
import pickle
import random
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
BASE_DIR    = r"C:\SignEase\SignEase"
DATASET_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR   = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5
)
def normalize_landmarks(hand_landmarks):
    coords = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
    coords -= coords[0]
    scale = np.linalg.norm(coords[9])
    if scale > 0:
        coords /= scale
    fingertips = [4, 8, 12, 16, 20]
    distances = []
    for i in range(len(fingertips)):
        for j in range(i + 1, len(fingertips)):
            d = np.linalg.norm(coords[fingertips[i]] - coords[fingertips[j]])
            distances.append(d)
    return list(coords.flatten()) + distances
def normalize_two_hands(multi_hand_landmarks, multi_handedness):
    right = left = None
    for lm, hd in zip(multi_hand_landmarks, multi_handedness):
        label = hd.classification[0].label
        if label == "Right":
            right = lm
        else:
            left  = lm
    if right is None or left is None:
        right = multi_hand_landmarks[0]
        left  = multi_hand_landmarks[1]
    return list(normalize_landmarks(right)) + list(normalize_landmarks(left))
def augment_image(image):
    yield image
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] + 30, 0, 255)
    yield cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    hsv2 = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int32)
    hsv2[:, :, 2] = np.clip(hsv2[:, :, 2] - 30, 0, 255)
    yield cv2.cvtColor(hsv2.astype(np.uint8), cv2.COLOR_HSV2BGR)
    yield cv2.flip(image, 1)
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), 10, 1.0)
    yield cv2.warpAffine(image, M, (w, h))
    M2 = cv2.getRotationMatrix2D((w // 2, h // 2), -10, 1.0)
    yield cv2.warpAffine(image, M2, (w, h))
def extract_features(image, required_hands):
    rgb    = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    if not result.multi_hand_landmarks:
        return None
    if required_hands == 1:
        return list(normalize_landmarks(result.multi_hand_landmarks[0]))
    if required_hands == 2:
        if len(result.multi_hand_landmarks) < 2:
            return None
        return normalize_two_hands(result.multi_hand_landmarks, result.multi_handedness)
    return None
def train_model(folder, hands_required, model_name):
    X, Y         = [], []
    path         = os.path.join(DATASET_DIR, folder)
    class_counts = {}
    print(f"\n{'='*60}")
    print(f"  Training : {model_name}  (hands={hands_required})")
    print(f"  Folder   : {path}")
    print(f"{'='*60}")
    if not os.path.isdir(path):
        print(f"  [ERROR] Folder not found: {path}")
        return
    for label in sorted(os.listdir(path)):
        label_path = os.path.join(path, label)
        if not os.path.isdir(label_path):
            continue
        count = 0
        for img_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_name)
            img      = cv2.imread(img_path)
            if img is None:
                continue
            for aug_img in augment_image(img):
                feats = extract_features(aug_img, hands_required)
                if feats is not None:
                    X.append(feats)
                    Y.append(label)
                    count += 1
        class_counts[label] = count
        print(f"  {label:15s}: {count} samples")
    if not X:
        print("\n  [ERROR] No samples extracted.")
        print("  Check that your images contain visible hands.")
        return
    X = np.array(X)
    Y = np.array(Y)
    print(f"\n  Total samples (with augmentation): {len(X)}")
    print(f"  Classes: {len(set(Y))}  →  {sorted(set(Y))}")
    low = [l for l, c in class_counts.items() if c < 15]
    if low:
        print(f"\n  ⚠ Low samples (<15): {low}")
        print("    Consider adding more images for these classes.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.15, random_state=42, stratify=Y
    )
    min_class_count = min(np.sum(y_train == c) for c in np.unique(y_train))
    n_splits = max(2, min(5, int(min_class_count)))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    print(f"\n  Using {n_splits}-fold cross-validation")
    print("\n  [1/2] Training SVM with hyperparameter search...")
    svm_pipe = make_pipeline(
        StandardScaler(),
        SVC(kernel="rbf", probability=True, class_weight="balanced")
    )
    svm_params = {
        "svc__C":     [1, 10, 50, 100],
        "svc__gamma": ["scale", "auto", 0.001, 0.01]
    }
    svm_search = GridSearchCV(svm_pipe, svm_params, cv=cv, n_jobs=1, verbose=0)
    svm_search.fit(X_train, y_train)
    best_svm = svm_search.best_estimator_
    print(f"  Best SVM params: {svm_search.best_params_}")
    svm_acc = accuracy_score(y_test, best_svm.predict(X_test))
    print(f"  SVM Test Accuracy: {round(svm_acc * 100, 2)}%")
    print("\n  [2/2] Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=1
    )
    rf_pipe = make_pipeline(StandardScaler(), rf)
    rf_pipe.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf_pipe.predict(X_test))
    print(f"  Random Forest Test Accuracy: {round(rf_acc * 100, 2)}%")
    if svm_acc >= rf_acc:
        best_model = best_svm
        print(f"\n  Using SVM (better: {round(svm_acc*100,2)}% vs RF {round(rf_acc*100,2)}%)")
    else:
        best_model = rf_pipe
        print(f"\n  Using Random Forest (better: {round(rf_acc*100,2)}% vs SVM {round(svm_acc*100,2)}%)")
    y_pred = best_model.predict(X_test)
    final_acc = accuracy_score(y_test, y_pred)
    print(f"\n{'='*60}")
    print(f"  FINAL TEST ACCURACY: {round(final_acc * 100, 2)}%")
    print(f"{'='*60}")
    print("\n  Per-class report:")
    print(classification_report(y_test, y_pred))
    model_path = os.path.join(MODEL_DIR, model_name)
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"  Saved: {model_path}")
    return final_acc
print("\n" + "="*60)
print("  SIGNEASE — ISL MODEL TRAINING")
print("="*60)
acc1 = train_model("single", 1, "isl_single.pkl")
acc2 = train_model("double", 2, "isl_double.pkl")
hands.close()
print("\n" + "="*60)
print("  TRAINING COMPLETE")
if acc1: print(f"  Single-hand model accuracy : {round(acc1*100, 2)}%")
if acc2: print(f"  Double-hand model accuracy : {round(acc2*100, 2)}%")
print("="*60)