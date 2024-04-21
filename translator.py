import streamlit as st
from PIL import Image
import os
import cv2
import base64
import easyocr
import numpy as np
#from googletrans import Translator
from gtts import gTTS
from language_tool_python import LanguageTool
import speech_recognition as sr

# pip install infobip-api-python-sdk
# from playsound import playsound

# Configuration de la page
st.set_page_config(
    page_title="Documents translator App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get help': "mailto:pauladeola@outlook.fr",
        'About': "FIRE AND ACCIDENT DECTECTION SYSTEM BY COMPUTER VISION. \
                 This is an *extremely* cool app! \
                 This app built with YOLOv8 and Streamlit is a fire and accident detection app. \
                 It can detect the fire or accident on  image or in real-time (using camera). \
                 His goal is to detect quickly fire or accident and alert to avoid damages \
                 \nAuthor: Moesse DJEKINNOU / School: DIT \
                 \nContact: +225-05-65-69-40-82 / \nMail: pauladeola@outlook.fr",
        'Report a bug': "mailto:pauladeola@outlook.fr"
    }
)

st.image('https://raw.githubusercontent.com/summermp/pisa22/main/static/img/banner/merry_christmas.gif', width=1350)

# Style pour le titre de la page
st.markdown(
    """
    <style>
    /* Style pour le cadre */
    .custom-frame {
        color: #4285F4;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 15px;
            padding: 20px;
            margin: 10px;
            border: 2px solid #ccc;
            border-radius: 5px;
            background-color: #f9f996;
    }
    </style>
    """
    , unsafe_allow_html=True)
