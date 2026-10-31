# 🎨 Pixel-ZeroBaran

> **المنظومة الذاتية الذكية لتوليد، هندسة، وتعديل الأصول البصرية وإعلانات المنتجات**
> — نظام متكامل مبني **بموارد مجانية 100%** لإنتاج صور إعلانية احترافية دون دفع دولار واحد.

---

## 👤 معلومات المؤلف وحقوق الملكية

| الحقل | القيمة |
|---|---|
| **اسم المشروع** | Pixel-ZeroBaran |
| **الإصدار** | 1.0.0 |
| **المؤلف** | Baran Avisat |
| **البريد الإلكتروني** | Baranavisat@gmail.com |
| **رقم الواتساب** | 00905313263722 |
| **الحساب البنكي (IBAN)** | `TR10 0001 0090 1008 4013 0050 01` |
| **الترخيص** | Proprietary — All Rights Reserved (Free to Use) |

```
© Baran Avisat — Project 'Pixel-ZeroBaran' v1.0.0.
All rights reserved. Built using 100% free and open-source resources.
```

> 📌 **الحقوق الفكرية**: هذا المشروع ثمرة عمل المطور Baran Avisat. يُسمح باستخدامه وتعديله
> لأغراض شخصية وتجارية، لكن **يجب الإبقاء على اسم المؤلف ومعلوماته في كل نسخة أو توزيع**.
> لأي دعم فني أو تعاون تجاري تواصل عبر البريد أو الواتساب أعلاه.

---

## 🌟 لماذا Pixel-ZeroBaran؟

| الميزة | الوصف |
|---|---|
| 💰 **توفير مال فلكي** | بديل مجاني بالكامل عن اشتراكات أدوات التصميم المدفوعة التي تكلف الشركات ثروات سنوياً. |
| ⚡ **إنتاج بصري فوري** | صور تسويقية وموكتات احترافية لمنتجاتك خلال ثوانٍ بدلاً من ساعات الانتظار. |
| 🔐 **السيادة الكاملة** | صور منتجاتك تُعالج في بيئتك السحابية الخاصة، لا تُستخدم لتدريب نماذج الآخرين. |
| 🤖 **ذكاء إبداعي** | Gemini يصوغ المشهد، و Stable Diffusion يولّد الخلفية، و Rembg يعزل المنتج — تناغم كامل. |

---

## 🛠️ الموارد المجانية البحتة المستخدمة

| المكون | الخدمة المجانية | الدور |
|---|---|---|
| محرك الجدولة | **GitHub Actions** | تنفيذ عمليات الدفعات المجدولة مجاناً (2000 دقيقة/شهر) |
| معالجة الصور | **Python + Pillow + Rembg** | إزالة الخلفيات تلقائياً بدقة عالية |
| الذكاء البصري | **Hugging Face Inference APIs** | توليد الخلفيات الإعلانية عبر Stable Diffusion |
| صياغة الأفكار | **Google Gemini API** | كتابة الأوصاف البصرية والنصوص الإعلانية بالعربية |
| التخزين والقاعدة | **Supabase** (PostgreSQL + Storage) | 500MB مجاناً للأصول والسجلات |
| الواجهة والتسليم | **Telegram Bot API + Streamlit** | تسليم فوري على الهاتف + لوحة تحكم ويب |

---

## 📐 البنية البرمجية (4 طبقات)

```
[رفع صورة المنتج الخام]
        │
        ▼
[① Python + Rembg  ← إزالة الخلفية بدقة]
        │
        ▼
[② HuggingFace + Gemini  ← توليد خلفية إعلانية + دمج المنتج]
        │
        ▼
[③ Supabase  ← تخزين الأصول + تسجيل السجلات]
        │
        ▼
[④ Telegram Bot / Streamlit  ← تسليم فوري على هاتفك]
```

### تفصيل الطبقات

1. **طبقة المعالجة والتنقية** (`core/background_remover.py`)
   يستخدم `Rembg` مع نموذج `u2net` لعزل المنتج خلال ثانية واحدة. يدعم `alpha-matting` لتنعيم الحواف.

2. **العقل الإبداعي والتوليدي** (`core/ai_generator.py`)
   - `GeminiClient` يصوغ وصفاً بصرياً احترافياً للمنتج.
   - `HuggingFaceClient` يولّد خلفية إعلانية مطابقة للوصف.
   - `AIVisualEngine` يدمج المنتج المعزول فوق الخلفية مع ظل طبيعي.

3. **طبقة الأرشيف والتخزين** (`core/storage.py`)
   - `SupabaseStorage` لرفع الصور الخام والمولّدة + تسجيل السجلات في PostgreSQL.
   - `LocalStorage` كـ fallback محلي عند غياب Supabase.

