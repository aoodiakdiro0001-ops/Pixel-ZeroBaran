# 📦 Pixel-ZeroBaran — دليل التثبيت السريع

> أصغر دليل ممكن لتشغيل المشروع في 5 دقائق.

---

## ① تثبيت التبعيات

```bash
# استنساخ
git clone https://github.com/<username>/Pixel-ZeroBaran.git
cd Pixel-ZeroBaran

# بيئة افتراضية
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# تثبيت
pip install -r requirements.txt

# تنزيل نموذج rembg (مرة واحدة، ~176MB)
python -c "from rembg import new_session; new_session('u2net')"
```

## ② الحصول على المفاتيح المجانية

| الخدمة | الخطوات |
|---|---|
| **HuggingFace** | https://huggingface.co/join → Settings → Access Tokens → New token (Read) |
| **Gemini** | https://aistudio.google.com/app/apikey → Create API key |
| **Supabase** | https://supabase.com/dashboard → New project → Settings → API → Copy URL & anon key |
| **Telegram** | تحدث مع [@BotFather](https://t.me/BotFather) → /newbot → انسخ التوكن |

## ③ ضبط الإعدادات

```bash
cp .env.example .env
nano .env   # عبّئ القيم
```

## ④ إعداد قاعدة البيانات

1. ادخل Dashboard Supabase → SQL Editor.
2. الصق محتوى `docs/supabase_schema.sql`.
3. اضغط Run.

## ⑤ فحص وتشغيل

```bash
python main.py check     # فحص
python main.py info      # معلومات المؤلف
python main.py bot       # تشغيل البوت
# أو
python main.py dashboard # تشغيل اللوحة على http://localhost:8501
```

## ⑥ أول صورة!

أرسل لبوتك صورة منتج مع caption:
```
ساعة فاخرة فولاذية #luxury_dark
```

انتظر 30-60 ثانية — سيعود إليك الإعلان جاهزاً! 🎉

---

**© Baran Avisat — Pixel-ZeroBaran v1.0.0**
