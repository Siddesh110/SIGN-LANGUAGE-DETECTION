# SignEase — Indian Sign Language Detection & Learning System

An AI-powered desktop application for **Indian Sign Language (ISL) Detection and Learning** using **Python, OpenCV, MediaPipe, Machine Learning, and CustomTkinter**.

This project helps users:
- Detect ISL hand signs in real time using a webcam
- Learn ISL alphabets and vocabulary
- Practice signs interactively
- Track learning progress and quiz performance

---

# Features

## Real-Time ISL Detection
- Webcam-based sign detection
- Single-hand and double-hand gesture support
- Confidence-based predictions
- Stable prediction smoothing

## Learning Module
- ISL alphabet guide
- Text-to-ISL fingerspelling helper
- Vocabulary practice

## Practice & Quiz System
- Random quizzes
- Letter-by-letter practice
- Whole-word gesture recognition
- Live feedback system

## Progress Tracking
- Correct/Wrong statistics
- Accuracy calculation
- Practice history

## Modern GUI
- Built using CustomTkinter
- Multiple themes
- Responsive fullscreen interface
- Profile customization

---

# Technologies Used

- Python
- OpenCV
- MediaPipe
- Scikit-learn
- NumPy
- Pillow
- CustomTkinter

---

# Project Structure

```bash
SignEase/
│
├── assets/
│   ├── logo.png
│   └── hand.png
│
├── data/
│   ├── single/
│   └── double/
│
├── models/
│   ├── isl_single.pkl
│   └── isl_double.pkl
│
├── image.py
├── train_model.py
├── webcam_detection.py
│
└── README.md
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/SignEase.git
cd SignEase
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

### Windows
```bash
venv\Scripts\activate
```

### Linux / Mac
```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install opencv-python mediapipe numpy pillow scikit-learn customtkinter
```

---

# Dataset Setup

Place your dataset inside:

```bash
data/single/
data/double/
```

Each folder should contain subfolders named after gestures/classes.

Example:

```bash
data/single/A/
data/single/B/
data/double/Hello/
```

---

# Train the Model

Run:

```bash
python train_model.py
```

This will:
- Extract hand landmarks
- Apply augmentation
- Train ML models
- Save `.pkl` models inside `/models`

---

# Run the Application

```bash
python image.py
```

---

# How It Works

## Hand Detection
MediaPipe detects hand landmarks in real time.

## Feature Extraction
The system extracts:
- 3D landmark coordinates
- Relative distances
- Hand geometry features

## Machine Learning
The application trains:
- SVM Classifier
- Random Forest Classifier

The best-performing model is automatically selected.

---

# Accuracy

Expected accuracy:

| Model Type | Accuracy |
|---|---|
| Single-hand signs | 93% – 98% |
| Double-hand signs | 88% – 95% |

Accuracy depends heavily on:
- Dataset quality
- Lighting conditions
- Hand visibility
- Camera quality

---

# Screenshots

Add screenshots here before uploading to GitHub.

Example:

```md
![Home Screen](screenshots/home.png)
![Detection](screenshots/detection.png)
```

---

# Future Improvements

- Deep learning integration
- Sentence-level ISL recognition
- Speech-to-sign conversion
- Mobile application support
- Cloud-based training
- Multiplayer learning mode

---

# Known Limitations

- Performance decreases in poor lighting
- Background clutter may affect detection
- Requires visible hand landmarks
- Some complex gestures may need larger datasets

---

# Contributing

Pull requests are welcome.

For major changes:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Open a pull request

---

# License

This project is licensed under the MIT License.

---

# Author

Siddesh Valmiki

---

# GitHub Upload Steps

## Initialize Git

```bash
git init
```

## Add Files

```bash
git add .
```

## Commit

```bash
git commit -m "Initial commit"
```

## Connect Repository

```bash
git remote add origin https://github.com/your-username/SignEase.git
```

## Push to GitHub

```bash
git branch -M main
git push -u origin main
```

---

# requirements.txt

Create a file named `requirements.txt`

```txt
opencv-python
mediapipe
numpy
pillow
scikit-learn
customtkinter
```
