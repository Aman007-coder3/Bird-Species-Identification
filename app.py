import streamlit as st
import tensorflow as tf
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import cv2
import os
import urllib.request

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Bird Species Identification",
    page_icon="🪶",
    layout="wide"
)

# ---------------- LOAD DATABASE ----------------
@st.cache_data
def load_database():
    try:
        df = pd.read_csv("bird_master_database.csv")
        names = df["Bird_Species"].tolist()
        summaries = dict(zip(df["Bird_Species"], df.get("Wiki_Summary", [""]*len(df))))
        return names, summaries
    except:
        return ["Unknown"] * 2205, {}

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    MODEL_PATH = "bird_model_V2_final.keras"
    MODEL_URL = "https://github.com/Aman007-coder3/Bird-Species-Identification/releases/download/v1.0/bird_model_V2_final.keras"

    if not os.path.exists(MODEL_PATH):
        st.info("Downloading model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=(224, 224, 3),
        include_top=False,
        weights=None
    )

    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(len(CLASS_NAMES), activation='softmax')(x)

    model = tf.keras.Model(base_model.input, outputs)
    model.load_weights(MODEL_PATH)

    return model

# ---------------- LOAD YOLO ----------------
@st.cache_resource
def load_yolo():
    return YOLO("yolov8n.pt")

# ---------------- IMAGE PROCESSING ----------------
def process_image(image):
    img = np.array(image)
    img = img[:, :, ::-1]

    results = yolo_model(img, verbose=False)

    BIRD_CLASS_ID = 14
    cropped = None

    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == BIRD_CLASS_ID:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped = img[y1:y2, x1:x2]
                break

    if cropped is None:
        cropped = img

    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(cropped)

    # Resize
    img_resized = pil_img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)

    # 🔥 IMPORTANT FIX: EfficientNet preprocessing
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)

    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array, verbose=0)[0]

    return pil_img, preds

# ---------------- UI ----------------
st.title("🪶 Bird Species Identification System")

uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")

    col1, col2 = st.columns(2)

    with st.spinner("Running AI model..."):
        processed_img, predictions = process_image(image)

    with col1:
        st.image(processed_img, caption="Processed Image")

    with col2:
        top_k = 5
        top_indices = np.argsort(predictions)[-top_k:][::-1]

        st.subheader("🔍 Top Predictions")

        for i in top_indices:
            name = CLASS_NAMES[i]
            confidence = predictions[i] * 100
            st.write(f"**{name}** — {confidence:.2f}%")

        best_idx = top_indices[0]
        best_conf = predictions[best_idx] * 100
        best_name = CLASS_NAMES[best_idx]

        # 🔥 Confidence Threshold
        if best_conf < 40:
            st.warning("⚠️ Low confidence prediction. Try a clearer image.")
        else:
            st.success(f"✅ Final Prediction: {best_name} ({best_conf:.2f}%)")

        # Progress bar
        st.progress(best_conf / 100)

        # Summary
        if best_name in BIRD_SUMMARIES:
            st.info(f"📚 {BIRD_SUMMARIES[best_name]}")

# ---------------- INIT ----------------
with st.spinner("Loading AI pipeline..."):
    CLASS_NAMES, BIRD_SUMMARIES = load_database()
    model = load_model()
    yolo_model = load_yolo()
