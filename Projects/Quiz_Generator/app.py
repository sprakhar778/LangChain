import os
import streamlit as st
st.set_page_config(layout="wide")
import base64
import zipfile
import io
from io import BytesIO

# Import the study material generator
from model import StudyMaterialGenerator

# ------------------------------ Utility Functions ------------------------------
def load_image_as_base64(image_path):
    """
    Load an image from a file path and encode it as a base64 string.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ------------------------------ UI Styling ------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    /* Global Styling for Dark Mode */
    body {
        background: #121212;
        font-family: 'Montserrat', sans-serif;
        color: #e0e0e0;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin: 20px;
    }

    /* Header */
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .subtitle {
        text-align: center;
        font-size: 1.5em;
        color: #bbbbbb;
        margin-bottom: 40px;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 15px 25px;
        border-radius: 8px;
        font-size: 1.2em;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
    }
    div.stButton > button:hover {
        color: #ffffff !important;
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgba(0,123,255,0.3);
    }

    /* Text Areas */
    .stTextArea textarea {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        font-size: 1.1em;
        resize: none;
    }
    
    /* Generated Material Boxes */
    .generated-box {
        background-color: #1e1e1e;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        font-size: 1.2em;
        color: #e0e0e0;
    }
    
    /* History Section */
    .history-box {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .history-box:hover {
        transform: translateY(-5px);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.9rem;
        color: #bbbbbb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------ Sidebar ------------------------------
st.sidebar.markdown(
    """
    <h2 style="
        text-align: center;
        color: #00AEEF; 
        font-family: 'Poppins', sans-serif;
        font-size: 24px;
        font-weight: bold;
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.1);">
        Study Material Generator
    </h2>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown(
    """
    <p style="
        text-align: center;
        color: #ffffff; 
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        font-weight: 400;
        margin-top: 10px;">
         Use this tool to generate <b>AI-powered study material</b> including explanation, notes, quiz, and key takeaways.
    </p>
    """,
    unsafe_allow_html=True
)

# History Toggle
history_enabled = st.sidebar.checkbox("Enable History Log", value=True)

# ------------------------------ Title & Hero Section ------------------------------
# Display Hero Image (ensure you have a logo.png in your app folder)
logo_base64 = load_image_as_base64("logo.png")
st.markdown(
    f"""
    <style>
    .hero-section {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 40px;
    }}
    .logo-image {{
        width: 200px;
        height: auto;
    }}
    </style>

    <div class="hero-section">
        <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Logo">
        <h1 class="title">Study Material Generator</h1>
        <p class="subtitle">Generate clear explanations, notes, quizzes, and key takeaways on any topic.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------ User Input ------------------------------

topic = st.text_input("Topic", "Newton's Laws", max_chars=300, key="topic_input")

# ------------------------------ Generate Button ------------------------------
if st.button("Generate Study Material"):
    with st.spinner("⏳ Generating study material..."):
        try:
            generator = StudyMaterialGenerator()
            # Generate study material as a list:
            # Index 0: Explanation, 1: Notes, 2: Quiz, 3: Key Takeaway
            material = generator.generate_study_material(topic)
            st.session_state['generated_material'] = material

            # Log history if enabled
            if history_enabled:
                if "history" not in st.session_state:
                    st.session_state["history"] = []
                st.session_state["history"].append({
                    "topic": topic,
                    "explanation": material[0],
                    "notes": material[1],
                    "quiz": material[2],
                    "key_takeaway": material[3]
                })
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")

# ------------------------------ Display Generated Study Material ------------------------------
if "generated_material" in st.session_state:
    material = st.session_state['generated_material']
    
    st.markdown("### 📚 Explanation")
    st.markdown(f"<div class='generated-box'>{material[0]}</div>", unsafe_allow_html=True)
    
    st.markdown("### 📝 Notes")
    st.markdown(f"<div class='generated-box'>{material[1]}</div>", unsafe_allow_html=True)
    
    st.markdown("### ❓ Quiz")
    st.markdown(f"<div class='generated-box'>{material[2]}</div>", unsafe_allow_html=True)
    
    st.markdown("### 🔑 Key Takeaway")
    st.markdown(f"<div class='generated-box'>{material[3]}</div>", unsafe_allow_html=True)

# ------------------------------ Display History ------------------------------
if history_enabled and "history" in st.session_state and st.session_state["history"]:
    with st.expander("📜 View Query History"):
        # Create a ZIP file containing the history text
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            history_text = ""
            for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
                history_text += (
                    f"Query {idx}:\n"
                    f"Topic: {entry['topic']}\n\n"
                    f"Explanation:\n{entry['explanation']}\n\n"
                    f"Notes:\n{entry['notes']}\n\n"
                    f"Quiz:\n{entry['quiz']}\n\n"
                    f"Key Takeaway:\n{entry['key_takeaway']}\n"
                    "-------------------------\n\n"
                )
            zip_file.writestr("query_history.txt", history_text)
        zip_buffer.seek(0)
        
        st.download_button(
            label="⬇️ Download History (Text)",
            data=zip_buffer,
            file_name="query_history.zip",
            mime="application/zip"
        )
        
        # Display each history entry
        for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
            st.markdown(f"<div class='history-box'><strong>Query {idx}:</strong><br>"
                        f"<strong>Topic:</strong> {entry['topic']}<br>"
                        f"<strong>Explanation:</strong> {entry['explanation']}<br>"
                        f"<strong>Notes:</strong> {entry['notes']}<br>"
                        f"<strong>Quiz:</strong> {entry['quiz']}<br>"
                        f"<strong>Key Takeaway:</strong> {entry['key_takeaway']}</div>", 
                        unsafe_allow_html=True)
            st.markdown("---")

# ------------------------------ Footer ------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="footer" style="text-align: center; padding: 10px; margin-top: 20px;">
      Developed using <a href="https://github.com/hwchase17/langchain" target="_blank" style="color: #007bff; text-decoration: none;">LangChain</a>.
    </div>
    """,
    unsafe_allow_html=True
)