# Affichage du titre de la page
st.markdown('<div class="custom-frame">SCANNED DOCUMENTS TRANSLATOR</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Image Translator", "Audio Translator", "Text Translator"]) #définit les pages

# Définition des fonctions
#Charge limage pour permettre sa reconnaissance par easy ocr
@st.cache_data
def load_img(uploaded_file):
    # Convertir l'image téléchargée en tableau NumPy
    image = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return img
#Recupere le texte de l'image
@st.cache_data
def read_img(image, lang):
    # Créer un objet EasyOCR
    ocr = easyocr.Reader([lang])
    # Appliquer OCR à l'image
    reading = ocr.readtext(image)
    texte_recupere = ' '.join([result[1] for result in reading])
    return texte_recupere

#Traduire le texte
@st.cache_resource
def translate(input:str, src, dest):
    from textblob import TextBlob
    # Vérifier si la langue source est différente de la langue cible
    if src != dest:
        # Créer une instance de TextBlob avec le texte d'origine
        blob = TextBlob(input)
        # Traduire le texte
        try:
            output = blob.translate(from_lang=src, to=dest)
        except Exception as e:
            if e==' Translation API returned the input string unchanged.':
                st.error("Erreur lors de la traduction : Le text saisi est deja dans la langue de sortie")
                output=" "
            else :
                st.error(f"Erreur lors de la traduction : {e}")
                output = " "
    else:
        output = input
    return str(output)

    #trans=Translator()
    #output = trans.translate(input, src=src, dest=dest).text
    #return output


@st.cache_data
def read_audio(text_to_read, lang):
    import io
    # Create a gTTS object
    tts = gTTS(text=text_to_read, lang=lang)

    # Use io to get the audio content as bytes
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    #audio_data.seek(0)
    #display(Audio(audio_data.read(), autoplay=True))
    return audio_data

import speech_recognition as sr
from pydub import AudioSegment

def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")

def transcribes(wav_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text
def listen_audio(lang):
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        voix=r.listen(source, timeout=6)
        if lang=='fr':
            lang='fr-FR'
        elif lang=='en':
            lang='en-US'
        else :
            lang='es-ES'
        try:
            result=r.recognize_google(voix,language=lang)
        except Exception as ex:
            result = ex
    return (result)     

# Nom du fichier MP3 d'entrée
mp3_file = "galates.mp3"

# Nom du fichier WAV de sortie
wav_file = "galates.wav"



def transcribe(url) :
    # Créer un objet Recognizer
    recognizer = sr.Recognizer()

    # Chemin vers le fichier audio
    chemin_fichier_audio = url

    # Charger le fichier audio
    with sr.AudioFile(chemin_fichier_audio) as source:
        # Utiliser record() pour capturer l'audio à partir du fichier
        audio = recognizer.record(source)

        try:
            # Utiliser la reconnaissance vocale pour transcrire l'audio en texte
            texte_transcrit = recognizer.recognize_google(audio, language="fr-FR")
            return texte_transcrit
        except sr.UnknownValueError:
            print("Google Speech Recognition n'a pas pu comprendre l'audio")
        except sr.RequestError as e:
            print("Erreur lors de la requête à l'API Google Speech Recognition ; {0}".format(e))


# show image: pour afficher des images statics (lire les images et ensuite les passer dans un markdown)
@st.cache_data
def show_image(path: str):
    file_ = open(path, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    return data_url
@st.cache_resource
def select_languages():
    st.markdown('''<div> <h6 style= 'font-size:20px'>Select Languagues : </h6></div>''', unsafe_allow_html=True)
    input_lang = st.selectbox("From", ("French", "English", "Spanish"), index=0, key='image')
    output_lang = st.selectbox("To", ("French", "English", "Spanish"), index=1, key='image2')

#correction du texte (optionnel)
#def correct(_texte, lang):
#    if lang=='en':
#        lang='en-US'
#    tool = LanguageTool(lang)  # Spécifiez la langue française
#    corrections = tool.correct(_texte)
#    #blob = TextBlob(_texte)
#    #corrections = blob.correct()
#    return str(corrections)

def show_translate(translation, text_translate):
    translation.markdown(f'''
                    <div style='padding:5px 5px 5px 5px; margin-bottom:15px; border-radius:8px; background-color: #4285F4; color:white;'>
                    <h6 style= 'color: white;font-size:19px;
                    user-select: none;
                    -moz-user-select: none;
                    -webkit-user-select: none;
                    -ms-user-select: none'>{text_translate}</h6> 
                    </div>''', unsafe_allow_html=True) # empeche la cope du texte
# img=show_image("cam.jpeg")
# st.markdown(f'<img src="data:image;base64,{white_img}" style="width: auto; height: 400px;" alt="cat gif">',unsafe_allow_html=True)

# mise en place du code
languages = {'French': 'fr', 'English': 'en', 'Spanish': 'es'}
if 'transcription' not in st.session_state:
    st.session_state.transcription=""
btn=True #Etat des boutons download et audio

with tab1:
    # Division de la page en colonnes
    col1, col2, col3 = st.columns([1, 3, 3])
    with col1:
        st.markdown('''<div> <h6 style= 'font-size:20px'>Select Languagues : </h6></div>''', unsafe_allow_html=True)
        input_lang = st.selectbox("From", ("French", "English", "Spanish"), index=0, key='image')
        output_lang = st.selectbox("To", ("French", "English", "Spanish"), index=1, key='image2')

    with col2:
        # st.markdown('<div class="custom-frame"> FIRE DETECTION </div>', unsafe_allow_html=True)
        #load_container = st.empty()
        msg_container = st.container(border=True)
        image = st.file_uploader('image', type=('jpg', 'png', 'bmp'), label_visibility='collapsed')
        in_img_container = st.container(border=True)
        in_img = in_img_container.markdown('''
                                <div style='padding:5px 5px 410px 5px; border-radius:5px; background-color: #f9f996;  margin-bottom: 20px;'>          
                                </div>''', unsafe_allow_html=True)
        if image is not None:

            msg_container.write("##### Image loaded!! Select languages and press Translate...")

            image_to_extract = load_img(image)
            img_show = Image.open(image)
            new_image = img_show.resize((900, 700))
            in_img.image(new_image)
            text_from_img=read_img(image_to_extract, languages[input_lang])  #recupere le texte de l'image

            btn_translate = st.button("Translate", type="primary") #affiche le bouton translate

            # Affichez le texte dans une zone de texte
            text_to_translate=st.text_area(label="Text readed from your image: you can correct errors before translate.", value=text_from_img, height=400, key="textarea_id")
        else:
            msg_container.write("##### Waiting for Image...")

    with col3:
        msg_container2 = st.container(border=True)
        msg_container2.write(f"##### Translation from {input_lang} to {output_lang}")
        translation = st.markdown(f'''
                    <div style='padding:5px 5px 400px 5px; margin-bottom:15px; border-radius:8px; background-color: #4285F4; color:white;'>
                    </div>''', unsafe_allow_html=True)
        btn1, btn2, btn3 = st.columns([3, 3, 2])
        if image is not None:
            text_translate = translate(text_to_translate, languages[input_lang], languages[output_lang])
            if btn_translate:
                show_translate(translation, text_translate)
                btn=False
            btn_download = btn1.download_button('Download', text_translate, file_name='Translation.txt', disabled=btn, key='image_download')
            if btn_download:
                show_translate(translation, text_translate)
                btn = False
            #btn_convert = btn1.button("Convert to img")
            btn_audio = btn3.button("Play audio   ", disabled=btn)
            if btn_audio:
                show_translate(translation, text_translate)
                audio_bytes=read_audio(text_translate, languages[output_lang])
                st.audio(audio_bytes)

with tab2:
    col1, col2, col3 = st.columns([1, 3, 3])
    with col1:
        st.markdown('''<div> <h6 style= 'font-size:20px'>Select Languagues : </h6></div>''', unsafe_allow_html=True)
        input_lang = st.selectbox("From", ("French", "English", "Spanish"), index=0, key='audio')
        output_lang = st.selectbox("To", ("French", "English", "Spanish"), index=1, key='audio2')
    with col2:
        st.markdown('''<div> <h6 style= 'color: blue; font-size:20px'>Press speak button... </h6></div>''', unsafe_allow_html=True)
        #audio_file = open('Alarme_sound.wav', 'rb')
        #audio_bytes = audio_file.read()
        #st.audio(audio_bytes, format='audio/ogg')
        #file=st.audio()
        #uploaded_file = st.file_uploader("Choose a file")
        #text_to_translate.write()
        speak_button=st.button("Speak")

        if speak_button:
            st.session_state.transcription=listen_audio(languages[input_lang])
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print("ok")
        text_to_translate = st.text_area(label="You said: ", value=st.session_state.transcription, height=400, key="textarea_id2")
        btn_translate = st.button("Translate", type="primary")  # affiche le bouton translate
        with col3:
            msg_container2 = st.container(border=True)
            msg_container2.write(f"##### Translation from {input_lang} to {output_lang}")
            translation = st.markdown(f'''
                        <div style='padding:5px 5px 400px 5px; margin-bottom:15px; border-radius:8px; background-color: #4285F4; color:white;'>
                        </div>''', unsafe_allow_html=True)
            btn1, btn2, btn3 = st.columns([3, 3, 2])
            text_translate = translate(text_to_translate, languages[input_lang], languages[output_lang])
            if btn_translate:

                show_translate(translation, text_translate)
                btn = False
            btn_download = btn1.download_button('Download', text_translate, file_name='Translation.txt',
                                                disabled=btn, key='image_download')
            if btn_download:
                show_translate(translation, text_translate)
                btn = False
            btn_audio = btn3.button("Play audio   ", disabled=btn)
            if btn_audio:
                show_translate(translation, text_translate)
                audio_bytes = read_audio(text_translate, languages[output_lang])
                st.audio(audio_bytes)
        # Conversion du fichier MP3 en WAV
        #convert_mp3_to_wav('galates.mp3', 'galate.wav')

        # Transcription du fichier WAV
        #resultat_transcription = transcribe('galate.wav')



with tab3:
    col1, col2, col3 = st.columns([1, 3, 3])
    with col1:
        st.markdown('''<div> <h6 style= 'font-size:20px'>Select Languagues : </h6></div>''', unsafe_allow_html=True)
        input_lang = st.selectbox("From", ("French", "English", "Spanish"), index=0, key="text")
        output_lang = st.selectbox("To", ("French", "English", "Spanish"), index=1, key="text2")

    with col2:
        msg_container = st.container(border=True)
        text_entry = st.text_area('Entry your text', placeholder='Type text...')
        btn_translate = st.button("Translate", type="primary", key="text_translate")
        if len(text_entry) >0:
            msg_container.write("##### Type a text, Select languages and press Translate...")
            st.write(text_entry ,':', len(text_entry))
            #texte_to_translate = correct(text_entry, languages[input_lang])
        else:
            msg_container.write("##### Waiting for text...")
    with col3:
        msg_container2 = st.container(border=True)
        msg_container2.write(f"##### Translation from {input_lang} to {output_lang}")
        #Affiche l'espace de la traduction
        translation = st.markdown(f'''
                    <div style='padding:5px 5px 400px 5px; margin-bottom:15px; border-radius:8px; background-color: #4285F4; color:white;'>
                    </div>''', unsafe_allow_html=True)
        btn1, btn2, btn3 = st.columns([3, 3, 2])
        if len(text_entry) >0 :
            text_translate = translate(text_entry, languages[input_lang], languages[output_lang])
            if btn_translate:
                btn = False
                show_translate(translation, text_translate)

            btn_download = btn1.download_button('Download', text_translate, file_name='Translation.txt', disabled=btn)
            if btn_download:
                show_translate(translation, text_translate)
                btn = False
            #btn_convert = btn1.button("Convert to img")
            btn_audio = btn3.button("Play audio   ", disabled=btn, key='audio_btn_text')
            if btn_audio:
                show_translate(translation, text_translate)
                btn = False
                audio_bytes=read_audio(text_translate, languages[output_lang])
                st.audio(audio_bytes)

# Pied de page
st.markdown('<div class="footer">© 2024 Translator / Moesse Djekinnou</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
# Affichage d'un cadre avec du contenu à l'intérieur
# st.markdown('<div class="custom-frame"></div>', unsafe_allow_html=True)
