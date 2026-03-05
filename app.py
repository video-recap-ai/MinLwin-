import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

# --- Configuration ---
# API Key ကို နေရာလွတ်ထားပေးထားပါတယ်။ အသုံးပြုသူက UI ကနေ ထည့်သွင်းရပါမယ်။
st.set_page_config(page_title="Video Recap AI (Myanmar)", page_icon="🎥", layout="centered")

# Custom CSS for UI
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4A90E2;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎥 Video Recap AI")
st.subheader("ဗီဒီယိုများကို မြန်မာလို အနှစ်ချုပ်ပြီး အသံနားထောင်မယ်")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key ကို ထည့်ပါ:", type="password")
    st.info("API Key ကို Google AI Studio တွင် အခမဲ့ရယူနိုင်ပါသည်။")

def process_video(video_path, api_key):
    """Gemini API ကို သုံးပြီး ဗီဒီယိုကို ခွဲခြမ်းစိတ်ဖြာသည်။"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        # ဗီဒီယိုဖိုင်ကို Upload တင်ခြင်း
        st.info("ဗီဒီယိုကို AI ထံ ပေးပို့နေသည်... ခေတ္တစောင့်ပါ။")
        video_file = genai.upload_file(path=video_path)
        
        prompt = """
        Context: မင်းက AI Video Analyst တစ်ယောက်ဖြစ်တယ်။ ငါပေးတဲ့ Video file ကို လေ့လာပြီး အောက်ပါအတိုင်း လုပ်ဆောင်ပေးပါ။
        Instructions:
         * Transcribe & Summarize: Video ထဲက စကားပြောတွေကို စာသားပြောင်းပါ။ ပြီးရင် အဓိက အချက် ၅ ချက်ကို ခေါင်းစဉ်တပ်ပြီး မြန်မာလို အနှစ်ချုပ်ပေးပါ။
         * Recap Script: ထိုအချက်တွေကို အခြေခံပြီး Social Media မှာ ပြန်သုံးလို့ရမယ့် ဇာတ်ညွှန်း (Script) တစ်ခုကို မြန်မာလို (စကားပြောဟန်) ရေးပေးပါ။
         * Language: Output အားလုံးကို လူနားလည်လွယ်တဲ့ မြန်မာစကားပြေနဲ့ပဲ ထုတ်ပေးပါ။
        """
        
        response = model.generate_content([video_file, prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def text_to_speech(text):
    """စာသားကို မြန်မာအသံဖိုင်အဖြစ် ပြောင်းလဲသည်။"""
    try:
        # Markdown sign တွေကို ဖယ်ရှားခြင်း
        clean_text = text.replace("#", "").replace("*", "").replace("-", "")
        tts = gTTS(text=clean_text, lang='my')
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        return fp.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# UI logic
uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင်ကို ရွေးချယ်ပါ (MP4, MOV, AVI)", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("Recap လုပ်မယ် ✨"):
        if not api_key:
            st.warning("ကျေးဇူးပြု၍ API Key အရင်ထည့်ပါ။")
        else:
            # ဗီဒီယိုကို ယာယီသိမ်းဆည်းခြင်း
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                tfile.write(uploaded_file.read())
                temp_path = tfile.name
            
            with st.spinner('AI က ဗီဒီယိုကို လေ့လာနေပါသည်...'):
                result_text = process_video(temp_path, api_key)
                
                st.success("ခွဲခြမ်းစိတ်ဖြာမှု ပြီးစီးပါပြီ။")
                st.markdown("### 📝 အနှစ်ချုပ် ရလဒ်")
                st.write(result_text)
                
                # အသံပြောင်းခြင်း
                st.markdown("### 🔊 အသံဖြင့် နားထောင်ရန်")
                audio_path = text_to_speech(result_text)
                if audio_path:
                    st.audio(audio_path, format="audio/mp3")
                    
            # ယာယီဖိုင်ကို ဖျက်ပစ်ခြင်း
            os.unlink(temp_path)

st.markdown("---")
st.caption("Powered by Gemini 3.1 Flash & Streamlit")