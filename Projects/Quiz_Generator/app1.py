import os
import streamlit as st
import base64
import zipfile
import io
import json
from io import BytesIO
from model import StudyMaterialGenerator

# ------------------------------ Utility Functions ------------------------------
def load_image_as_base64(image_path):
    """Load an image from a file path and encode it as a base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def render_quiz(quiz_data, attempt=1):
    """Render quiz questions with radio buttons for answers."""
    user_answers = {}
    
    # Get previous answers if they exist
    previous_answers = st.session_state.get(f'quiz_attempt_{attempt-1}', {}) if attempt > 1 else {}
    
    for idx, q in enumerate(quiz_data, 1):
        st.markdown(f"**{idx}. {q['question']}**")
        default_index = None
        
        # If there's a previous answer for this question, find its index to set as default
        if idx in previous_answers:
            try:
                if previous_answers[idx].isalpha():  # If it's a letter (A, B, C...)
                    default_index = ord(previous_answers[idx].upper()) - ord('A')
                else:  # It's the full text answer
                    default_index = q['options'].index(previous_answers[idx])
            except (ValueError, IndexError):
                default_index = None
        
        # Add option letters to each choice
        options_with_letters = [f"{chr(65+i)}. {option}" for i, option in enumerate(q['options'])]
                
        selected_option = st.radio(
            f"Select the correct answer for Question {idx}",
            options_with_letters,
            index=default_index,
            key=f"q{idx}_attempt{attempt}"
        )
        
        # Store just the letter (A, B, C...) as the answer
        user_answers[idx] = selected_option.split('.')[0]
    
    return user_answers

def format_quiz_for_history(quiz_data):
    """Format quiz data for better readability in history."""
    formatted = []
    for idx, q in enumerate(quiz_data, 1):
        formatted.append(f"{idx}. {q['question']}")
        for i, option in enumerate(q['options']):
            formatted.append(f"   {chr(65+i)}. {option}")
        
        # Convert the answer to a letter if it's not already
        answer = q['answer']
        if not answer.isalpha():
            try:
                answer_index = q['options'].index(answer)
                answer = chr(65 + answer_index)
            except (ValueError, IndexError):
                answer = "Unknown"
                
        formatted.append(f"   Answer: {answer}")
        formatted.append("")
    return "\n".join(formatted)

def format_quiz_solution(solution_text):
    """Format quiz solution for better readability."""
    # Handle case where solution_text might be an AIMessage or other object
    if hasattr(solution_text, 'content'):
        solution_text = solution_text.content
    
    # Ensure solution_text is a string
    if not isinstance(solution_text, str):
        solution_text = str(solution_text)
        
    lines = solution_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a question number
        if line and line[0].isdigit() and '.' in line.split()[0]:
            formatted_lines.append(f"\n**{line}**")
        else:
            formatted_lines.append(line)
            
    return "\n".join(formatted_lines)

def get_answer_letter(quiz_item, answer_text):
    """Convert an answer text to its corresponding letter option."""
    try:
        # If the answer is already a letter (A, B, C, etc.)
        if answer_text.isalpha() and len(answer_text) == 1:
            return answer_text.upper()
            
        # If the answer is the full text, find its index and convert to letter
        index = quiz_item['options'].index(answer_text)
        return chr(65 + index)
    except (ValueError, IndexError):
        return "?"  # Return a placeholder if we can't determine the letter

# ------------------------------ UI Styling ------------------------------
st.set_page_config(layout="wide")
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

    /* Quiz Attempt Tag */
    .attempt-tag {
        display: inline-block;
        padding: 5px 10px;
        background-color: #007bff;
        color: white;
        border-radius: 15px;
        font-size: 0.8em;
        margin-bottom: 15px;
    }

    /* Score Display */
    .score-display {
        font-size: 1.5em;
        text-align: center;
        padding: 15px;
        margin: 20px 0;
        background-color: #1e1e1e;
        border-radius: 10px;
        border-left: 5px solid #007bff;
    }

    /* Quiz Result Item */
    .quiz-result-correct {
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        background-color: rgba(0, 128, 0, 0.2);
        border-left: 3px solid #00ff00;
    }
    .quiz-result-incorrect {
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        background-color: rgba(255, 0, 0, 0.2);
        border-left: 3px solid #ff0000;
    }

    /* Solution Box */
    .solution-box {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        color: #e0e0e0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1e1e1e;
        border-radius: 5px 5px 0 0;
        border: 1px solid #333;
        border-bottom: none;
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007bff !important;
        color: white !important;
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

# Quiz Attempts Setting
max_attempts = st.sidebar.slider("Maximum Quiz Attempts", min_value=1, max_value=5, value=3)

# ------------------------------ Title & Hero Section ------------------------------
# Display Hero Image (ensure you have a logo.png in your app folder)
try:
    logo_base64 = load_image_as_base64("logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-image" alt="Logo">'
except:
    logo_html = '<div style="height: 100px;"></div>'  # Placeholder if image doesn't exist

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
        {logo_html}
        <h1 class="title">Study Material Generator</h1>
        <p class="subtitle">Generate clear explanations, notes, quizzes, and key takeaways on any topic.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------ User Input ------------------------------
topic = st.text_input("Enter the topic:", "Newton's Laws", max_chars=300, key="topic_input")

# ------------------------------ Generate Button ------------------------------
if st.button("Generate Study Material"):
    with st.spinner("⏳ Generating..."):
        try:
            generator = StudyMaterialGenerator()
            material = generator.generate_study_material(topic)
            
            # Handle different types of returns from the generator
            # Ensure each element is converted to string if needed
            explanation = material[0].content if hasattr(material[0], 'content') else str(material[0])
            notes = material[1].content if hasattr(material[1], 'content') else str(material[1])
            quiz = material[2]
            solution = material[3].content if hasattr(material[3], 'content') else str(material[3])
            
            # Process quiz answer format: ensure each question has the correct answer in letter form
            for q in quiz:
                if 'answer' in q and not q['answer'].isalpha():
                    q['answer'] = get_answer_letter(q, q['answer'])
            
            st.session_state['generated_material'] = [explanation, notes, quiz, solution]
            
            # Reset quiz attempts and scores
            if 'current_attempt' in st.session_state:
                del st.session_state['current_attempt']
            
            for i in range(1, max_attempts + 1):
                if f'quiz_attempt_{i}' in st.session_state:
                    del st.session_state[f'quiz_attempt_{i}']
                    
            if 'quiz_completed' in st.session_state:
                del st.session_state['quiz_completed']
                
            # Set current attempt to 1
            st.session_state['current_attempt'] = 1

            # Log history if enabled
            if history_enabled:
                if "history" not in st.session_state:
                    st.session_state["history"] = []
                
                formatted_quiz = format_quiz_for_history(quiz)
                formatted_solution = format_quiz_solution(solution)
                
                st.session_state["history"].append({
                    "topic": topic,
                    "explanation": explanation,
                    "notes": notes,
                    "quiz": formatted_quiz,
                    "quiz_solution": formatted_solution,
                    "timestamp": "Current Session"
                })
                
            st.success("✅ Study material generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            st.error("Please check the model.py implementation to ensure it returns proper data")

# ------------------------------ Display Generated Material ------------------------------
if "generated_material" in st.session_state:
    material = st.session_state['generated_material']
    
    # Initialize current_attempt if not exists
    if 'current_attempt' not in st.session_state:
        st.session_state['current_attempt'] = 1

    tabs = st.tabs(["📚 Explanation", "📝 Notes", "❓ Quiz", "📜 History"])
    
    with tabs[0]:
        st.markdown(f"<div class='generated-box'>{material[0]}</div>", unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown(f"<div class='generated-box'>{material[1]}</div>", unsafe_allow_html=True)
    
    with tabs[2]:
        current_attempt = st.session_state['current_attempt']
        
        # Show attempt counter
        st.markdown(f"<div class='attempt-tag'>Attempt {current_attempt} of {max_attempts}</div>", unsafe_allow_html=True)
        
        # Check if quiz has been completed
        quiz_completed = st.session_state.get('quiz_completed', False)
        
        if not quiz_completed and current_attempt <= max_attempts:
            # Render quiz for current attempt
            user_answers = render_quiz(material[2], current_attempt)
            
            col1, col2 = st.columns([1, 5])
            
            with col1:
                # Submit button for quiz
                if st.button("Submit Quiz"):
                    # Save the answers for the current attempt
                    st.session_state[f'quiz_attempt_{current_attempt}'] = user_answers
                    # Don't auto-increment the attempt counter here
                    st.rerun()
            
            with col2:
                # Reset button (only show if at least one attempt was made)
                if current_attempt > 1 and st.button("Reset Quiz"):
                    for i in range(1, max_attempts + 1):
                        if f'quiz_attempt_{i}' in st.session_state:
                            del st.session_state[f'quiz_attempt_{i}']
                    
                    if 'quiz_completed' in st.session_state:
                        del st.session_state['quiz_completed']
                        
                    st.session_state['current_attempt'] = 1
                    st.rerun()
            
        # Display results if an attempt was submitted
        if f'quiz_attempt_{current_attempt}' in st.session_state:
            user_answers = st.session_state[f'quiz_attempt_{current_attempt}']
            
            correct_answers = 0
            total_questions = len(material[2])  # Use length of quiz data
            
            st.markdown("### 🎯 Quiz Results")
            
            # Check answers for the current attempt
            for idx, q in enumerate(material[2], 1):
                correct_option_letter = q['answer'].upper()
                user_answer_letter = user_answers.get(idx, "").upper()
                
                # Get the full text of the options for display
                correct_option_text = q['options'][ord(correct_option_letter) - ord('A')] if ord(correct_option_letter) - ord('A') < len(q['options']) else "Unknown"
                
                if user_answer_letter == correct_option_letter:
                    correct_answers += 1
                    st.markdown(f"<div class='quiz-result-correct'>✅ Q{idx}: Correct - Your answer: {user_answer_letter}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='quiz-result-incorrect'>❌ Q{idx}: Incorrect - Your answer: {user_answer_letter}, Correct: {correct_option_letter}</div>", unsafe_allow_html=True)
            
            score = (correct_answers / total_questions) * 100
            st.markdown(f"<div class='score-display'>Score: {correct_answers} / {total_questions} ({score:.1f}%)</div>", unsafe_allow_html=True)
            
            # Determine if quiz is completed or not
            if current_attempt >= max_attempts or score == 100:
                st.session_state['quiz_completed'] = True
                
                # Show complete solution when quiz is completed
                st.markdown("### 📝 Complete Solution")
                st.markdown(f"<div class='solution-box'>{format_quiz_solution(material[3])}</div>", unsafe_allow_html=True)
            else:
                # Offer next attempt only if quiz not completed
                if st.button("Try Next Attempt"):
                    st.session_state['current_attempt'] += 1
                    st.rerun()
    
    # ------------------------------ History Tab ------------------------------
    with tabs[3]:
        if history_enabled and "history" in st.session_state and st.session_state["history"]:
            st.markdown("### 📜 Study Session History")
            
            # Create download button for history
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                history_data = []
                for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
                    # Ensure all values are strings
                    history_data.append({
                        "id": idx,
                        "topic": entry['topic'],
                        "timestamp": entry.get('timestamp', 'Unknown'),
                        "content": {
                            "explanation": str(entry['explanation']),
                            "notes": str(entry['notes']),
                            "quiz": str(entry['quiz']),
                            "quiz_solution": str(entry['quiz_solution'])
                        }
                    })
                
                # Add formatted text file
                history_text = ""
                for entry in history_data:
                    history_text += (
                        f"=== STUDY SESSION {entry['id']} ===\n"
                        f"Topic: {entry['topic']}\n"
                        f"Timestamp: {entry['timestamp']}\n\n"
                        f"--- EXPLANATION ---\n{entry['content']['explanation']}\n\n"
                        f"--- NOTES ---\n{entry['content']['notes']}\n\n"
                        f"--- QUIZ ---\n{entry['content']['quiz']}\n\n"
                        f"--- QUIZ SOLUTION ---\n{entry['content']['quiz_solution']}\n"
                        f"=================================\n\n"
                    )
                zip_file.writestr("study_history.txt", history_text)
                
                # Add JSON file for structured data
                zip_file.writestr("study_history.json", json.dumps(history_data, indent=2))
                
            zip_buffer.seek(0)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.download_button(
                    label="⬇️ Download History",
                    data=zip_buffer,
                    file_name="study_history.zip",
                    mime="application/zip"
                )
            
            # Display each history entry
            for idx, entry in enumerate(reversed(st.session_state["history"]), 1):
                with st.expander(f"Study Session {idx}: {entry['topic']}"):
                    st.markdown(f"**Topic:** {entry['topic']}")
                    st.markdown(f"**Timestamp:** {entry.get('timestamp', 'Unknown')}")
                    
                    sub_tabs = st.tabs(["Explanation", "Notes", "Quiz", "Solution"])
                    
                    with sub_tabs[0]:
                        st.markdown(str(entry['explanation']))
                    
                    with sub_tabs[1]:
                        st.markdown(str(entry['notes']))
                    
                    with sub_tabs[2]:
                        st.markdown(f"```\n{str(entry['quiz'])}\n```")
                    
                    with sub_tabs[3]:
                        st.markdown(str(entry['quiz_solution']))
        else:
            st.info("No history available yet. Generate study material to start building your history.")

# ------------------------------ Footer ------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="footer" style="text-align: center; padding: 10px; margin-top: 20px;">
      Developed using <a href="https://github.com/hwchase17/langchain" target="_blank" style="color: #007bff; text-decoration: none;">LangChain</a> and <a href="https://streamlit.io" target="_blank" style="color: #007bff; text-decoration: none;">Streamlit</a>.
    </div>
    """,
    unsafe_allow_html=True
)