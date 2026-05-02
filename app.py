import streamlit as st
import tensorflow as tf
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import cv2
import os
import urllib.request
import time
import re

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bird Species Identification",
    page_icon="🪶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE FOR THEME ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

# --- 3. DYNAMIC CSS STYLING ---
def inject_css():
    if st.session_state.theme == 'dark':
        bg_color = "#0b1121"
        panel_bg = "rgba(255, 255, 255, 0.03)"
        text_main = "#ccd6f6"
        text_sub = "#8892b0"
        accent_blue = "#00f2fe"
        accent_teal = "#64ffda"
        card_bg = "linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%)"
        border_color = "rgba(255, 255, 255, 0.08)"
        button_bg = "rgba(255, 255, 255, 0.05)"
        uploader_bg = "#111827"  # Solid Dark Color for Uploader box
    else:
        bg_color = "#f4f7f6"
        panel_bg = "#ffffff"
        text_main = "#2d3748"
        text_sub = "#718096"
        accent_blue = "#3182ce"
        accent_teal = "#38b2ac"
        card_bg = "linear-gradient(135deg, rgba(49, 130, 206, 0.1) 0%, rgba(56, 178, 172, 0.1) 100%)"
        border_color = "rgba(0, 0, 0, 0.08)"
        button_bg = "#ffffff"
        uploader_bg = "#ffffff"  # Solid Light Color for Uploader box

    st.markdown(f"""
    <style>
        /* Base Desktop Styles */
        #MainMenu, header, footer, [data-testid="stToolbar"], .stDeployButton, [data-testid="stSidebar"] {{ display: none !important; }}
        .stApp {{ background-color: {bg_color}; min-height: 100vh; font-family: 'Inter', sans-serif; color: {text_main}; transition: background-color 0.3s ease; }}
        
        /* Streamlit Native Buttons */
        [data-testid="stButton"] button {{ background-color: {button_bg} !important; color: {text_main} !important; border: 1px solid {border_color} !important; transition: all 0.3s ease; border-radius: 20px; }}
        [data-testid="stButton"] button:hover {{ border-color: {accent_blue} !important; color: {accent_blue} !important; }}
        
        /* General Layout */
        [data-testid="stHorizontalBlock"] {{ gap: 2rem !important; padding: 2rem 4rem !important; align-items: stretch !important; }}
        details.left-panel {{ background: {panel_bg}; border: 1px solid {border_color}; border-radius: 20px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; transition: all 0.3s ease; }}
        .panel-logo {{ text-align: center; padding-bottom: 20px; border-bottom: 1px dashed {border_color}; }}
        .panel-logo-title {{ font-size: 20px; font-weight: 800; color: {accent_blue}; margin: 10px 0 0 0; }}
        .panel-logo-sub {{ font-size: 11px; color: {text_sub}; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }}
        .section-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; color: {accent_teal}; margin: 15px 0 8px 0; }}
        .tag {{ background: rgba(100, 255, 218, 0.1); border: 1px solid rgba(100, 255, 218, 0.3); color: {text_main}; padding: 6px 12px; border-radius: 20px; font-size: 12px; display: inline-flex; margin: 4px; }}
        .main-content {{ background: {panel_bg}; border: 1px solid {border_color}; border-radius: 20px; padding: 40px; transition: all 0.3s ease; }}
        .hero-title {{ font-size: 3rem; font-weight: 800; color: {text_main}; line-height: 1.2; margin: 0 0 16px; text-align: center; }}
        .hero-title span {{ color: {accent_blue}; }}
        .hero-sub {{ font-size: 1.1rem; color: {text_sub}; max-width: 500px; margin: 0 auto; text-align: center; }}
        
        /* 🔥 ABSOLUTE OVERRIDE FOR FILE UPLOADER 🔥 */
        [data-testid="stFileUploader"] {{ background-color: {uploader_bg} !important; border: 2px dashed {accent_blue} !important; border-radius: 16px !important; padding: 10px !important; transition: background-color 0.3s ease !important; }}
        
        /* Make all internal layers completely invisible so the main color shows through */
        [data-testid="stFileUploader"] > section, 
        [data-testid="stFileUploader"] > div, 
        [data-testid="stFileUploadDropzone"] {{ background-color: transparent !important; border: none !important; }}
        
        /* 🔥 FIX FOR THE UPLOADED FILE BADGE (The dark box in your image) 🔥 */
        [data-testid="stUploadedFile"] {{ background-color: {panel_bg} !important; border: 1px solid {border_color} !important; border-radius: 10px !important; }}
        [data-testid="stUploadedFile"] div, [data-testid="stUploadedFile"] span, [data-testid="stUploadedFile"] small {{ color: {text_main} !important; }}
        [data-testid="stUploadedFile"] button svg {{ fill: {text_main} !important; }}

        /* Force text colors to update */
        [data-testid="stFileUploader"] label, 
        [data-testid="stFileUploader"] p, 
        [data-testid="stFileUploader"] span, 
        [data-testid="stFileUploader"] small {{ color: {text_main} !important; }}
        
        /* Results Cards */
        .result-card {{ background: {card_bg}; border: 1px solid {accent_blue}; border-radius: 16px; padding: 30px; text-align: center; margin-top: 20px; }}
        .result-label {{ font-size: 12px; color: {accent_blue}; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }}
        .result-text {{ font-size: 2rem; color: {text_main}; font-weight: 800; margin: 10px 0; }}
        .result-score {{ color: {accent_teal}; font-size: 1.1rem; font-weight: 600; }}
        .error-card {{ background: rgba(255, 0, 0, 0.1); border: 1px solid rgba(255, 0, 0, 0.3); border-radius: 16px; padding: 30px; text-align: center; margin-top: 20px; }}
        .error-text {{ font-size: 1.5rem; color: #ff4b4b; font-weight: bold; }}

        /* Mobile Responsive */
        @media screen and (max-width: 768px) {{
            [data-testid="stHorizontalBlock"] {{ padding: 1rem 1rem !important; gap: 1rem !important; }}
            .main-content {{ padding: 20px !important; border-radius: 15px !important; }}
            details.left-panel {{ padding: 20px !important; border-radius: 15px !important; }}
            .hero-title {{ font-size: 2rem !important; }}
            .hero-sub {{ font-size: 0.9rem !important; }}
            [data-testid="stFileUploader"] {{ padding: 5px !important; }}
            .result-card {{ padding: 20px !important; }}
            .result-text {{ font-size: 1.6rem !important; }}
        }}
        @media screen and (max-width: 480px) {{
            .hero-title {{ font-size: 1.7rem !important; }}
            .tag {{ font-size: 10px !important; padding: 4px 8px !important; margin: 2px !important; }}
            .panel-logo-title {{ font-size: 18px !important; }}
        }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

col_spacer, col_btn = st.columns([10, 1])
with col_btn:
    st.button("🌓 Toggle Theme", on_click=toggle_theme)


# --- 4. DATA & MODEL LOADING ---
@st.cache_data
def load_database():
    # --- FILE 1: The Core Classes (Mandatory 2,205 rows) ---
    classes_path = 'bird_master_database.csv' 
    try:
        df_classes = pd.read_csv(classes_path)
        names_list = df_classes['Bird_Species'].tolist()
    except Exception as e:
        st.error(f"❌ Core index missing: {e}")
        names_list = ["Unknown"] * 2205 

    # --- FILE 2: The Optional Summaries (Dynamic rows) ---
    summaries_path = 'bird_summaries.csv'
    summary_dict = {}
    
    if os.path.exists(summaries_path):
        try:
            df_summaries = pd.read_csv(summaries_path)
            summary_dict = dict(zip(df_summaries['species_query'], df_summaries['text']))
        except Exception as e:
            st.warning(f"⚠️ Could not read summaries file: {e}")
            
    return names_list, summary_dict
    

@st.cache_resource
def load_classification_model():
    model_path = 'bird_model_V2_final.keras'
    
    # Your verified golden link
    MODEL_URL = "https://github.com/Aman007-coder3/Bird-Species-Identification/releases/download/v1.0/bird_model_V2_final.keras"
    
    # 1. Aggressive Cleanup Check (Deletes fake webpages)
    if os.path.exists(model_path):
        size_in_mb = os.path.getsize(model_path) / (1024 * 1024)
        if size_in_mb < 20.0:
            os.remove(model_path)
    
   # 2. GitHub Release Downloader
    if not os.path.exists(model_path):
        # Create an empty container that we can clear later
        download_status = st.empty() 
        download_status.info("⬇️ Downloading High-Resolution AI Model from GitHub (This takes about 30 seconds)...")
        try:
            urllib.request.urlretrieve(MODEL_URL, model_path)
            new_size = os.path.getsize(model_path) / (1024 * 1024)
            if new_size < 20.0:
                download_status.error("❌ Download failed! The downloaded file is broken/too small.")
                os.remove(model_path)
                st.stop()
            else:
                download_status.success(f"✅ Successfully downloaded {new_size:.2f} MB model!")
                time.sleep(4)            # Wait for 4 seconds so the user can read the success message
                download_status.empty()  # CLEARS the container, hiding the messages completely!
        except Exception as e:
            download_status.error(f"Failed to download Model: {e}")
            st.stop()

    # 3. Model Architecture (Reverted back to EfficientNetB0 standard!)
    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=(224, 224, 3), 
        include_top=False, 
        weights=None
    )
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(len(CLASS_NAMES), activation='softmax')(x) 
    m = tf.keras.Model(inputs, outputs)
    
    # 4. Load weights into the B0 brain
    m.load_weights(model_path) 
    return m

@st.cache_resource
def load_yolo_model():
    return YOLO("yolov8n.pt")

with st.spinner("Initializing AI Pipeline..."):
    CLASS_NAMES, BIRD_SUMMARIES = load_database()
    classifier_model = load_classification_model()
    yolo_model = load_yolo_model()


# --- 5. LOGIC: YOLO GATEKEEPER & FAILSAFE ---
def process_image(pil_image):
    open_cv_image = np.array(pil_image) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() 
    
    results = yolo_model(open_cv_image, verbose=False)
    BIRD_CLASS_ID = 14 
    
    bird_detected_by_yolo = False
    cropped_img = None
    
    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == BIRD_CLASS_ID:
                bird_detected_by_yolo = True
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                
                h, w, _ = open_cv_image.shape
                pad = 20
                y1, y2 = max(0, y1-pad), min(h, y2+pad)
                x1, x2 = max(0, x1-pad), min(w, x2+pad)
                
                crop = open_cv_image[y1:y2, x1:x2]
                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                cropped_img = Image.fromarray(crop_rgb)
                break 
        if bird_detected_by_yolo:
            break

    target_img = cropped_img if bird_detected_by_yolo else pil_image
    
    # Image size matching EfficientNetB0
    img_resized = target_img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    img_array = tf.expand_dims(img_array, 0)
    
    predictions = classifier_model.predict(img_array, verbose=0)
    predicted_idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0])) * 100
    
    species_name = CLASS_NAMES[predicted_idx] if predicted_idx < len(CLASS_NAMES) else "Unknown"
    
    if bird_detected_by_yolo:
        status = "Success"
        message = "Bird isolated by YOLO."
    else:
        if confidence >= 40.0:
            status = "Success"
            message = "YOLO missed it, but Classifier is confident it's a bird."
        else:
            status = "Failed"
            message = "No bird detected."
            
    return status, message, target_img, species_name, confidence


# --- 6. MAIN UI LAYOUT ---
left_col, main_col = st.columns([1, 2.5])

with left_col:
    logo_html = '<div class="panel-logo-icon">🐦</div>'
    if os.path.exists('logo.webp'):
        import base64
        with open("logo.webp", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f'<img src="data:image/webp;base64,{encoded_string}" width="120" style="margin-bottom:10px;">'

    st.html(f"""
    <details class="left-panel" open>
        <div class="panel-content">
            <div class="panel-logo">
                {logo_html}
                <h2 class="panel-logo-title">BIET Jhansi</h2>
                <div class="panel-logo-sub">Major Project 2026</div>
                <div class="tag" style="margin-top:10px; font-weight: bold;">Group-5</div>
            </div>
            <p class="section-label">🎓 Mentor</p>
            <div><span class="tag">👨‍🏫 Prof. Yash Pal Singh</span></div>
            <p class="section-label">🎓 HOD CSE</p>
            <div><span class="tag">👨‍🏫 Prof. Sanjai Kumar Gupta</span></div>
            <p class="section-label">👨‍💻 Developers</p>
            <div>
                <span class="tag">Aman (2200430100007)</span>
                <span class="tag">Bal Krishna Rao (2200430100024)</span>
                <span class="tag">Suryank Mishra (2200430100057)</span>
                <span class="tag">Yugank Singh (2200430100070)</span>
                <span class="tag">Rohit Kumar Bharti (2300430109005)</span>
            </div>
        </div>
    </details>
    """)

with main_col:
    st.html("""
    <div class="main-content">
        <h1 class="hero-title">Bird Species <span>Identification</span></h1>
        <p class="hero-sub">Using Deep Learning.</p>
    </div>
    """)

    st.write("")
    uploaded_file = st.file_uploader(label="Upload Image", type=["jpg", "jpeg", "png" ,"webp"], label_visibility="collapsed")

    if uploaded_file is not None:
        img_col, res_col = st.columns([1, 1], gap="large")
        original_image = Image.open(uploaded_file).convert('RGB')
        
        with st.spinner("Running deep learning pipeline..."):
            status, message, processed_img, species_name, confidence = process_image(original_image)
            
        with img_col:
            st.image(processed_img, caption="Processed Image", use_container_width=True)
            
        with res_col:
            if status == "Success":
                st.html(f"""
                <div class="result-card">
                    <p class="result-label">Classification Result</p>
                    <p class="result-text">{species_name}</p>
                    <p class="result-score">Confidence Score: {confidence:.2f}%</p>
                </div>
                """)
                st.progress(confidence / 100)
                
          # Try to pull the offline Wikipedia summary if available
                if BIRD_SUMMARIES:
                    offline_summary = BIRD_SUMMARIES.get(species_name)
                    
                    if offline_summary:
                        # 1. Use Regex to split the text by the "--- Section Name ---" markers
                        sections = re.split(r'---\s*(.*?)\s*---', offline_summary)
                        parsed_data = {}
                        
                        # Pack the split text into a clean dictionary
                        for i in range(1, len(sections), 2):
                            title = sections[i].strip()
                            content = sections[i+1].strip()
                            parsed_data[title] = content
                        
                        # 2. Render the separate toggle buttons
                        st.markdown("### 📖 Species Encyclopedia")
                        
                        # Loop through the exact sections you want to create toggles for
                        for section_name in ["Summary", "Description", "Behavior", "Taxonomy", "Distribution"]:
                            # Only create a button if the bird actually has data for that section
                            if section_name in parsed_data:
                                with st.expander(f"🔍 {section_name}"):
                                    st.write(parsed_data[section_name])
                                    
                    else:
                        st.info("📚 **Educational Summary**\n\nDetailed habitat and behavioral data for this specific species is currently being updated in our database.")
            else:
                st.html(f"""
                <div class="error-card">
                    <p class="error-text">❌ No Bird Detected</p>
                    <p style="color: #ff4b4b; font-size: 14px;">We couldn't find a bird in this image, and the model confidence is too low to make a guess.</p>
                </div>
                """)
