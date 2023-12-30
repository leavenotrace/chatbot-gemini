import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 0.95,
  "top_k": 1,
  "max_output_tokens": 99998,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

chat = model.start_chat(history=[])
def get_gemini_response(question):
    response=chat.send_message(question,stream=True)
    return response

##initialize our streamlit app

st.set_page_config(page_title="Gemini Chatbot",page_icon=":gem:")
st.header("Gemini LLM Chatbot🎈")
st.write("This is a Gemini LLM Chatbot. This app is powered by Google's GEMINI Generative AI models. This app is built using Streamlit and hosted on Streamlit Share.")


# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input=st.text_input("Input: ",key="input")
submit=st.button("Ask the question")

if submit and input:
 with st.spinner('Processing your question...'):
        st.session_state['chat_history'].append(("You", input))
        response=get_gemini_response(input)
        # Combine all chunks of the response into one message
        bot_response = ' '.join(chunk.text for chunk in response)
        st.session_state['chat_history'].append(("Bot", bot_response))
        st.subheader("The Response is")
        st.write(bot_response)
        
with st.sidebar:
    st.header("Chat History")
    for role, text in st.session_state['chat_history']:
        if role == "You":
            st.markdown(f"**{role}:** {text}", unsafe_allow_html=True)
        else:
            st.markdown(f"{role}: {text}", unsafe_allow_html=True)
        
st.markdown("---")
st.markdown("""
    App built by [srikresna](https://github.com/srikresna) using [Streamlit](https://streamlit.io) and hosted on [Streamlit Share](https://share.streamlit.io).
""")