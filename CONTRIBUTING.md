# 🤝 CONTRIBUTING — Pixel-ZeroBaran

شكراً لاهتمامك بالمساهمة في **Pixel-ZeroBaran**! هذا الدليل يشرح كيف تساهم بفعالية.

---

## 📋 قبل البدء

1. اقرأ [README.md](README.md) و [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) لفهم البنية.
2. تأكد أن ملاحظتك أو ميزتك غير مطروحة بالفعل في [Issues](../../issues).

---

## 🐛 الإبلاغ عن الأخطاء

افتح issue بالصيغة التالية:

```markdown
**وصف الخطأ:** ...
**خطوات الإعادة:**
1. ...
2. ...
**السلوك المتوقع:** ...
**السلوك الفعلي:** ...
**البيئة:**
- نظام التشغيل: 
- إصدار Python: 
- إصدار Pixel-ZeroBaran: 
**مرفقات:** (لقطات شاشة / سجلات)
```

---

## ✨ اقتراح ميزة

افتح issue بعنوان `[Feature] وصف الميزة` واشرح:
- المشكلة التي تحلها.
- الحل المقترح.
- بدائل جرت في الحسبان.

---

## 🔧 إرسال Pull Request

### 1) التحضير

```bash
fork المستودع على GitHub
git clone https://github.com/<your-username>/Pixel-ZeroBaran.git
cd Pixel-ZeroBaran
git checkout -b feature/اسم-الميزة
```

### 2) التطوير

- اتبع نمط الكود الموجود (PEP 8 + type hints + docstrings عربية).
- أضف اختبارات في `tests/` لكل ميزة جديدة.
- حدّث التوثيق في `docs/` إن لزم.
- لا تُضِف ملفات `.env` أو مفاتيح سرية.

### 3) الاختبار

```bash
# تشغيل الاختبارات
pytest tests/ -v

# فحص الإعدادات
python main.py check

# تجربة يدوية
python main.py pipeline assets/sample.jpg --style studio_marble
```

### 4) الالتزام (Commit)

استخدم رسائل commit واضحة بالصيغة:
```
<type>: <وصف مختصر>

<تفاصيل اختيارية>
```

الأنواع:
- `feat`: ميزة جديدة
- `fix`: إصلاح خطأ
- `docs`: توثيق
- `refactor`: إعادة هيكلة
- `test`: اختبارات
- `chore`: مهام صيانة

مثال:
```
feat: إضافة نمط بصري جديد 'cyberpunk_neon'

نمط جديد بخلفية نيون مستقبلية مع إضاءة درامية.
تم تحديث scene_presets في config.py.
```

### 5) الإرسال

```bash
git push origin feature/اسم-الميزة
# ثم افتح Pull Request على GitHub
```

---

## 📜 معايير المراجعة

سيتم قبول PRs التي:
- ✅ تتبع نمط الكود.
- ✅ تجتاز الاختبارات.
- ✅ تحوي توثيقاً محدّثاً.
- ✅ لا تكسر التوافق مع الإصدارات السابقة (أو تُحدّث رقم الإصدار).
- ✅ تحافظ على روح "موارد مجانية 100%".

---

## 🎨 إضافة نمط بصري جديد

مثال كامل لإضافة نمط `cyberpunk_neon`:

```python
# في config.py → scene_presets
"cyberpunk_neon": (
    "futuristic cyberpunk product photography, neon pink and blue lighting, "
    "rainy city street background, holographic reflections, "
    "blade runner aesthetic, cinematic, 8k ultra detailed"
),
```

ثم:
1. أضف الاختبار في `tests/test_basic.py` للتأكد من وجود النمط.
2. أضف النمط لخيارات `--style` في `main.py`.
3. أضف النمط لقائمة `style` choice في GitHub Actions workflow.
4. حدّث README و API_REFERENCE.

---

## 💬 التواصل

للأسئلة المفتوحة أو النقاشات المعمارية:
- 📧 Baranavisat@gmail.com
- 📱 00905313263722 (واتساب)

---

## 📜 اتفاقية المساهمة

بإرسالك أي مساهمة، توافق على:
- منح Baran Avisat حق دمجها في المشروع.
- الإسناد لاسمك في `AUTHORS.md`.
- احترام حقوق الملكية الفكرية للمؤلف كما في `LICENSE`.

---

**© Baran Avisat — Pixel-ZeroBaran v1.0.0**