4. **طبقة التوصيل والتسليم** (`bot/telegram_bot.py` + `dashboard/streamlit_app.py`)
   - البوت يرسل لك الصورة الإعلانية النهائية فوراً مع النص والهاشتاجات.
   - لوحة Streamlit تتيح المعالجة البصرية من المتصفح.

---

## 🚀 طريقة التشغيل السريع

### 1) التثبيت

```bash
# استنساخ المستودع
git clone https://github.com/<username>/Pixel-ZeroBaran.git
cd Pixel-ZeroBaran

# إنشاء بيئة افتراضية
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# أو: .venv\Scripts\activate   (Windows)

# تثبيت التبعيات
pip install -r requirements.txt

# تنزيل نموذج rembg (مرة واحدة فقط)
python -c "from rembg import new_session; new_session('u2net')"
```

### 2) الإعدادات

```bash
# نسخ قالب البيئة
cp .env.example .env

# تعبئة المفاتيح (كلها مجانية — راجع التعليقات داخل الملف)
nano .env
```

### 3) فحص الإعدادات

```bash
python main.py check
```

### 4) تشغيل المكونات

```bash
# تشغيل بوت تليجرام
python main.py bot

# تشغيل لوحة Streamlit (افتح http://localhost:8501)
python main.py dashboard

# معالجة صورة واحدة عبر CLI
python main.py pipeline path/to/product.jpg --style studio_marble --desc "زجاجة عطر ذهبية"

# معالجة دفعة كاملة
python main.py batch path/to/folder --style luxury_dark --report report.json

# عرض معلومات المؤلف
python main.py info
```

---

## 🎨 الأنماط البصرية الجاهزة

| المفتاح | الوصف |
|---|---|
| `studio_marble` | سطح رخامي فاخر مع إضاءة استوديو ناعمة (الافتراضي) |
| `sunny_beach` | شاطئ مشمس بوقت الذهبي مع موجات المحيط |
| `minimal_white` | خلفية بيضاء نقية مع ظل خفيف (مثالي للـ e-commerce) |
| `luxury_dark` | استوديو داكن درامي مع إضاءة جانبية سينمائية |
| `forest_nature` | غابة خضراء مع طحالب وخشب طبيعي وإضاءة متلألئة |

يمكن إضافة أنماط جديدة بسهولة من `config.py` في قاموس `scene_presets`.

---

## ⚙️ GitHub Actions للجدولة التلقائية

ملف `.github/workflows/cron-batch.yml` يعالج أي صور في مجلد `assets/raw/` بشكل يومي تلقائياً، أو يدوياً عبر زر **Run workflow** في تبويب Actions.

**المطلوب إعداد Secrets و Variables في GitHub:**

| Type | Name | الوصف |
|---|---|---|
| Secret | `HF_TOKEN` | توكن Hugging Face |
| Secret | `GEMINI_API_KEY` | مفتاح Gemini |
| Secret | `SUPABASE_URL` | رابط مشروع Supabase |
| Secret | `SUPABASE_KEY` | مفتاح Supabase |
| Secret | `TELEGRAM_BOT_TOKEN` | توكن بوت تليجرام |
| Secret | `TELEGRAM_CHAT_ID` | معرّف الدردشة |
| Variable | `HF_MODEL_BG` | اسم النموذج الافتراضي |
| Variable | `SUPABASE_BUCKET_RAW` | اسم bucket الخام |
| Variable | `SUPABASE_BUCKET_GENERATED` | اسم bucket المولّد |

---

## 🗂️ بنية المشروع

```
Pixel-ZeroBaran/
├── main.py                       # نقطة دخول موحّدة (bot/dashboard/pipeline/batch/info/check)
├── config.py                     # الإعدادات المركزية + معلومات المؤلف
├── requirements.txt              # التبعيات
├── .env.example                  # قالب المتغيرات البيئية
├── .gitignore
│
├── core/                         # الطبقات الأساسية
│   ├── __init__.py
│   ├── background_remover.py     # ① إزالة الخلفية (Rembg)
│   ├── ai_generator.py           # ② HuggingFace + Gemini + الدمج
│   └── storage.py                # ③ Supabase + LocalStorage fallback
│
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py           # ④ بوت تليجرام للتسليم الفوري
│
├── dashboard/
│   └── streamlit_app.py          # ④ لوحة تحكم ويب
│
├── scripts/
│   ├── __init__.py
│   ├── run_pipeline.py           # خط الأنابيب الكامل
│   └── batch_processor.py        # معالج الدفعات
│
├── .github/workflows/
│   └── cron-batch.yml            # جدولة GitHub Actions
│
├── workflows/
│   └── backup-workflow.yml       # نسخة احتياطية
│
├── tests/
│   └── test_basic.py             # اختبارات أساسية
│
├── docs/
│   ├── ARCHITECTURE.md           # تفصيل البنية الهندسية
│   ├── DEPLOYMENT.md             # دليل النشر الكامل
│   ├── API_REFERENCE.md          # مرجع الـ API الداخلي
│   └── supabase_schema.sql       # مخطط قاعدة البيانات
│
├── assets/                       # (يُنشأ تلقائياً)
│   ├── raw/
│   ├── output/
│   └── temp/
│
├── LICENSE                       # الترخيص وحقوق الملكية
├── AUTHORS.md                    # قائمة المساهمين
├── CONTRIBUTING.md               # دليل المساهمة
└── CHANGELOG.md                  # سجل التغييرات
```

