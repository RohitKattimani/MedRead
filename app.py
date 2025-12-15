import streamlit as st
import pandas as pd
import time
import os
import random
from datetime import datetime

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="MedRead",
    page_icon="🩺",
    layout="centered"
)

# --- 2. ELEGANT THEME CSS ---
def local_css():
    st.markdown("""
    <style>
        /* Main Background - Clean White */
        .stApp {
            background-color: #ffffff;
            color: #2c3e50;
            font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 300;
            color: #2c3e50;
        }
        
        /* Buttons - Minimalist Outline Style */
        div.stButton > button {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #dcdcdc;
            border-radius: 6px;
            padding: 10px 24px;
            font-size: 15px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 100%;
        }
        
        div.stButton > button:hover {
            background-color: #f8f9fa;
            border-color: #b0b0b0;
            color: #000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Special styling for the 'Submit' button inside the form */
        [data-testid="stFormSubmitButton"] > button {
            background-color: #2c3e50;
            color: white;
            border: none;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #34495e;
            color: white;
        }

        /* Countdown Text */
        .countdown-text {
            font-size: 90px;
            font-weight: 300;
            text-align: center;
            color: #34495e;
            padding-top: 40px;
        }
        
        /* Footer Styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            color: #95a5a6;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            border-top: 1px solid #eaeaea;
            z-index: 100;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

if 'initialized' not in st.session_state:
    # Setup dummy files if real ones don't exist for the demo
    # In production, ensure these files exist
    file_list = ['pt1.jpg', 'pt2.jpg', 'nt1.jpg', 'nt2.jpg']
    # Fallback to create dummy logic if files are missing (optional for stability)
    available_files = [f for f in file_list] 
    
    # Shuffle
    random.shuffle(available_files)
    
    st.session_state.images = available_files
    st.session_state.current_index = 0
    st.session_state.results = []
    st.session_state.start_time = None
    st.session_state.custom_mode = False # NEW: Tracks if we are in 'Other' input mode
    st.session_state.initialized = True

# --- 4. LOGIC FUNCTIONS ---

def go_home():
    """Resets everything and goes to landing."""
    st.session_state.page = 'landing'
    st.session_state.current_index = 0
    st.session_state.results = []
    st.session_state.start_time = None
    st.session_state.custom_mode = False
    random.shuffle(st.session_state.images)

def start_countdown():
    st.session_state.page = 'countdown'

def record_choice(choice):
    # Handle empty input
    if not choice or choice.strip() == "":
        choice = "Undisclosed"

    end_time = time.time()
    duration = end_time - st.session_state.start_time if st.session_state.start_time else 0
    
    # Safety check for index
    if st.session_state.current_index < len(st.session_state.images):
        current_img = st.session_state.images[st.session_state.current_index]
    else:
        current_img = "Unknown"
    
    st.session_state.results.append({
        "Image_ID": current_img,
        "Diagnosis": choice.title(), # Clean up capitalization
        "Time_Seconds": round(duration, 3),
        "Timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    st.session_state.current_index += 1
    st.session_state.start_time = None
    st.session_state.custom_mode = False # Reset custom mode

# --- 5. HEADER (HOME BUTTON) ---
if st.session_state.page != 'landing':
    col_h1, col_h2 = st.columns([1, 10])
    with col_h1:
        if st.button("🏠"):
            go_home()
            st.rerun()

# --- 6. PAGE RENDERING ---

# >>> LANDING PAGE <<<
if st.session_state.page == 'landing':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("RadView Assessment")
    st.caption("CLINICAL DIAGNOSTIC TIMING PROTOCOL")
    st.markdown("---")
    
    st.markdown("""
    **Welcome, Doctor.**
    
    This session will measure your diagnostic speed and accuracy.
    1. A series of Radiology scans will be presented.
    2. Assess: **Normal**, **Tumor**, or specify **Other**.
    3. Timing begins immediately upon image load.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Initialize Session"):
            start_countdown()
            st.rerun()

# >>> COUNTDOWN PAGE <<<
elif st.session_state.page == 'countdown':
    placeholder = st.empty()
    for i in [3, 2, 1]:
        placeholder.markdown(f"<div class='countdown-text'>{i}</div>", unsafe_allow_html=True)
        time.sleep(0.8)
    
    placeholder.empty()
    st.session_state.page = 'session'
    st.rerun()

# >>> SESSION PAGE <<<
elif st.session_state.page == 'session':
    if st.session_state.current_index >= len(st.session_state.images):
        st.session_state.page = 'results'
        st.rerun()
    else:
        # Start Timer if not running
        if st.session_state.start_time is None:
            time.sleep(0.1) 
            st.session_state.start_time = time.time()

        # Progress bar
        count_str = f"Case {st.session_state.current_index + 1} / {len(st.session_state.images)}"
        st.progress((st.session_state.current_index) / len(st.session_state.images))
        st.caption(count_str)

        # Image Container
        current_img_file = st.session_state.images[st.session_state.current_index]
        
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            try:
                # In a real scenario, remove the if check if files are guaranteed
                if os.path.exists(current_img_file):
                    st.image(current_img_file, use_container_width=True)
                else:
                    st.warning(f"File {current_img_file} not found (Demo Mode)")
            except:
                st.error("Error loading image.")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- INTERACTION AREA ---
        
        # Check if user clicked 'OTHER' previously
        if st.session_state.custom_mode:
            # Show Text Input Form
            with st.form("custom_diag_form"):
                st.write("Specify Diagnosis:")
                custom_val = st.text_input("Diagnosis", label_visibility="collapsed", placeholder="e.g. Benign, Cyst, Artifact...")
                
                # Form columns
                fc1, fc2 = st.columns([1, 1])
                with fc1:
                    submitted = st.form_submit_button("Confirm Diagnosis")
                with fc2:
                    # Cancel button logic requires a bit of a trick inside a form
                    # simpler to just put it outside or use the form submit to cancel?
                    # We will rely on the user confirming.
                    pass 

            if submitted:
                record_choice(custom_val)
                st.rerun()
                
            # Cancel Button (outside form to function as a reset)
            if st.button("Cancel / Back"):
                st.session_state.custom_mode = False
                st.rerun()

        else:
            # Show Standard Buttons (Normal / Tumor / Other)
            b1, b2, b3 = st.columns(3)
            
            with b1:
                if st.button("Normal"):
                    record_choice("Normal")
                    st.rerun()
            with b2:
                if st.button("Tumor"):
                    record_choice("Tumor")
                    st.rerun()
            with b3:
                if st.button("Other..."):
                    st.session_state.custom_mode = True
                    st.rerun()

# >>> RESULTS PAGE <<<
elif st.session_state.page == 'results':
    st.title("Analysis Complete")
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state.results)
    
    if not df.empty:
        # Calculate Metrics
        avg_time = df['Time_Seconds'].mean()
        
        # Elegant Metric Display
        m1, m2 = st.columns(2)
        m1.metric("Cases", len(df))
        m2.metric("Avg Speed", f"{avg_time:.2f}s")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CSV Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data Report (.csv)",
            data=csv,
            file_name='radiology_report.csv',
            mime='text/csv',
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start New Assessment"):
        go_home()
        st.rerun()

# --- 7. FOOTER ---
st.markdown("""
    <div class='footer'>
        © Rohit Kattimani 2025
    </div>

""", unsafe_allow_html=True)
