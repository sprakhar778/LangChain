import os
import streamlit as st
import asyncio
from io import BytesIO
from generator import BlogPostGenerator
import base64
from io import BytesIO

def load_image_as_base64(image_path):
    """
    Load an image from a file path and encode it as a base64 string.

    Args:
        image_path (str): The file path of the image.

    Returns:
        str: Base64 encoded string of the image.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ------------------------------ UI Styling ------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    /* Global Styling */
    body {
        background: linear-gradient(135deg, #f0f2f5, #ffffff);
        font-family: 'Montserrat', sans-serif;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px;
    }

    /* Header */
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        font-size: 1.5em;
        color: #555;
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
        background-color: #f8f9fa;
        color: #333;
        border: 1px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        font-size: 1.1em;
        resize: none;
    }
    
    /* History Section */
    .history-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
        color: #555;
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
        background-color: rgba(255  , 255, 255, 0.1);">
        Blog Post Generator
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
         Use this tool to generate an <b>AI-powered blog post</b> and image.
    </p>
    """,
    unsafe_allow_html=True
)
# History Toggle

history_enabled = st.sidebar.checkbox("Enable History Log")



# ------------------------------ Title & Subtitle ------------------------------

# Display Hero Image
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
        width: 500px;
        height: 380px;
       
        
    }}
   
   
    </style>

    <div class="hero-section">
        <img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Synthesia Logo">
       
       
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------ User Input ------------------------------
# st.subheader("Enter your topic:")
topic = st.text_input(" ", "Paris Skyline", max_chars=300, key="topic_input")


# ------------------------------ Generate Button ------------------------------
if st.button(" Generate Content"):
    with st.spinner("⏳ Generating... Please wait"):
        generator = BlogPostGenerator()
        try:
            result = asyncio.run(generator.generate(topic))
            st.session_state['generated_text'] = result.get("text", "")
            st.session_state['generated_image'] = result.get("image", None)
            
            # Log history only when "Generate Content" is clicked
            if history_enabled:
                if "history" not in st.session_state:
                    st.session_state["history"] = []

                img_bytes = None
                if st.session_state['generated_image']:
                    buffered = BytesIO()
                    st.session_state['generated_image'].save(buffered, format="PNG")
                    img_bytes = buffered.getvalue()

                st.session_state["history"].append({
                    "topic": topic,
                    "response": st.session_state['generated_text'],
                    "image_bytes": img_bytes  # Store image bytes in history
                })
                
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")

# ------------------------------ Display Blog Content ------------------------------
if "generated_text" in st.session_state:
    st.markdown("### 📄 AI-Generated Blog Post")
    st.write(st.session_state['generated_text'])

# ------------------------------ Display Generated Image ------------------------------
if "generated_image" in st.session_state and st.session_state['generated_image']:
    st.markdown("### 🖼️ AI-Generated Image")
    st.image(st.session_state['generated_image'], caption=f"Generated image for '{topic}'")

    buffered = BytesIO()
    st.session_state['generated_image'].save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    st.download_button(
        label="⬇️ Download Image",
        data=img_bytes,
        file_name="generated_image.png",
        mime="image/png"
    )

# ------------------------------ Display History ------------------------------
if history_enabled and "history" in st.session_state and st.session_state["history"]:
    with st.expander("📜 View Query History"):
        # Create a ZIP file containing the history text and images
        import zipfile
        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            history_text = ""
            for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
                history_text += f"Query {idx}:\nTopic: {entry['topic']}\nResponse:\n{entry['response']}\n\n"
            zip_file.writestr("query_history.txt", history_text)

            # Add images from history if available
            for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
                if entry["image_bytes"]:
                    image_filename = f"history_image_{idx}.png"
                    zip_file.writestr(image_filename, entry["image_bytes"])
        zip_buffer.seek(0)
        
        st.download_button(
            label="⬇️ Download History (Text & Images)",
            data=zip_buffer,
            file_name="query_history.zip",
            mime="application/zip"
        )

        # Display the history log
        for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
            st.markdown(f"**Query {idx}:**")
            st.write(f"**Topic:** {entry['topic']}")
            st.write(f"**Response:** {entry['response']}")
            if entry["image_bytes"]:
                st.image(BytesIO(entry["image_bytes"]), caption=f"Image for '{entry['topic']}'")
            st.markdown("---")

# ------------------------------ Footer ------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="footer" style="text-align: center; padding: 10px; margin-top: 20px; font-size: 0.9em; color: #d3d3d3;">
      Developed using <a href="https://github.com/hwchase17/langchain" target="_blank" style="color: #007bff; text-decoration: none;">LangChain</a> & 
      <a href="https://cloud.google.com/vertex-ai" target="_blank" style="color: #007bff; text-decoration: none;">Vertex AI</a>.
    </div>
    """, unsafe_allow_html=True
)