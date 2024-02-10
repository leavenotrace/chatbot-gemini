from PIL import Image
import io
import logging
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

temperature = 0.9

generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 99998,
}

st.set_page_config(page_title="Gemini Chatbot", page_icon=":gem:")

with st.sidebar:
    st.title("Gemini Setting")

    #api_key = st.text_input("API key", placeholder="if you have one.")
    api_key = "AIzaSyCfa62eNW62tqXPet6pFc3-6eg5qMPaLRI"
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        else:
            st.error("Missing API key.")
    select_model = st.selectbox(
        "Select model", ["gemini-pro", "gemini-pro-vision"])
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.9, 0.1)
    st.caption(
        "Temperature controls the randomness of the model. Lower temperature results in less randomness.")

    if select_model == "gemini-pro-vision":
        uploaded_image = st.file_uploader(
            "upload image",
            label_visibility="collapsed",
            accept_multiple_files=False,
            type=["png", "jpg"],
        )
        st.caption(
            "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
        )
        if uploaded_image:
            image_bytes = uploaded_image.read()


def get_response(messages, model="gemini-pro"):
    model = genai.GenerativeModel(model)
    res = model.generate_content(messages,
                                 generation_config=generation_config)
    return res


if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages = st.session_state["messages"]

# The vision model gemini-pro-vision is not optimized for multi-turn chat.
st.header("Happy Gemini  ")
# st.write("This is a Gemini LLM Chatbot. This app is powered by Google's GEMINI Generative AI models. This app is built using Streamlit and hosted on Streamlit Share.")
# st.markdown(
#    App built by [srikresna](https://github.com/srikresna) using [Streamlit](https://streamlit.io) and hosted on [Streamlit Share](https://share.streamlit.io).
#""") """

# Initialize session state for chat history if it doesn't exist
if messages and select_model != "gemini-pro-vision":
    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "model":
            st.chat_message("assistant").markdown(parts[0])

chat_message = st.chat_input("Say something")

res = None
if chat_message:
    st.chat_message("user").markdown(chat_message)
    res_area = st.chat_message("assistant").markdown("...")

    if select_model == "gemini-pro-vision":
        if "image_bytes" in globals():
            vision_message = [chat_message,
                              Image.open(io.BytesIO(image_bytes))]
            try:
                res = get_response(vision_message, model="gemini-pro-vision")
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
        else:
            vision_message = [{"role": "user", "parts": [chat_message]}]
            st.warning(
                "Since there is no uploaded image, the result is generated by the default gemini-pro model.")
            try:
                res = get_response(vision_message)
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
    else:
        messages.append(
            {"role": "user", "parts":  [chat_message]},
        )
        try:
            res = get_response(messages)
        except google_exceptions.InvalidArgument as e:
            if "API key not valid" in str(e):
                st.error("API key not valid. Please pass a valid API key.")
            else:
                st.error("An error occurred. Please refresh your page and try again.")
        except Exception as e:
            logging.error(e)
            st.error("Error occured. Please refresh your page and try again.")
    
    if res is not None:
        res_text = ""
        for chunk in res:
            if chunk.candidates:
                res_text += chunk.text
            if res_text == "":
                res_text = "unappropriate words"
                st.error("Your words violate the rules that have been set. Please try again!")
        res_area.markdown(res_text)

        if select_model != "gemini-pro-vision":
            messages.append({"role": "model", "parts": [res_text]})
