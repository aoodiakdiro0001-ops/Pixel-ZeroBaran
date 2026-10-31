# 🚀 Pixel-ZeroBaran — دليل النشر الكامل

> كيف تنشر المشروع وتشغّله على بيئات مختلفة — كلها مجانية.

---

## 📋 المتطلبات المسبقة

أنشئ حسابات مجانية في الخدمات التالية (كلها لها خطط free tier سخية):

| الخدمة | الرابط | ما تحصل عليه مجاناً |
|---|---|---|
| Hugging Face | https://huggingface.co/join | توكن + وصول لنماذج Stable Diffusion |
| Google AI Studio | https://aistudio.google.com/ | مفتاح Gemini API (15 req/min) |
| Supabase | https://supabase.com/signup | مشروع + 500MB تخزين + PostgreSQL |
| Telegram | https://t.me/BotFather | بوت توكن (غير محدود) |
| GitHub | https://github.com/signup | مستودع + 2000 دقيقة Actions/شهر |

---

## 🖥️ النشر المحلي (للتطوير والاختبار)

### 1) استنساخ وتثبيت

```bash
git clone https://github.com/<your-username>/Pixel-ZeroBaran.git
cd Pixel-ZeroBaran

python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2) تنزيل نموذج Rembg

```bash
python -c "from rembg import new_session; new_session('u2net')"
# سيُنزّل ~176MB مرة واحدة في ~/.u2net/
```

### 3) إعداد المتغيرات البيئية

```bash
cp .env.example .env
# عبّئ القيم في .env (راجع التعليقات)
```

### 4) إعداد Supabase

1. ادخل Dashboard مشروعك في Supabase.
2. افتح **SQL Editor** والصق محتوى `docs/supabase_schema.sql` ثم نفّذه.
3. سيُنشئ الجدول + Buckets + السياسات تلقائياً.

### 5) إنشاء بوت تليجرام

1. تحدث مع [@BotFather](https://t.me/BotFather) على تليجرام.
2. أرسل `/newbot` واتبع التعليمات.
3. احفظ التوكن في `TELEGRAM_BOT_TOKEN`.
4. تحدث مع [@userinfobot](https://t.me/userinfobot) لمعرفة `TELEGRAM_CHAT_ID`.

### 6) فحص الإعدادات

```bash
python main.py check
```
يجب أن ترى ✅ لكل التبعيات والتنبيهات الوحيدة تكون عن المفاتيح الاختيارية.

### 7) التشغيل

```bash
# بوت تليجرام
python main.py bot

# لوحة Streamlit (http://localhost:8501)
python main.py dashboard
```

---

## ☁️ النشر على السحابة (مجاني)

### الخيار A: Render.com (لبوت تليجرام)

1. ادفع المستودع إلى GitHub.
2. اذهب إلى https://render.com وأنشئ **Web Service**.
3. اربط المستودع.
4. الإعدادات:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py bot`
   - **Instance Type**: Free
5. أضف متغيرات البيئة من `.env` في تبويب **Environment**.
6. انشر. سيبقى البوت يعمل 24/7 (قد ينام في الطبقة المجانية بعد 15 دقيقة من الخمول).

### الخيار B: Railway.app (بديل)

نفس الخطوات تقريباً، مع Start Command = `python main.py bot`.

### الخيار C: Hugging Face Spaces (للوحة Streamlit)

1. اذهب إلى https://huggingface.co/new-space.
2. اختر **Streamlit** كـ SDK.
3. ارفع ملفات المشروع.
4. أضف المتغيرات البيئية في **Settings → Variables and secrets**.
5. ستحصل على URL عام للوحة.

---

## ⚙️ تفعيل GitHub Actions للجدولة

1. اذهب إلى تبويب **Settings → Secrets and variables → Actions** في مستودعك.
2. أضف **Secrets** (تكون مخفية):

| Name | القيمة |
|---|---|
| `HF_TOKEN` | توكن Hugging Face |
| `GEMINI_API_KEY` | مفتاح Gemini |
| `SUPABASE_URL` | رابط Supabase |
| `SUPABASE_KEY` | مفتاح Supabase |
| `TELEGRAM_BOT_TOKEN` | توكن البوت |
| `TELEGRAM_CHAT_ID` | معرّف الدردشة |

3. أضف **Variables** (تظهر في السجلات):

| Name | القيمة الافتراضية |
|---|---|
| `HF_MODEL_BG` | `stabilityai/stable-diffusion-xl-base-1.0` |
| `HF_MODEL_INPAINT` | `runwayml/stable-diffusion-inpainting` |
| `GEMINI_MODEL` | `gemini-1.5-flash` |
| `SUPABASE_BUCKET_RAW` | `pixel-raw` |
| `SUPABASE_BUCKET_GENERATED` | `pixel-generated` |

4. اذهب إلى تبويب **Actions**.
5. ستجد workflow باسم **Pixel-ZeroBaran Batch Processor**.
6. اضغط **Enable workflows**.
7. لتشغيل يدوي: اضغط **Run workflow** واختر النمط.

الـ workflow سيعالج أي صور في مجلد `assets/raw/` يومياً عند منتصف الليل UTC.

---

## 🔄 تحديث المشروع

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py check
```

---

## 📊 مراقبة الاستهلاك

| الخدمة | أين تراقب؟ | الحد المجاني |
|---|---|---|
| Hugging Face | https://huggingface.co/settings/account | ~1000 inference/يوم |
| Gemini | https://aistudio.google.com/usage | 15 req/min, 1500/يوم |
| Supabase | https://supabase.com/dashboard/project/_/settings/billing | 500MB تخزين، 2GB bandwidth |
| GitHub Actions | https://github.com/settings/billing | 2000 دقيقة/شهر |
| Telegram | غير محدود | غير محدود |

---

## 🆘 استكشاف الأخطاء الشائعة

### `ModuleNotFoundError: No module named 'rembg'`
```bash
pip install rembg
# أو مع GPU:
pip install rembg[gpu]
```

### `onnxruntime` فشل في التحميل
```bash
# على الأنظمة القديمة:
pip install onnxruntime==1.16.0
```

### `HF API 401 Unauthorized`
- تأكد أن `HF_TOKEN` صحيح ومن https://huggingface.co/settings/tokens.
- اقبل شروط استخدام النموذج على صفحته (مثلاً https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0).

### `Supabase 401`
- `SUPABASE_KEY` يجب أن يكون **anon key** وليس service_role key، إلا للمهام الإدارية.

### `Telegram 409 Conflict`
- البوت يعمل في مكان آخر. أوقف كل العمليات الأخرى ثم أعد التشغيل.

### `Streamlit لا يظهر`
```bash
streamlit run dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 💾 النسخ الاحتياطي

- **الصور**: محفوظة في Supabase Storage (أو محلياً في `assets/`).
- **السجلات**: في جدول `pixel_zerobaran_assets` — صدّرها دورياً عبر SQL Editor.
- **الكود**: GitHub يحتفظ بالتاريخ الكامل.

---

## 📞 الدعم

لأي مشكلة في النشر، تواصل مع المؤلف:
- ✉️ Baranavisat@gmail.com
- 📱 00905313263722 (واتساب)

---

**© Baran Avisat — Pixel-ZeroBaran v1.0.0**
