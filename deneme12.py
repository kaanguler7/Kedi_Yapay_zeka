# API_Gemini = AIzaSyDpPZ-c_KjJXuCB7bKeUbLUCtIaPGQJzjM
from flask import Flask, render_template, request
import os
import contextlib
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
from playsound import playsound
import tempfile
import pygame
import time
import emoji

# log kayıtlarını bastırma
with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
    import google.generativeai as genai

app = Flask(__name__)

# API anahtarını çağır
genai.configure(api_key="AIzaSyDpPZ-c_KjJXuCB7bKeUbLUCtIaPGQJzjM")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    # "response_mime_type": "text/plain",  ← HATALI ALANDI, KALDIRILDI
}

# Modeli tanımla
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro-exp-03-25",
    generation_config=generation_config
)

corporate_text = (
    "Aşağıda \"Hakan Konuk'un \" kedileri için hazırlanmış Yapay Zeka Modeli yer almaktadır. "
    "Bu metin belgesi modelin nasıl çalıştığını ve neler kullandığı gibi temel bilgiler içerir.\n\n"
    "-------------------------------\n"
    "Hakan Konuk'un Éćlabré Yapay Zeka Modelenin Temelleri.\n\n "
    "1. Modelin Tanımı\n"
    "   -Doğal Dil İşleme (NLP): Kullanıcının metin tabanlı girişlerini anlamlandırır ve yanıtlar üretir.\n"
    "   -Konuşma Tanıma (STT): Mikrofon üzerinden sesli komutları algılar ve yazıya çevirir.\n"
    "   -Metinden Konuşmaya (TTS): Kedilerin gerçekçi bir şekilde konuşmasını sağlar.\n"
    "   -Duygu Analizi: Kullanıcının mesajındaki duyguyu tespit ederek yanıtların tonunu belirler.\n"
    "   -Bağlamsal Hafıza: Önceki konuşmaları hatırlayarak daha akıllı ve doğal yanıtlar oluşturur.\n"
    "   -Karakter Bazlı Yanıtlar: Kediler farklı kişiliklere sahip olup, her biri belirli duygu durumlarına özel yanıtlar üretir."
    "Cevap verirken bana bir müşteri veya kullanıcı gibi davran ve direk sorduğum soruya tam cevap ya da metinde benzer bir yer görürsen ordaki veriyi aktar ve cevap verirken emoji kullan ki samimi gözüksün"
    "Senin adın artık Éćlabré Kedi her şeye buna göre cevap vereceksin"
    "Yanıtlarını mutlaka Türkçe ver. İngilizce, Fransızca veya başka dil kullanma."
    "Hakan Konuk yerine onun kelimesini kullan."
)

# sohbet oturumunu oluştur
chat_session = model.start_chat(history=[])

# sohbeti başlat
conversation = [
    {"sender": "Éćlabré", "message": "Éćlabré Modeline Hoşgeldiniz!"}
]

# 🎤 Sesli girişi metne çeviren fonksiyon
def sesli_giris():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Konuşmaya başlayabilirsiniz...")
        r.adjust_for_ambient_noise(source, duration=1)  # Gürültü ayarı
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)  # daha sağlıklı sınırlar
        except sr.WaitTimeoutError:
            print("⏱️ Mikrofon sesi duymadı, zaman aşımı.")
            return ""
    try:
        metin = r.recognize_google(audio, language="tr-TR")
        print("✅ Anlaşılan: " + metin)
        return metin
    except sr.UnknownValueError:
        print("⚠️ Ne dediğin anlaşılmadı.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Google API hatası: {e}")
        return ""
    
def temizle_emoji(metin):
    return emoji.replace_emoji(metin, replace='')  # tüm emojileri sil

# 🔊 Metni sesli okuyan fonksiyon
def sesi_oku(metin):
    try:
        # Emojileri temizle
        temiz_metin = temizle_emoji(metin)
        # Geçici mp3 dosyası oluştur
        tts = gTTS(text=temiz_metin, lang='tr')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_file = fp.name
        tts.save(temp_file)

        # pygame ile çal
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()

        # Sesin çalınması bitene kadar bekle
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove(temp_file)
    except Exception as e:
        print(f"🔊 Sesli okuma hatası: {e}")

# Yazılı sohbet
@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input.lower() in ["exit", "quit"]:
            conversation.append({"sender": "Sistem", "message": "Sohbet sonlandırıldı"})
            return render_template("chat.html", conversation=conversation)

        conversation.append({"sender": "Kullanıcı", "message": user_input})
        combined_input = corporate_text + "\nSoru: " + user_input
        response = chat_session.send_message(combined_input)
        cevap = response.text
        conversation.append({"sender": "Éćlabré", "message": cevap})
        sesi_oku(cevap)

    return render_template("chat.html", conversation=conversation)

# Sesli komutla sohbet
@app.route("/voice", methods=["POST"])
def voice():
    global conversation
    user_input = sesli_giris()

    if user_input:
        conversation.append({"sender": "Kullanıcı", "message": user_input})
        combined_input = corporate_text + "\nSoru: " + user_input
        response = chat_session.send_message(combined_input)
        cevap = response.text
        conversation.append({"sender": "Éćlabré", "message": cevap})
        sesi_oku(cevap)

    return render_template("chat.html", conversation=conversation)

if __name__ == "__main__":
    app.run(debug=True)

#elevenlabs api : sk_5851aafbdd389ece4f095cc9252abc95f938f59976f813a6