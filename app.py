import streamlit as st
import random
import os
import whisper
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from st_audiorec import st_audiorec
import time
from gtts import gTTS
import base64
from datetime import datetime
from difflib import SequenceMatcher

# Load environment variables for API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Whisper model once
whisper_model = whisper.load_model("base")

PICTURE_FOLDER = "pictures"
PROGRESS_FILE = "progress_data.json"

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'description'  # description -> story_generated -> practice
if 'errors' not in st.session_state:
    st.session_state.errors = []
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'story' not in st.session_state:
    st.session_state.story = ""
if 'picture_file' not in st.session_state:
    st.session_state.picture_file = None
if 'picture_subject' not in st.session_state:
    st.session_state.picture_subject = ""
if 'story_sections' not in st.session_state:
    st.session_state.story_sections = []
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'section_attempts' not in st.session_state:
    st.session_state.section_attempts = {}
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()

def get_random_picture():
    pictures = os.listdir(PICTURE_FOLDER)
    if not pictures:
        return None, ""
    idx = random.randint(0, len(pictures) - 1)
    picture_file = pictures[idx]
    subject = os.path.splitext(picture_file)[0]
    return picture_file, subject

def detect_errors(transcript):
    prompt = f"""
You are a speech therapist helping a child aged 4-6 years. 
Analyze the following child's sentence for errors:

\"{transcript}\"

Identify:
1. Grammar errors and corrections
2. Vocabulary errors and corrections
3. Simple articulation errors that can be inferred from the text

Return a JSON array. Each element must include:
- type: "grammar" or "vocabulary" or "articulation"
- incorrect: the incorrect phrase
- correction: the corrected phrase
- explanation: short child-friendly explanation (max 15 words)

Return ONLY the JSON array (empty if no errors).
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing AI response as JSON: {e}")
        return []
    except Exception as e:
        st.error(f"Error calling AI: {e}")
        return []

def generate_story(subject, errors, transcript):
    if not errors or len(errors) == 0:
        error_description = "No specific errors were detected, so create a simple engaging story."
    else:
        error_list = []
        for err in errors:
            error_list.append(f"- {err.get('type', 'error')}: '{err.get('incorrect', '')}' should be '{err.get('correction', '')}'")
        error_description = "The child made these errors:\n" + "\n".join(error_list)
    
    prompt = f"""
You are a creative children's story writer and speech therapist.

Create a SHORT story (3 sentences) for a 4-6 year old child about: {subject}

IMPORTANT REQUIREMENTS:
1. The story MUST naturally incorporate and repeatedly use the words/sounds the child struggled with
2. Make the story engaging, fun, and age-appropriate, and mostly with simple words adapted for young children.
3. {error_description}
4. Use simple vocabulary but strategically include the correction words from the errors
5. Break the story into very short sections (1-2 sentences each) separated by a pipe symbol |

The child said: "{transcript}"

Generate the story with sections separated by | (pipe symbol).
Example format: "Once upon a time, there was a happy dog. | The dog loved to play. | One day, the dog found a ball."

Return ONLY the story text with | separators, no other commentary.
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        story = response.text.strip()
        
        if story.startswith('```'):
            lines = story.split('\n')
            story = '\n'.join(lines[1:-1])
        
        return story
    except Exception as e:
        st.error(f"Error generating story: {e}")
        return ""

def text_to_speech(text, filename="temp_audio.mp3"):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")
        return None

def calculate_accuracy(original, spoken):
    """Calculate similarity between original text and spoken text"""
    original = original.lower().strip()
    spoken = spoken.lower().strip()
    return SequenceMatcher(None, original, spoken).ratio() * 100

def save_progress(session_data):
    """Save session progress to JSON file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {"sessions": []}
        
        data["sessions"].append(session_data)
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving progress: {e}")

def load_progress():
    """Load progress data from JSON file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return {"sessions": []}
    except Exception as e:
        st.error(f"Error loading progress: {e}")
        return {"sessions": []}

def display_error_table(errors):
    """Display error table in a formatted way"""
    if errors and len(errors) > 0:
        df = pd.DataFrame(errors)
        required_cols = ["type", "incorrect", "correction", "explanation"]
        available_cols = [col for col in required_cols if col in df.columns]
        if available_cols:
            df = df[available_cols]
            df.columns = ["Type", "What you said", "Let's try", "Tip"]
            st.table(df)
    else:
        st.info("No errors detected in this session")

# Main UI
st.title("Child Speech Therapy Assistant")

