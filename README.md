🎙️ StoryWeaver
A Generative-AI Powered Speech Therapy Platform for Children (Ages 4–6)

StoryWeaver is an interactive speech-therapy assistant that helps young children practice articulation, grammar, and vocabulary through AI-generated stories. It listens to a child describe a picture, detects errors in real time, and builds a personalized story that teaches correct speech through fun narrative practice.

🚀 Features

🎧 Real-Time Speech Recognition
- Powered by OpenAI Whisper
- Handles child speech variations
- Works with moderate background noise

🔍 Automated Error Detection
- Uses Google Gemini 2.5-Flash
- Detects:
  - Grammar mistakes
  - Vocabulary errors
  - Simple articulation patterns
- Returns child-friendly corrections

📚 Personalized Story Generation
- Story is generated based on:
  - Picture subject
  - Detected errors
  - Age-appropriate vocabulary
- Story is split into short sections using the "|" separator

🎤 Interactive Practice
- System narrates each story section
- Child records their reading
- Whisper re-checks pronunciation
- Accuracy score generated
- Retry or advance based on performance

📊 Progress Dashboard
- Tracks:
  - Total sessions
  - Average accuracy
  - Errors per session
  - Sections completed
- Saves all session data in JSON

🧠 Tech Stack
Component: Technology
Frontend: Streamlit
ASR: Whisper (OpenAI)
NLP / Story Generation: Gemini 2.5-Flash
Text-to-Speech: gTTS
Storage: JSON
Audio Recorder: st_audiorec

📂 Project Structure
📦 StoryWeaver
 ┣ 📁 pictures
 ┣ 📄 app.py
 ┣ 📄 progress_data.json
 ┣ 📄 README.md
 ┗ 📄 requirements.txt

🛠️ Installation & Setup

1. Clone the repository
   git clone https://github.com/your-username/StoryWeaver.git
   cd StoryWeaver

2. Install dependencies
   pip install -r requirements.txt

3. Add your Google API key
   Create a .env file:
   GOOGLE_API_KEY=your_api_key_here

4. Run the application
   streamlit run app.py

📌 requirements.txt
streamlit
openai-whisper
google-generativeai
pandas
gtts
python-dotenv
st-audiorec

📌 How It Works
- Child sees a picture
- Child describes it
- Whisper → text
- Gemini → error detection
- Gemini → story generation
- Story displayed with highlighted correction words
- Child practices reading each section
- Whisper evaluates accuracy
- Session saved in JSON

🔒 Privacy & Safety
- All processing is local
- No external upload of child's voice
- JSON-based storage only
- Safe for early-childhood educational use

✨ Authors
- Roshan A Rauof – 22BAI1041
- Reem Fariha – 22BAI1454

📜 License
MIT License
