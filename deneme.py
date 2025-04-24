# API_Gemini = AIzaSyDpPZ-c_KjJXuCB7bKeUbLUCtIaPGQJzjM
from flask import Flask, render_template, request
import os
import contextlib
import emoji
from google.generativeai import GenerativeModel, configure

# log kayıtlarını bastırma
with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
    import google.generativeai as genai

app = Flask(__name__)

# API anahtarını çağır
configure(api_key="AIzaSyDpPZ-c_KjJXuCB7bKeUbLUCtIaPGQJzjM")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 512, #daha hızlı yantı veriri max 512 kelime yazar 
}

# Modeli tanımla
model = GenerativeModel(
    model_name="gemini-2.5-pro-exp-03-25",
    generation_config=generation_config
)

corporate_text = (
    "Aşağıda 'Éćlabré' adlı kediler için hazırlanmış Yapay Zeka Modeli yer almaktadır.\n"
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
    "Senin adın Éćlabré Kedi. Cevaplarını Türkçe ver."
)

chat_session = model.start_chat(history=[])

conversation = [
    {"sender": "Éćlabré", "message": "Éćlabré Modeline Hoşgeldiniz!"}
]

def temizle_emoji(metin):
    return emoji.replace_emoji(metin, replace='')

@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation
    kedi = request.form.get("kedi", "beyaz")

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input.lower() in ["exit", "quit"]:
            conversation.append({"sender": "Sistem", "message": "Sohbet sonlandırıldı."})
            return render_template("chat.html", conversation=conversation)

        conversation.append({"sender": "Kullanıcı", "message": user_input})

        if kedi == "beyaz":
            karakter_bilgi = "Karakter: Beyaz Kedi - iyimser, kültürlü, nazik"
        else:
            karakter_bilgi = "Karakter: Siyah Kedi - alaycı, zeki, sivri dilli"

        # "Yanıt oluşturuluyor..." mesajı
        conversation.append({"sender": "Sistem", "message": "Yanıt oluşturuluyor..."})

        combined_input = f"{corporate_text}\n\n{karakter_bilgi}\n\nSoru: {user_input}"
        response = chat_session.send_message(combined_input)
        cevap = response.text

        # Geçici sistemi mesajı silip gerçek cevabı göster
        conversation.pop()  # Yanıt oluşturuluyor...
        conversation.append({"sender": "Éćlabré", "message": cevap})

    return render_template("chat.html", conversation=conversation)

if __name__ == "__main__":
    app.run(debug=True)