# Sidebar for progress tracking
with st.sidebar:
    st.header("Progress Tracking")
    progress_data = load_progress()
    
    if progress_data["sessions"]:
        st.metric("Total Sessions", len(progress_data["sessions"]))
        
        # Calculate average accuracy
        accuracies = [s.get("average_accuracy", 0) for s in progress_data["sessions"]]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
        
        # Show recent sessions
        st.subheader("Recent Sessions")
        for i, session in enumerate(reversed(progress_data["sessions"][-5:])):
            with st.expander(f"📅 {session.get('date', 'Unknown')}"):
                st.write(f"**Subject:** {session.get('subject', 'N/A')}")
                st.write(f"**Accuracy:** {session.get('average_accuracy', 0):.1f}%")
                st.write(f"**Errors Found:** {session.get('initial_errors', 0)}")
                st.write(f"**Sections Completed:** {session.get('sections_completed', 0)}")
                
                # Show errors table
                if session.get('initial_errors', 0) > 0:
                    st.markdown("---")
                    st.markdown("**Error Details:**")
                    error_details = session.get('errors_detail', [])
                    display_error_table(error_details)
    else:
        st.info("No sessions yet. Start practicing!")

# Main content area
st.markdown("---")

# Stage 1: Picture Description
if st.session_state.stage == 'description':
    st.header("Describe the Picture")
    
    if st.session_state.picture_file is None:
        st.session_state.picture_file, st.session_state.picture_subject = get_random_picture()
    
    if st.session_state.picture_file:
        st.image(os.path.join(PICTURE_FOLDER, st.session_state.picture_file), 
                caption=f"What do you see?", width=400)
        st.info(f"Picture: {st.session_state.picture_subject.title()}")
    else:
        st.warning("Please add images to the 'pictures' folder (dog.jpg, cat.jpg, dolphin.jpg, car.jpg, rainbow.jpg)")
        st.stop()
    
    st.markdown("### Tell me about this picture!")
    
    audio_bytes = st_audiorec()
    
    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")
        
        audio_path = "child_description.wav"
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        
        st.success("✅ Audio recorded!")
        
        with st.spinner("Understanding what you said..."):
            whisper_result = whisper_model.transcribe(audio_path)
            st.session_state.transcript = whisper_result.get("text", "").strip()
        
        st.markdown(f"**You said:** *{st.session_state.transcript}*")
        
        if st.session_state.transcript:
            with st.spinner("Checking for improvements..."):
                st.session_state.errors = detect_errors(st.session_state.transcript)
            
            if st.session_state.errors and len(st.session_state.errors) > 0:
                st.subheader("Let's work on these:")
                display_error_table(st.session_state.errors)
            else:
                st.success("Perfect! Great speaking!")
            
            # Automatically generate story
            with st.spinner("Creating your practice story..."):
                st.session_state.story = generate_story(
                    st.session_state.picture_subject,
                    st.session_state.errors,
                    st.session_state.transcript
                )
                
                if st.session_state.story:
                    st.session_state.story_sections = [s.strip() for s in st.session_state.story.split('|') if s.strip()]
                    st.session_state.stage = 'story_generated'
                    st.session_state.current_section = 0
                    st.session_state.section_attempts = {}
                    time.sleep(1)
                    st.rerun()

