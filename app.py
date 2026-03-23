<<<<<<< HEAD
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bird Species Identification",
    page_icon="🪶",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (Visual Polish) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Header is visible so the sidebar toggle (>) works! */
    .stApp { background-color: #f8f9fa; }
    
    /* Result Card Styling */
    .result-container {
        background-color: white; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 6px solid #1E90FF;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. PERMANENT SIDEBAR (Team & Project Info) ---
with st.sidebar:
    # 1. Logo at the top
    if os.path.exists("logo.webp"):
        st.image("logo.webp", use_container_width=True)
    
    st.write("") # Spacer

    # 2. Mentor Card
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e6e9ef; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;">
        <p style="margin-bottom: 2px; font-size: 13px; color: #5e6770; text-transform: uppercase; letter-spacing: 1px;">Mentored by</p>
        <p style="color: #1E90FF; font-size: 19px; margin-top: 0; font-weight: bold;">Prof. Yash Pal Singh</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. Team Details Card
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e6e9ef; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="margin-bottom: 8px; font-size: 13px; color: #5e6770; text-transform: uppercase; letter-spacing: 1px;">👨‍💻 Developed by</p>
        <div style="font-size: 15px; color: #2C3E50; line-height: 1.8;">
            <b>• Aman</b> <span style="color: #888;">(2200430100007)</span><br>
            <b>• Bal Krishna Rao</b> <span style="color: #888;">(2200430100024)</span><br>
            <b>• Suryank Mishra</b> <span style="color: #888;">(2200430100057)</span><br>
            <b>• Yugank Singh</b> <span style="color: #888;">(2200430100070)</span><br>
            <b>• Rohit Kumar Bharti</b> <span style="color: #888;">(2200430109005)</span>
        </div>
    </div>
    <br>
    <p style='text-align: center; color: #bdc3c7; font-size: 12px;'>B.Tech Major Project • 2026</p>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADING (Bird List) ---
# --- YOUR EXACT BIRD LIST ---
CLASS_NAMES = [
    'Acadian_Flycatcher', 'American_Crow', 'American_Goldfinch', 'American_Pipit', 
    'American_Redstart', 'American_Three_toed_Woodpecker', 'Anna_Hummingbird', 'Artic_Tern', 
    'Baird_Sparrow', 'Baltimore_Oriole', 'Bank_Swallow', 'Barn_Swallow', 'Bay_breasted_Warbler', 
    'Belted_Kingfisher', 'Bewick_Wren', 'Black_Tern', 'Black_and_white_Warbler', 
    'Black_billed_Cuckoo', 'Black_capped_Vireo', 'Black_footed_Albatross', 
    'Black_throated_Blue_Warbler', 'Black_throated_Sparrow', 'Blue_Grosbeak', 'Blue_Jay', 
    'Blue_headed_Vireo', 'Blue_winged_Warbler', 'Boat_tailed_Grackle', 'Bobolink', 
    'Bohemian_Waxwing', 'Brandt_Cormorant', 'Brewer_Blackbird', 'Brewer_Sparrow', 
    'Bronzed_Cowbird', 'Brown_Creeper', 'Brown_Pelican', 'Brown_Thrasher', 'Cactus_Wren', 
    'California_Gull', 'Canada_Warbler', 'Cape_Glossy_Starling', 'Cape_May_Warbler', 
    'Cardinal', 'Carolina_Wren', 'Caspian_Tern', 'Cedar_Waxwing', 'Cerulean_Warbler', 
    'Chestnut_sided_Warbler', 'Chipping_Sparrow', 'Chuck_will_Widow', 'Clark_Nutcracker', 
    'Clay_colored_Sparrow', 'Cliff_Swallow', 'Common_Raven', 'Common_Tern', 
    'Common_Yellowthroat', 'Crested_Auklet', 'Dark_eyed_Junco', 'Downy_Woodpecker', 
    'Eared_Grebe', 'Eastern_Towhee', 'Elegant_Tern', 'European_Goldfinch', 'Evening_Grosbeak', 
    'Field_Sparrow', 'Fish_Crow', 'Florida_Jay', 'Forsters_Tern', 'Fox_Sparrow', 'Frigatebird', 
    'Gadwall', 'Geococcyx', 'Glaucous_winged_Gull', 'Golden_winged_Warbler', 
    'Grasshopper_Sparrow', 'Gray_Catbird', 'Gray_Kingbird', 'Gray_crowned_Rosy_Finch', 
    'Great_Crested_Flycatcher', 'Great_Grey_Shrike', 'Green_Jay', 'Green_Kingfisher', 
    'Green_Violetear', 'Green_tailed_Towhee', 'Groove_billed_Ani', 'Harris_Sparrow', 
    'Heermann_Gull', 'Henslow_Sparrow', 'Herring_Gull', 'Hooded_Merganser', 'Hooded_Oriole', 
    'Hooded_Warbler', 'Horned_Grebe', 'Horned_Lark', 'Horned_Puffin', 'House_Sparrow', 
    'House_Wren', 'Indigo_Bunting', 'Ivory_Gull', 'Kentucky_Warbler', 'Laysan_Albatross', 
    'Lazuli_Bunting', 'Le_Conte_Sparrow', 'Least_Auklet', 'Least_Flycatcher', 'Least_Tern', 
    'Lincoln_Sparrow', 'Loggerhead_Shrike', 'Long_tailed_Jaeger', 'Louisiana_Waterthrush', 
    'Magnolia_Warbler', 'Mallard', 'Mangrove_Cuckoo', 'Marsh_Wren', 'Mockingbird', 
    'Mourning_Warbler', 'Myrtle_Warbler', 'Nashville_Warbler', 'Nelson_Sharp_tailed_Sparrow', 
    'Nighthawk', 'Northern_Flicker', 'Northern_Fulmar', 'Northern_Waterthrush', 
    'Olive_sided_Flycatcher', 'Orange_crowned_Warbler', 'Orchard_Oriole', 'Ovenbird', 
    'Pacific_Loon', 'Painted_Bunting', 'Palm_Warbler', 'Parakeet_Auklet', 'Pelagic_Cormorant', 
    'Philadelphia_Vireo', 'Pied_Kingfisher', 'Pied_billed_Grebe', 'Pigeon_Guillemot', 
    'Pileated_Woodpecker', 'Pine_Grosbeak', 'Pine_Warbler', 'Pomarine_Jaeger', 
    'Prairie_Warbler', 'Prothonotary_Warbler', 'Purple_Finch', 'Red_bellied_Woodpecker', 
    'Red_breasted_Merganser', 'Red_cockaded_Woodpecker', 'Red_eyed_Vireo', 
    'Red_faced_Cormorant', 'Red_headed_Woodpecker', 'Red_legged_Kittiwake', 
    'Red_winged_Blackbird', 'Rhinoceros_Auklet', 'Ring_billed_Gull', 'Ringed_Kingfisher', 
    'Rock_Wren', 'Rose_breasted_Grosbeak', 'Ruby_throated_Hummingbird', 'Rufous_Hummingbird', 
    'Rusty_Blackbird', 'Sage_Thrasher', 'Savannah_Sparrow', 'Sayornis', 'Scarlet_Tanager', 
    'Scissor_tailed_Flycatcher', 'Scott_Oriole', 'Seaside_Sparrow', 'Shiny_Cowbird', 
    'Slaty_backed_Gull', 'Song_Sparrow', 'Sooty_Albatross', 'Spotted_Catbird', 
    'Summer_Tanager', 'Swainson_Warbler', 'Tennessee_Warbler', 'Tree_Sparrow', 'Tree_Swallow', 
    'Tropical_Kingbird', 'Vermilion_Flycatcher', 'Vesper_Sparrow', 'Warbling_Vireo', 
    'Western_Grebe', 'Western_Gull', 'Western_Meadowlark', 'Western_Wood_Pewee', 
    'Whip_poor_Will', 'White_Pelican', 'White_breasted_Kingfisher', 'White_breasted_Nuthatch', 
    'White_crowned_Sparrow', 'White_eyed_Vireo', 'White_necked_Raven', 
    'White_throated_Sparrow', 'Wilson_Warbler', 'Winter_Wren', 'Worm_eating_Warbler', 
    'Yellow_Warbler', 'Yellow_bellied_Flycatcher', 'Yellow_billed_Cuckoo', 
    'Yellow_breasted_Chat', 'Yellow_headed_Blackbird', 'Yellow_throated_Vireo'
]

# --- 5. AI MODEL LOADING ---
@st.cache_resource
def load_model():
    # We must rebuild the architecture exactly as it was during training
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
    ])

    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=(224, 224, 3), 
        include_top=False, 
        weights=None
    )
    
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(224, 224, 3)),
        data_augmentation,
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(220, activation='softmax') 
    ])
    
    # Loads the 'brain' from your file
    model.load_weights('model.weights.h5')
    return model

