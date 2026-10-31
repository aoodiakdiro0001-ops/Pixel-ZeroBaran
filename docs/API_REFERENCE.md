# 📚 Pixel-ZeroBaran — مرجع الـ API الداخلي

> توثيق كل الكائنات والدوال العامة في المشروع.

---

## 📦 `config`

### `Settings` (dataclass)

الكائن المركزي لكل إعدادات النظام.

**الحقول الرئيسية:**

| الحقل | النوع | الوصف |
|---|---|---|
| `hf_token` | `str` | توكن Hugging Face |
| `hf_model_bg` | `str` | نموذج توليد الخلفية (افتراضي: SDXL) |
| `gemini_api_key` | `str` | مفتاح Gemini |
| `gemini_model` | `str` | نموذج Gemini (افتراضي: 1.5-flash) |
| `supabase_url` | `str` | رابط Supabase |
| `supabase_key` | `str` | مفتاح Supabase |
| `telegram_bot_token` | `str` | توكن بوت تليجرام |
| `raw_dir` | `Path` | مجلد الصور الخام محلياً |
| `output_dir` | `Path` | مجلد المخرجات محلياً |
| `default_output_size` | `tuple` | أبعاد الإخراج الافتراضية (1024×1024) |
| `scene_presets` | `dict` | قاموس الأنماط البصرية الجاهزة |

**الدوال:**
- `ensure_dirs()` — ينشئ المجلدات المحلية.
- `validate() -> List[str]` — يرجع قائمة بأخطاء الإعدادات الحرجة.

**الاستخدام:**
```python
from config import settings
settings.ensure_dirs()
errors = settings.validate()
```

### `AUTHOR` (dict)
معلومات المؤلف الكاملة: name, email, whatsapp, iban, project, version, license.

### `COPYRIGHT_NOTICE` (str)
نص حقوق الملكية الجاهز للعرض.

---

## 📦 `core.background_remover`

### `BackgroundRemover`

عزل المنتجات عن خلفياتها باستخدام Rembg.

**المُنشئ:**
```python
BackgroundRemover(model_name="u2net")
```
النماذج المتاحة: `u2net` (افتراضي), `u2netp` (أسرع، أقل دقة), `u2net_human_seg` (للأشخاص), `silueta`, `isnet-general-use`.

**الدوال:**

#### `remove_background(image_bytes=None, image_path=None, alpha_matting=False, sharpen=True) -> (bytes, dict)`
يزيل الخلفية من صورة.

**المعاملات:**
- `image_bytes`: بيانات الصورة الخام (يُفضّل).
- `image_path`: مسار بديل.
- `alpha_matting`: تفعيل تنعيم الحواف (أبطأ ~3x، أدق للأقمشة والشعر).
- `sharpen`: شحذ قناة الألفا لتحسين الحواف.

**الناتج:**
- `bytes`: PNG بشفافية.
- `dict`: `{elapsed_seconds, model, alpha_matting, output_format, output_bytes}`.

#### `process_directory(input_dir, output_dir) -> List[dict]`
يعالج كل صور في مجلد.

---

## 📦 `core.ai_generator`

### `HuggingFaceClient`

**المُنشئ:**
```python
HuggingFaceClient(token=None)  # إن لم يُمرر، يأخذ من settings.hf_token
```

**الدوال:**

#### `generate_background(prompt, width=1024, height=1024, model=None, retries=3) -> bytes`
يولّد صورة خلفية من نص. يُعيد المحاولة تلقائياً عند 503.

#### `inpaint_product_into_scene(product_png_bytes, scene_prompt, model=None) -> bytes`
يدمج المنتج في مشهد عبر inpainting.

---

### `GeminiClient`

**المُنشئ:**
```python
GeminiClient(api_key=None)
```

**الدوال:**

#### `craft_scene_prompt(product_description, style="luxury") -> str`
يصوغ وصفاً بصرياً احترافياً عبر Gemini. إن فشل، يستخدم fallback محلي.

#### `write_ad_copy(product_description, platform="instagram") -> dict`
يولّد نصاً إعلانياً عربياً + هاشتاجات.

**الناتج:**
```python
{
    "caption": "✨ النص الإعلاني العربي...",
    "hashtags": ["#هاشتاج1", "#hashtag2", ...]
}
```

---

### `AIVisualEngine`

المنسّق الموحّد الذي يجمع HuggingFace + Gemini.

**المُنشئ:**
```python
AIVisualEngine()  # يهيّئ عميلَين داخليين
```

**الدوال:**

#### `generate_ad(product_png_bytes, product_description, style="studio_marble", size=(1024,1024)) -> dict`
ينفّذ كامل عملية التوليد.

**الناتج:**
```python
{
    "image_bytes": <JPG bytes>,
    "scene_prompt": "luxury dark moody studio...",
    "ad_copy": {"caption": "...", "hashtags": [...]},
    "meta": {"elapsed_seconds": 23.4, "style": "luxury_dark", "size": (1024,1024), "engine": "HuggingFace+Gemini"}
}
```

---

## 📦 `core.storage`

### `SupabaseStorage`

**المُنشئ:**
```python
SupabaseStorage()  # يقرأ الإعدادات من settings تلقائياً
```

**الدوال:**