# Stage 2: Story Display and Practice
elif st.session_state.stage == 'story_generated':
    st.header(f"Story Time: {st.session_state.picture_subject.title()}")
    
    # Display error table at the top if there are errors
    if st.session_state.errors and len(st.session_state.errors) > 0:
        with st.expander("Areas to Focus On", expanded=False):
            st.markdown("These are the areas we're working on in this story:")
            display_error_table(st.session_state.errors)
        st.markdown("---")
    
    # Display full story
    st.markdown("#### Your Practice Story:")
    st.markdown(
        f"""
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 2px solid #4CAF50;">
            <p style="font-size: 18px; line-height: 1.8; color: #333;">
                {st.session_state.story.replace('|', '<br><br>')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("### Practice Each Line")
    
    if st.session_state.current_section < len(st.session_state.story_sections):
        current_text = st.session_state.story_sections[st.session_state.current_section]
        section_key = f"section_{st.session_state.current_section}"
        
        # Progress indicator
        progress = (st.session_state.current_section) / len(st.session_state.story_sections)
        st.progress(progress)
        st.caption(f"Section {st.session_state.current_section + 1} of {len(st.session_state.story_sections)}")
        
        # Highlight error words in current section
        highlighted_text = current_text
        error_words = []
        if st.session_state.errors:
            for err in st.session_state.errors:
                correction = err.get('correction', '').lower()
                if correction and correction in current_text.lower():
                    error_words.append(correction)
                    highlighted_text = highlighted_text.replace(
                        correction,
                        f'<span style="background-color: #ffeb3b; font-weight: bold; padding: 2px 4px; border-radius: 3px;">{correction}</span>'
                    )
        
        # Display current section
        st.markdown(
            f"""
            <div style="background-color: #e3f2fd; padding: 25px; border-radius: 10px; border: 3px solid #2196F3; margin: 20px 0;">
                <p style="font-size: 24px; line-height: 2; color: #1565C0; font-weight: 500;">
                    {highlighted_text}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if error_words:
            st.warning(f"Focus on: **{', '.join(set(error_words))}**")
        
        # Listen button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Listen", key=f"listen_{section_key}", use_container_width=True):
                audio_file = text_to_speech(current_text, f"{section_key}.mp3")
                if audio_file:
                    st.audio(audio_file)
        
        with col2:
            st.markdown("**Now you read it!**")
        
        # Record child's attempt
        st.markdown("### Record yourself reading this line:")
        practice_audio = st_audiorec()
        
        if practice_audio is not None:
            st.audio(practice_audio, format="audio/wav")
            
            practice_path = f"practice_{section_key}.wav"
            with open(practice_path, "wb") as f:
                f.write(practice_audio)
            
            with st.spinner("Checking your reading..."):
                practice_result = whisper_model.transcribe(practice_path)
                practice_transcript = practice_result.get("text", "").strip()
            
            st.markdown(f"**You said:** *{practice_transcript}*")
            
            # Calculate accuracy
            accuracy = calculate_accuracy(current_text, practice_transcript)
            
            # Store attempt
            if section_key not in st.session_state.section_attempts:
                st.session_state.section_attempts[section_key] = []
            
            st.session_state.section_attempts[section_key].append({
                'transcript': practice_transcript,
                'accuracy': accuracy,
                'timestamp': datetime.now().isoformat()
            })
            
            # Show accuracy
            if accuracy >= 80:
                st.success(f"🌟 Excellent! Accuracy: {accuracy:.1f}%")
                if st.button("➡️ Next Line", type="primary", use_container_width=True):
                    st.session_state.current_section += 1
                    st.rerun()
            elif accuracy >= 60:
                st.warning(f"👍 Good try! Accuracy: {accuracy:.1f}% - Try again to improve!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Try Again", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("➡️ Next Line", use_container_width=True):
                        st.session_state.current_section += 1
                        st.rerun()
            else:
                st.error(f"💪 Keep practicing! Accuracy: {accuracy:.1f}%")
                st.info("Tip: Listen again and speak slowly and clearly!")
                if st.button("🔄 Try Again", type="primary", use_container_width=True):
                    st.rerun()
    
    else:
        # Session complete
        st.success("🎉 Congratulations! You completed the story!")
        st.balloons()
        
        # Calculate session statistics
        total_attempts = sum(len(attempts) for attempts in st.session_state.section_attempts.values())
        all_accuracies = []
        for attempts in st.session_state.section_attempts.values():
            all_accuracies.extend([a['accuracy'] for a in attempts])
        
        avg_accuracy = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0
        
        # Display session summary
        st.markdown("### 📊 Session Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sections", len(st.session_state.story_sections))
        with col2:
            st.metric("Total Attempts", total_attempts)
        with col3:
            st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
        with col4:
            st.metric("Initial Errors", len(st.session_state.errors))
        
        # Save progress
        session_data = {
            'date': st.session_state.session_start.strftime("%Y-%m-%d %H:%M:%S"),
            'subject': st.session_state.picture_subject,
            'initial_errors': len(st.session_state.errors),
            'errors_detail': st.session_state.errors,
            'sections_completed': len(st.session_state.story_sections),
            'total_attempts': total_attempts,
            'average_accuracy': avg_accuracy,
            'section_attempts': st.session_state.section_attempts
        }
        save_progress(session_data)
        
        # Show detailed progress
        st.markdown("### 📈 Detailed Progress")
        progress_df = []
        for section_idx, (key, attempts) in enumerate(st.session_state.section_attempts.items()):
            best_accuracy = max([a['accuracy'] for a in attempts])
            progress_df.append({
                'Section': section_idx + 1,
                'Attempts': len(attempts),
                'Best Accuracy': f"{best_accuracy:.1f}%"
            })
        
        if progress_df:
            st.dataframe(pd.DataFrame(progress_df), use_container_width=True)
        
        # Reset button
        if st.button("🔄 Start New Session", type="primary", use_container_width=True):
            st.session_state.stage = 'description'
            st.session_state.errors = []
            st.session_state.transcript = ""
            st.session_state.story = ""
            st.session_state.picture_file = None
            st.session_state.picture_subject = ""
            st.session_state.story_sections = []
            st.session_state.current_section = 0
            st.session_state.section_attempts = {}
            st.session_state.session_start = datetime.now()
            st.rerun()