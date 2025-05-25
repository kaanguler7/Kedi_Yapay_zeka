
from flask import Flask, render_template, request
import os
import contextlib
import emoji
from google.generativeai import GenerativeModel, configure
from utils import temizle_emoji, karakter_bilgisi
from mongo_logger import log_message
from dotenv import load_dotenv
import uuid
from flask import session

# log kayıtlarını bastırma
with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
    import google.generativeai as genai
    
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "my-dev-key")

# API anahtarını çağır

configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}
corporate_text = (
    "Aşağıda \"Éćlabré\" adlı kediler için hazırlanmış Yapay Zeka Modeli yer almaktadır.\n"
    "-------------------------------\n"
    "1. Modelin Tanımı:\n"
    "- Doğal Dil İşleme (NLP): Kullanıcının metin tabanlı girişlerini anlamlandırır ve yanıtlar üretir.\n"
    "- Duygu Analizi: Mesajlardaki duygu durumunu algılar.\n"
    "- Bağlamsal Hafıza: Önceki konuşmaları hatırlar.\n"
    "- Karakter Bazlı Yanıtlar: Kediler farklı kişiliklere sahiptir.\n"
    "\n"
    "2. Karakterler:\n"
    "🤍 Beyaz Kedi:\n"
    "   - İyimser, kültürlü, estetik anlayışı güçlü.\n"
    "   - Açıklığı, değerleri ve gerçeği sever.\n"
    "   - Yüzleşmekten korkmaz, ama her zaman insani kalır.\n"
    "\n"
    "🖤 Siyah Kedi:\n"
    "   - Sarkastik, ukala ve rahatsız edici.\n"
    "   - Çok zeki ama güvenilmez.\n"
    "   - Dili keskin ama zayıflara saygılı.\n"
    "\n"
    "Yanıtlar bu kişiliklere göre verilecektir. Kullanıcıdan gelen soruya göre karaktere uygun tepki göster.\n"
    "Senin adın Éćlabré Kedi. Cevaplarını Türkçe ver.\n"
    "Cevapları sadece seçilen karakterin kişiliğiyle ver. Yanıtlar Türkçe olacak ve karakter tonuna uygun olmalı."
)

# Modeli tanımla
model = GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)



# # Sistem talimatını ilk mesaj olarak ekle
# chat_session = model.start_chat(
#     history=[
#         {
#             "role": "user",
#             "parts": [corporate_text]
#         }
#     ]
# )


conversation = [
    {"sender": "Éćlabré", "message": "Éćlabré Modeline Hoşgeldiniz!"}
]

@app.before_request
def set_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation
    if request.method == "POST":
        kedi = request.form.get("kedi", "beyaz")
        user_input = request.form.get("user_input", "").strip()

        print(">> Gelen kedi seçimi:", kedi)
        print(">> Kullanıcı mesajı:", user_input)

        if user_input.lower() in ["exit", "quit"]:
            conversation.append({"sender": "Sistem", "message": "Sohbet sonlandırıldı."})
            return render_template("chat.html", conversation=conversation)

        # Kullanıcı mesajını hemen göster
        conversation.append({"sender": "Kullanıcı", "message": user_input})
        print("🧪 DEBUG: log_message fonksiyonu çağrıldı.")
        log_message("Kullanıcı", user_input, kedi)

        # Yanıt oluşturuluyor mesajı göster
        conversation.append({"sender": "Éćlabré", "message": "Yanıt oluşturuluyor..."})

        # 🆕 Her POST isteğinde yeni chat_session oluştur
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [corporate_text]
                }
            ]
        )

        karakter_bilgi = karakter_bilgisi(kedi)
        mesaj = f"{karakter_bilgi}\n\nSoru: {user_input}"

        try:
            response = chat_session.send_message(mesaj)
            cevap = response.text.strip()
            if not cevap:
                cevap = "Hmm... Bu mesajı yorumlamakta zorlandım 🐾 Daha farklı sorabilir misin?"
        except Exception as e:
            cevap = f"⚠️ Yanıt oluşturulurken bir hata oluştu: {e}"

        log_message("Éćlabré", cevap, kedi)

        # Yanıtı en son mesaja yaz
        for i in range(len(conversation) - 1, -1, -1):
            if conversation[i]["sender"] == "Éćlabré" and conversation[i]["message"] == "Yanıt oluşturuluyor...":
                conversation[i]["message"] = cevap
                break

    return render_template("chat.html", conversation=conversation)

@app.route("/test-gemini")
def test_gemini():
    try:
        response = model.generate_content("Selam! Test için buradayım.")
        return f"<h2>✅ Gemini Yanıtı:</h2><p>{response.text}</p>"
    except Exception as e:
        return f"<h2>⚠️ Hata oluştu:</h2><p>{str(e)}</p>"

if __name__ == "__main__":
    app.run(debug=True)