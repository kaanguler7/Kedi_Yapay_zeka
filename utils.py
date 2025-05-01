import emoji

def temizle_emoji(metin: str) -> str:
    return emoji.replace_emoji(metin, replace='')

def karakter_bilgisi(kedi: str) -> str:
    if kedi == "beyaz":
        return "Karakter: Beyaz Kedi - iyimser, kültürlü, nazik"
    else:
        return "Karakter: Siyah Kedi - alaycı, zeki, sivri dilli"