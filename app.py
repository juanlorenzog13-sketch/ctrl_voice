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
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("GIT-HUBC")
client1.on_message = on_message

st.set_page_config(
    page_title="CONTROL POR VOZ",
    page_icon="🔴",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top, rgba(120,0,0,0.35) 0%, rgba(40,0,0,0.15) 25%, rgba(0,0,0,1) 70%),
        linear-gradient(180deg, #120000 0%, #000000 100%);
    color: #f5d6d6;
}

h1, h2, h3 {
    color: #ff2b2b !important;
    text-align: center;
    text-shadow: 0 0 8px rgba(255, 0, 0, 0.6), 0 0 18px rgba(255, 0, 0, 0.3);
    letter-spacing: 1px;
}

p, label, .stMarkdown, div {
    color: #f2caca;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.scary-card {
    background: rgba(20, 0, 0, 0.82);
    border: 1px solid rgba(255, 0, 0, 0.35);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 0 30px rgba(255, 0, 0, 0.14);
    backdrop-filter: blur(6px);
    margin-bottom: 18px;
}

.scary-note {
    text-align: center;
    color: #ffb3b3;
    font-size: 1.02rem;
}

[data-testid="stImage"] img {
    border-radius: 18px;
    border: 2px solid rgba(255, 0, 0, 0.45);
    box-shadow: 0 0 25px rgba(255, 0, 0, 0.18);
}

hr {
    border-top: 1px solid rgba(255, 0, 0, 0.25) !important;
}

.stAlert {
    background: rgba(30, 0, 0, 0.88) !important;
    border: 1px solid rgba(255, 0, 0, 0.35) !important;
    color: #ffd1d1 !important;
}

iframe {
    filter: hue-rotate(-15deg) saturate(1.3) contrast(1.05);
}
</style>
""", unsafe_allow_html=True)

st.title("INTERFACES MULTIMODALES")
st.subheader("CONTROL POR VOZ")

image = Image.open('voice_ctrl.jpg')

st.markdown('<div class="scary-card">', unsafe_allow_html=True)
st.image(image, width=260)
st.markdown(
    '<p class="scary-note">Toca el botón y habla.</p>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

stt_button = Button(label=" INICIO ", width=220, button_type="danger")

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
        st.markdown('<div class="scary-card">', unsafe_allow_html=True)
        st.write(result.get("GET_TEXT"))
        st.markdown('</div>', unsafe_allow_html=True)

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
