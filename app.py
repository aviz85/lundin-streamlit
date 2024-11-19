import streamlit as st
import anthropic
import json
from prompt_template import SYSTEM_PROMPT, PROMPT_TEMPLATE
from examples import INTERPRETATION_EXAMPLES
from services.text_generator import create_interpretation_txt
import io

def get_interpretation(text):
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    model_name = st.secrets["MODEL_NAME"]
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user", 
            "content": PROMPT_TEMPLATE.format(
                text_to_analyze=text
            )
        }]
    )
    
    # Extract JSON from response
    try:
        response_text = message.content[0].text
        json_start = response_text.find('```json\n') + 8
        json_end = response_text.find('```', json_start)
        json_str = response_text[json_start:json_end].strip()
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        return None

def main():
    # Set basic page config
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed",
        page_title="מנדי - עוזר אישי לכתיבת פירוש תורני",
        page_icon="📚"
    )
    
    # Minimal CSS just for RTL support
    st.markdown("""
        <style>
            .stApp { direction: rtl; }
            .stTextArea textarea { direction: rtl; }
        </style>
    """, unsafe_allow_html=True)

    st.title("מנדי - עוזר אישי לכתיבת פירוש תורני")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_text = st.text_area("הכנס טקסט לפירוש:", height=200)
        if st.button("פרש את הטקסט"):
            if not user_text:
                st.error("אנא הכנס טקסט לפירוש")
                return
                
            with st.spinner("מנתח את הטקסט..."):
                interpretation = get_interpretation(user_text)
                
                if interpretation:
                    with col2:
                        st.subheader("טקסט מקורי")
                        st.write(interpretation["original_text"])
                        
                        st.subheader("אות")
                        st.write(interpretation["letter"])
                        
                        st.subheader("מילים קשות")
                        for word in interpretation["difficult_words"]:
                            st.write(f"**{word['word']}**: {word['explanation']}")
                        
                        st.subheader("פירוש מפורט")
                        for detail in interpretation["detailed_interpretation"]:
                            st.write(f"**ציטוט**: {detail['quote']}")
                            st.write(f"**פירוש**: {detail['explanation']}")
                            st.markdown("---")
                        
                        # Add download button for txt
                        text_content = create_interpretation_txt(interpretation)
                        
                        st.download_button(
                            label="הורד כקובץ טקסט",
                            data=text_content.encode('utf-8'),
                            file_name="interpretation.txt",
                            mime="text/plain"
                        )

if __name__ == "__main__":
    main() 