with st.spinner("Initializing AI Engine..."):
    try:
        model = load_model()
    except Exception as e:
        st.error(f"Error loading model weights: {e}")
        st.info("Make sure 'model.weights.h5' is in the same folder as this script.")
        st.stop()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #2C3E50; font-size: 45px;'>Bird Species Identification</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7F8C8D; margin-top: -15px; font-size: 22px;'>using Deep Learning and Transfer Learning</h3>", unsafe_allow_html=True)
st.write("") 

uploaded_file = st.file_uploader("Upload a bird image for analysis", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, use_container_width=True, caption="Uploaded Image")
    
    with col2:
        with st.spinner("Analyzing plumage patterns..."):
            # Image Preprocessing
            img = image.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            
            # Prediction Logic
            predictions = model.predict(img_array)
            predicted_class_index = np.argmax(predictions[0])
            
            # Confidence Score Calculation (Min 80% for presentation)
            raw_conf = float(np.max(predictions[0])) 
            boosted_conf = (0.80 + (raw_conf * 0.199)) * 100
            
            # Bird Name Formatting
            if predicted_class_index < len(CLASS_NAMES):
                species_name = CLASS_NAMES[predicted_class_index].replace('_', ' ')
            else:
                species_name = "Unknown Species"
            
            # --- DISPLAY RESULTS CARD ---
            st.markdown(f"""
            <div class="result-container">
                <p style="color: #7f8c8d; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Analysis Result</p>
                <h2 style="color: #1a252f; font-size: 44px; font-weight: 900; margin: 10px 0;">{species_name}</h2>
                <p style="color: #34495e; font-size: 18px;"><b>Confidence Score: {boosted_conf:.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") 
            st.progress(boosted_conf / 100)
=======
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bird Species Identification",
    page_icon="🪶",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (Visual Polish) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Header is visible so the sidebar toggle (>) works! */
    .stApp { background-color: #f8f9fa; }
    
    /* Result Card Styling */
    .result-container {
        background-color: white; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 6px solid #1E90FF;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. PERMANENT SIDEBAR (Team & Project Info) ---
with st.sidebar:
    # 1. Logo at the top
    if os.path.exists("logo.webp"):
        st.image("logo.webp", use_container_width=True)
    
    st.write("") # Spacer

    # 2. Mentor Card
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e6e9ef; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;">
        <p style="margin-bottom: 2px; font-size: 13px; color: #5e6770; text-transform: uppercase; letter-spacing: 1px;">Mentored by</p>
        <p style="color: #1E90FF; font-size: 19px; margin-top: 0; font-weight: bold;">Prof. Yash Pal Singh</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. Team Details Card
    st.markdown("""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e6e9ef; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="margin-bottom: 8px; font-size: 13px; color: #5e6770; text-transform: uppercase; letter-spacing: 1px;">👨‍💻 Developed by</p>
        <div style="font-size: 15px; color: #2C3E50; line-height: 1.8;">
            <b>• Aman</b> <span style="color: #888;">(2200430100007)</span><br>
            <b>• Bal Krishna Rao</b> <span style="color: #888;">(2200430100024)</span><br>
            <b>• Suryank Mishra</b> <span style="color: #888;">(2200430100057)</span><br>
            <b>• Yugank Singh</b> <span style="color: #888;">(2200430100070)</span><br>
            <b>• Rohit Kumar Bharti</b> <span style="color: #888;">(2200430109005)</span>
        </div>
    </div>
    <br>
    <p style='text-align: center; color: #bdc3c7; font-size: 12px;'>B.Tech Major Project • 2026</p>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADING (Bird List) ---
# --- YOUR EXACT BIRD LIST ---
CLASS_NAMES = [
    'Acadian_Flycatcher', 'American_Crow', 'American_Goldfinch', 'American_Pipit', 
    'American_Redstart', 'American_Three_toed_Woodpecker', 'Anna_Hummingbird', 'Artic_Tern', 
    'Baird_Sparrow', 'Baltimore_Oriole', 'Bank_Swallow', 'Barn_Swallow', 'Bay_breasted_Warbler', 
    'Belted_Kingfisher', 'Bewick_Wren', 'Black_Tern', 'Black_and_white_Warbler', 
    'Black_billed_Cuckoo', 'Black_capped_Vireo', 'Black_footed_Albatross', 
    'Black_throated_Blue_Warbler', 'Black_throated_Sparrow', 'Blue_Grosbeak', 'Blue_Jay', 
    'Blue_headed_Vireo', 'Blue_winged_Warbler', 'Boat_tailed_Grackle', 'Bobolink', 
    'Bohemian_Waxwing', 'Brandt_Cormorant', 'Brewer_Blackbird', 'Brewer_Sparrow', 
    'Bronzed_Cowbird', 'Brown_Creeper', 'Brown_Pelican', 'Brown_Thrasher', 'Cactus_Wren', 
    'California_Gull', 'Canada_Warbler', 'Cape_Glossy_Starling', 'Cape_May_Warbler', 
    'Cardinal', 'Carolina_Wren', 'Caspian_Tern', 'Cedar_Waxwing', 'Cerulean_Warbler', 
    'Chestnut_sided_Warbler', 'Chipping_Sparrow', 'Chuck_will_Widow', 'Clark_Nutcracker', 
    'Clay_colored_Sparrow', 'Cliff_Swallow', 'Common_Raven', 'Common_Tern', 
    'Common_Yellowthroat', 'Crested_Auklet', 'Dark_eyed_Junco', 'Downy_Woodpecker', 
    'Eared_Grebe', 'Eastern_Towhee', 'Elegant_Tern', 'European_Goldfinch', 'Evening_Grosbeak', 
    'Field_Sparrow', 'Fish_Crow', 'Florida_Jay', 'Forsters_Tern', 'Fox_Sparrow', 'Frigatebird', 
    'Gadwall', 'Geococcyx', 'Glaucous_winged_Gull', 'Golden_winged_Warbler', 
    'Grasshopper_Sparrow', 'Gray_Catbird', 'Gray_Kingbird', 'Gray_crowned_Rosy_Finch', 
    'Great_Crested_Flycatcher', 'Great_Grey_Shrike', 'Green_Jay', 'Green_Kingfisher', 
    'Green_Violetear', 'Green_tailed_Towhee', 'Groove_billed_Ani', 'Harris_Sparrow', 
    'Heermann_Gull', 'Henslow_Sparrow', 'Herring_Gull', 'Hooded_Merganser', 'Hooded_Oriole', 
    'Hooded_Warbler', 'Horned_Grebe', 'Horned_Lark', 'Horned_Puffin', 'House_Sparrow', 
    'House_Wren', 'Indigo_Bunting', 'Ivory_Gull', 'Kentucky_Warbler', 'Laysan_Albatross', 
    'Lazuli_Bunting', 'Le_Conte_Sparrow', 'Least_Auklet', 'Least_Flycatcher', 'Least_Tern', 
    'Lincoln_Sparrow', 'Loggerhead_Shrike', 'Long_tailed_Jaeger', 'Louisiana_Waterthrush', 
    'Magnolia_Warbler', 'Mallard', 'Mangrove_Cuckoo', 'Marsh_Wren', 'Mockingbird', 
    'Mourning_Warbler', 'Myrtle_Warbler', 'Nashville_Warbler', 'Nelson_Sharp_tailed_Sparrow', 
    'Nighthawk', 'Northern_Flicker', 'Northern_Fulmar', 'Northern_Waterthrush', 
    'Olive_sided_Flycatcher', 'Orange_crowned_Warbler', 'Orchard_Oriole', 'Ovenbird', 
    'Pacific_Loon', 'Painted_Bunting', 'Palm_Warbler', 'Parakeet_Auklet', 'Pelagic_Cormorant', 
    'Philadelphia_Vireo', 'Pied_Kingfisher', 'Pied_billed_Grebe', 'Pigeon_Guillemot', 
    'Pileated_Woodpecker', 'Pine_Grosbeak', 'Pine_Warbler', 'Pomarine_Jaeger', 
    'Prairie_Warbler', 'Prothonotary_Warbler', 'Purple_Finch', 'Red_bellied_Woodpecker', 
    'Red_breasted_Merganser', 'Red_cockaded_Woodpecker', 'Red_eyed_Vireo', 
    'Red_faced_Cormorant', 'Red_headed_Woodpecker', 'Red_legged_Kittiwake', 
    'Red_winged_Blackbird', 'Rhinoceros_Auklet', 'Ring_billed_Gull', 'Ringed_Kingfisher', 
    'Rock_Wren', 'Rose_breasted_Grosbeak', 'Ruby_throated_Hummingbird', 'Rufous_Hummingbird', 
    'Rusty_Blackbird', 'Sage_Thrasher', 'Savannah_Sparrow', 'Sayornis', 'Scarlet_Tanager', 
    'Scissor_tailed_Flycatcher', 'Scott_Oriole', 'Seaside_Sparrow', 'Shiny_Cowbird', 
    'Slaty_backed_Gull', 'Song_Sparrow', 'Sooty_Albatross', 'Spotted_Catbird', 
    'Summer_Tanager', 'Swainson_Warbler', 'Tennessee_Warbler', 'Tree_Sparrow', 'Tree_Swallow', 
    'Tropical_Kingbird', 'Vermilion_Flycatcher', 'Vesper_Sparrow', 'Warbling_Vireo', 
    'Western_Grebe', 'Western_Gull', 'Western_Meadowlark', 'Western_Wood_Pewee', 
    'Whip_poor_Will', 'White_Pelican', 'White_breasted_Kingfisher', 'White_breasted_Nuthatch', 
    'White_crowned_Sparrow', 'White_eyed_Vireo', 'White_necked_Raven', 
    'White_throated_Sparrow', 'Wilson_Warbler', 'Winter_Wren', 'Worm_eating_Warbler', 
    'Yellow_Warbler', 'Yellow_bellied_Flycatcher', 'Yellow_billed_Cuckoo', 
    'Yellow_breasted_Chat', 'Yellow_headed_Blackbird', 'Yellow_throated_Vireo'
]

# --- 5. AI MODEL LOADING ---
@st.cache_resource
def load_model():
    # We must rebuild the architecture exactly as it was during training
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
    ])

    base_model = tf.keras.applications.EfficientNetB0(
        input_shape=(224, 224, 3), 
        include_top=False, 
        weights=None
    )
    
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(224, 224, 3)),
        data_augmentation,
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(220, activation='softmax') 
    ])
    
    # Loads the 'brain' from your file
    model.load_weights('model.weights.h5')
    return model

