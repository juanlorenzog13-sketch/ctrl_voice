import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client,userdata,result):             #create function for callback
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("JLOctrl")
client1.on_message = on_message

st.set_page_config(
    page_title="Detecta tu voz aqui",
    page_icon="🎀",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #ffe4f2 0%, #ffd6eb 45%, #fff0f8 100%);
}

h1, h2, h3 {
    color: #d63384 !important;
    text-align: center;
}

p, label, .stMarkdown, div {
    color: #9c4674;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.pink-card {
    background: rgba(255, 255, 255, 0.78);
    border: 2px solid #f7b6d2;
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(214, 51, 132, 0.12);
    margin-bottom: 18px;
    backdrop-filter: blur(10px);
}

.pink-note {
    text-align: center;
    color: #b54d84;
    font-size: 1rem;
}

[data-testid="stImage"] img {
    border-radius: 22px;
    border: 3px solid #f7b6d2;
    box-shadow: 0 12px 24px rgba(214, 51, 132, 0.14);
}

.stAlert {
    background: rgba(255,255,255,0.82) !important;
    border: 2px solid #f6b2d0 !important;
    color: #9c4674 !important;
    border-radius: 18px !important;
}

iframe {
    filter: hue-rotate(-18deg) saturate(1.15) brightness(1.03);
}
</style>
""", unsafe_allow_html=True)

st.title("Detecta tu voz aqui")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')

st.markdown('<div class="pink-card">', unsafe_allow_html=True)
st.image(image, width=220)
st.markdown(
    '<p class="pink-note">Toca el botón y habla ✨</p>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

stt_button = Button(label=" Inicio ", width=200, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.markdown('<div class="pink-card">', unsafe_allow_html=True)
        st.write(result.get("GET_TEXT"))
        st.markdown('</div>', unsafe_allow_html=True)

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_JLOctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