---

## 📊 سيناريو الاستخدام النموذجي

1. **التاجر** يفتح تليجرام ويرسل صورة منتج مع `caption`: "ساعة يد فاخرة فولاذية `#luxury_dark`".
2. **البوت** ينزّل الصورة، يرفعها إلى Supabase raw bucket.
3. **Rembg** يعزل الساعة عن خلفيتها الأصلية في ثانية واحدة.
4. **Gemini** يصوغ وصفاً: "luxury dark moody studio, dramatic rim lighting, premium steel watch placement, cinematic atmosphere, 8k advertising photography".
5. **Stable Diffusion** يولّد خلفية استوديو داكنة مطابقة.
6. المحرك يدمج الساعة المعزولة فوق الخلفية مع ظل طبيعي.
7. الناتج يُرفع إلى Supabase generated bucket ويُسجّل في قاعدة البيانات.
8. **البوت** يرسل للمستخدم خلال 30-60 ثانية: الصورة النهائية + نص إعلاني عربي + هاشتاجات.
9. **التاجر** ينشر الإعلان مباشرة على متجره أو حساباته.

**التكلفة الإجمالية: 0.00$** 💚

---

## 🧪 الاختبارات

```bash
# تثبيت pytest
pip install pytest

# تشغيل الاختبارات
pytest tests/ -v

# أو بدون pytest
python tests/test_basic.py
```

---

## 🔧 استكشاف الأخطاء

| المشكلة | الحل |
|---|---|
| `rembg` لا يعمل | ثبّت `onnxruntime`: `pip install onnxruntime` |
| `HF API returns 503` | النموذج قيد التحميل — انتظر 20 ثانية وأعد المحاولة (الكود يفعل ذلك تلقائياً) |
| `Supabase connection failed` | تأكد من URL & KEY في `.env`، وأن الجداول منشأة عبر `docs/supabase_schema.sql` |
| `Telegram bot لا يستقبل` | تحقق من التوكن عبر `BotFather`، وأن البوت ليس قيد التشغيل في مكانين معاً |
| الصور الناتجة فارغة | راجع `assets/temp/` وفعّل `alpha_matting=True` في `BackgroundRemover` |

---

## 📜 الترخيص وحقوق الملكية

هذا المشروع محمي بحقوق الملكية الفكرية للمؤلف **Baran Avisat**.

- ✅ **يُسمح**: الاستخدام الشخصي والتجاري، التعديل، التوزيع مع الإبقاء على اسم المؤلف.
- ❌ **يُمنع**: إزالة معلومات المؤلف، بيع المشروع كوداً خاماً دون إضافة قيمة، نِسبته لشخص آخر.

للاستفسارات التجارية أو طلب تطوير مخصص، تواصل مباشرة:
- ✉️ Baranavisat@gmail.com
- 📱 00905313263722 (واتساب)

راجع ملف `LICENSE` للتفاصيل الكاملة.

---

## 🤝 المساهمة

راجع `CONTRIBUTING.md`. كل المساهمات موضع ترحيب — افتح issue أو pull request.
سيُضاف اسمك إلى `AUTHORS.md`.

---

## 📈 خارطة الطريق

- [x] إزالة الخلفية بدقة عالية
- [x] توليد خلفيات إعلانية بـ 5 أنماط جاهزة
- [x] تكامل Supabase للتخزين والسجلات
- [x] بوت تليجرام للتسليم الفوري
- [x] لوحة Streamlit للتحكم البصري
- [x] جدولة GitHub Actions للدفعات
- [ ] دعم الفيديو القصير (Reels/TikTok)
- [ ] توليد كتالوج PDF تلقائي
- [ ] واجهة عربية كاملة RTL للوحة Streamlit
- [ ] دعم نماذج Flux المجانية على HuggingFace

---

## 💚 شكر وتقدير

- فريق **Hugging Face** على البنية التحتية المجانية للنماذج.
- فريق **Google** على الطبقة المجانية السخية من Gemini.
- فريق **Supabase** على المنصة المجانية الرائعة.
- فريق **Rembg** على المكتبة مفتوحة المصدر.
- مجتمع **Python** كله.

---

**© Baran Avisat 2026 — Pixel-ZeroBaran v1.0.0 — All Rights Reserved.**