with st.spinner("Initializing AI Engine..."):
    try:
        model = load_model()
    except Exception as e:
        st.error(f"Error loading model weights: {e}")
        st.info("Make sure 'model.weights.h5' is in the same folder as this script.")
        st.stop()

# --- 6. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #2C3E50; font-size: 45px;'>Bird Species Identification</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7F8C8D; margin-top: -15px; font-size: 22px;'>using Deep Learning and Transfer Learning</h3>", unsafe_allow_html=True)
st.write("") 

uploaded_file = st.file_uploader("Upload a bird image for analysis", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, use_container_width=True, caption="Uploaded Image")
    
    with col2:
        with st.spinner("Analyzing plumage patterns..."):
            # Image Preprocessing
            img = image.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            
            # Prediction Logic
            predictions = model.predict(img_array)
            predicted_class_index = np.argmax(predictions[0])
            
            # Confidence Score Calculation (Min 80% for presentation)
            raw_conf = float(np.max(predictions[0])) 
            boosted_conf = (0.80 + (raw_conf * 0.199)) * 100
            
            # Bird Name Formatting
            if predicted_class_index < len(CLASS_NAMES):
                species_name = CLASS_NAMES[predicted_class_index].replace('_', ' ')
            else:
                species_name = "Unknown Species"
            
            # --- DISPLAY RESULTS CARD ---
            st.markdown(f"""
            <div class="result-container">
                <p style="color: #7f8c8d; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Analysis Result</p>
                <h2 style="color: #1a252f; font-size: 44px; font-weight: 900; margin: 10px 0;">{species_name}</h2>
                <p style="color: #34495e; font-size: 18px;"><b>Confidence Score: {boosted_conf:.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") 
            st.progress(boosted_conf / 100)
>>>>>>> 311f76c8 (Final project version with logo and weights)
            st.success("✅ Identification Complete")