| الدالة | الناتج | الوصف |
|---|---|---|
| `upload_raw(image_bytes, filename) -> str` | URL عام | يرفع صورة خام |
| `upload_generated(image_bytes, filename) -> str` | URL عام | يرفع صورة مولّدة |
| `log_asset(**kwargs) -> None` | - | يسجل في قاعدة البيانات |
| `list_recent(limit=20) -> List[dict]` | قائمة سجلات | آخر N أصل |

### `LocalStorage`
نفس الواجهة لكن يخزّن في ملفات محلية. مفيد للتطوير بدون Supabase.

### `get_storage() -> SupabaseStorage | LocalStorage`
مصنع يرجع Supabase إن توفر، وإلا LocalStorage.

---

## 📦 `bot.telegram_bot`

### `PixelZeroBaranBot`

بوت تليجرام كامل المزايا.

**المُنشئ:**
```python
PixelZeroBaranBot()  # يهيّئ BackgroundRemover + AIVisualEngine + storage
```

**الدوال:**

| الدالة | الوصف |
|---|---|
| `run()` | يبدأ حلقة long-polling (تستمر حتى Ctrl+C) |
| `send_message(chat_id, text)` | يرسل رسالة نصية |
| `send_photo(chat_id, image_bytes, caption)` | يرسل صورة مع تعليق |
| `download_file(file_id) -> bytes` | ينزّل ملفاً من تليجرام |

**الأوامر المدعومة:**
- `/start` — ترحيب
- `/help` — شرح الاستخدام
- `/about` — معلومات المؤلف وحقوق الملكية
- `/styles` — عرض الأنماط المتاحة

**رسالة صورة مع شرح:**
أرسل صورة + caption بالصيغة:
```
وصف المنتج #اسم_النمط
```
مثال:
```
ساعة يد فاخرة فولاذية #luxury_dark
```

---

## 📦 `scripts.run_pipeline`

### `PixelZeroBaranPipeline`

خط الأنابيب الكامل لمعالجة صورة واحدة.

**المُنشئ:**
```python
PixelZeroBaranPipeline()
```

**الدالة الرئيسية:**

#### `run(image_bytes, product_description="منتج فاخر", style="studio_marble", size=None, source="pipeline", filename="product.png") -> PipelineResult`

**PipelineResult (dataclass):**
```python
@dataclass
class PipelineResult:
    cutout_path: str          # URL الصورة المعزولة
    generated_path: str       # URL الصورة النهائية
    scene_prompt: str         # وصف المشهد
    ad_caption: str           # النص الإعلاني
    ad_hashtags: list         # الهاشتاجات
    elapsed_seconds: float    # الزمن الكلي
    style: str                # النمط المستخدم
    status: str = "ok"
    error: Optional[str] = None
```

---

## 📦 `scripts.batch_processor`

### `batch_process(input_dir, style, product_description, size, delay_between) -> dict`

يعالج مجلداً كاملاً.

**الناتج:**
```python
{
    "total": 25,
    "ok": 23,
    "failed": 2,
    "elapsed": 612.4,
    "results": [
        {"file": "1.jpg", "status": "ok", ...PipelineResult...},
        {"file": "2.jpg", "status": "error", "error": "..."},
        ...
    ]
}
```

---

## 🖥️ CLI — `main.py`

```bash
python main.py <command> [options]
```

| Command | الوصف | الخيارات |
|---|---|---|
| `bot` | تشغيل بوت تليجرام | - |
| `dashboard` | تشغيل لوحة Streamlit | - |
| `pipeline <image>` | معالجة صورة واحدة | `--style`, `--desc`, `--size` |
| `batch <dir>` | معالجة دفعة | `--style`, `--desc`, `--size`, `--delay`, `--report` |
| `info` | معلومات المؤلف | - |
| `check` | فحص الإعدادات | - |

**أمثلة:**
```bash
python main.py bot
python main.py dashboard
python main.py pipeline assets/product.jpg --style luxury_dark --desc "ساعة ذهبية"
python main.py batch assets/raw/ --style studio_marble --delay 3 --report report.json
python main.py info
python main.py check
```

---

## 📐 أمثلة كود (Python API)

### مثال 1: معالجة صورة واحدة برمجياً
```python
from scripts.run_pipeline import PixelZeroBaranPipeline

pipeline = PixelZeroBaranPipeline()
result = pipeline.run(
    image_bytes=open("product.jpg", "rb").read(),
    product_description="عطر فاخر ذهبي",
    style="luxury_dark",
    source="my_script",
    filename="product.jpg",
)
print(f"الإعلان النهائي: {result.generated_path}")
print(f"النص: {result.ad_caption}")
```

### مثال 2: استخدام الطبقات منفصلة
```python
from core.background_remover import BackgroundRemover
from core.ai_generator import AIVisualEngine

remover = BackgroundRemover()
cutout, _ = remover.remove_background(image_path="product.jpg")

engine = AIVisualEngine()
result = engine.generate_ad(
    product_png_bytes=cutout,
    product_description="عطر فاخر",
    style="studio_marble",
)
open("ad.jpg", "wb").write(result["image_bytes"])
```

### مثال 3: استخدام Gemini فقط لصياغة نص إعلاني
```python
from core.ai_generator import GeminiClient

gemini = GeminiClient()
ad = gemini.write_ad_copy("قهوة عربية محمصة طازجة", platform="instagram")
print(ad["caption"])
print(" ".join(ad["hashtags"]))
```

---

**© Baran Avisat — Pixel-ZeroBaran v1.0.0**
