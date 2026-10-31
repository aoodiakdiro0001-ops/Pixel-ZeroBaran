"""
Pixel-ZeroBaran | لوحة التحكم (Streamlit Dashboard)
=====================================================
واجهة ويب محلية لرفع صور المنتجات، اختيار النمط البصري،
ومعالجة الدفعات بصرية مباشرة.
"""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

# ضمان استيراد الإعدادات من جذر المشروع
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from PIL import Image

from config import settings, AUTHOR, COPYRIGHT_NOTICE
from core.background_remover import BackgroundRemover
from core.ai_generator import AIVisualEngine
from core.storage import get_storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("pixel-zerobaran.dashboard")


# --------------------------------------------------------------------------- #
@st.cache_resource
def get_components():
    """يُهيّئ المكونات الثقيلة مرة واحدة فقط."""
    return BackgroundRemover(), AIVisualEngine(), get_storage()


# --------------------------------------------------------------------------- #
def main():
    st.set_page_config(
        page_title="Pixel-ZeroBaran",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ----- الترويسة -----
    st.markdown(
        """
        <style>
        .pixel-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 2rem;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .pixel-header h1 { margin: 0; font-size: 2.4rem; letter-spacing: 2px; }
        .pixel-header p { opacity: 0.85; margin-top: 0.5rem; }
        </style>
        <div class="pixel-header">
            <h1>🎨 Pixel-ZeroBaran</h1>
            <p>المنظومة الذاتية الذكية لتوليد الأصول البصرية والإعلانات</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- الشريط الجانبي -----
    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")
        style = st.selectbox(
            "النمط البصري",
            list(settings.scene_presets.keys()),
            format_func=lambda k: k.replace("_", " ").title(),
        )
        product_desc = st.text_area(
            "وصف المنتج",
            value="منتج فاخر",
            help="وصف مختصر يساعد الذكاء الاصطناعي على صياغة المشهد المناسب.",
        )
        size = st.select_slider(
            "أبعاد الإخراج",
            options=[512, 768, 1024, 1280],
            value=1024,
        )
        run_pipeline = st.checkbox("تشغيل كامل (إزالة + توليد)", value=True)

        st.markdown("---")
        st.markdown(f"**👤 المؤلف:** {AUTHOR['name']}")
        st.markdown(f"**✉️ البريد:** `{AUTHOR['email']}`")
        st.markdown(f"**📱 واتساب:** `{AUTHOR['whatsapp']}`")
        st.markdown(f"**🏷️ الإصدار:** v{AUTHOR['version']}")
        st.caption(COPYRIGHT_NOTICE)

    # ----- المنطقة الرئيسية -----
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 ارفع صورة المنتج")
        uploaded = st.file_uploader(
            "اسحب وأفلِت صورة هنا",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        if uploaded:
            st.image(uploaded, caption="الصورة الأصلية", use_column_width=True)

        if st.button("🚀 ابدأ المعالجة", type="primary", disabled=not uploaded):
            process_uploaded(uploaded, style, product_desc, size, run_pipeline)

    with col2:
        st.markdown("### 🗂️ آخر الأصول المولّدة")
        display_recent_assets()


# --------------------------------------------------------------------------- #
def process_uploaded(uploaded, style, product_desc, size, run_pipeline):
    remover, engine, storage = get_components()

    progress = st.progress(0.0, text="جارٍ التحضير...")
    raw_bytes = uploaded.getvalue()

    # حفظ الصورة الخام
    storage.upload_raw(raw_bytes, uploaded.name)
    progress.progress(0.15, text="تم رفع الصورة الخام.")

    # 1) إزالة الخلفية
    with st.spinner("✂️ إزالة الخلفية..."):
        cutout_bytes, _ = remover.remove_background(image_bytes=raw_bytes)
    progress.progress(0.45, text="تم عزل المنتج.")

    # عرض المنتج المعزول
    st.image(cutout_bytes, caption="المنتج المعزول", use_column_width=True)

    if not run_pipeline:
        st.success("✅ تم إزالة الخلفية بنجاح!")
        st.download_button(
            "⬇️ تحميل المنتج المعزول (PNG)",
            cutout_bytes,
            file_name=f"{Path(uploaded.name).stem}_cutout.png",
            mime="image/png",
        )
        return

    # 2) توليد الإعلان
    with st.spinner("🎨 توليد الخلفية الإعلانية..."):
        try:
            result = engine.generate_ad(
                product_png_bytes=cutout_bytes,
                product_description=product_desc,
                style=style,
                size=(size, size),
            )
        except Exception as exc:
            st.error(f"❌ فشل التوليد: {exc}")
            return

    progress.progress(1.0, text="اكتمل!")

    # 3) حفظ الناتج
    generated_url = storage.upload_generated(
        result["image_bytes"], f"{Path(uploaded.name).stem}_ad.jpg"
    )
    storage.log_asset(
        source="streamlit",
        raw_path=uploaded.name,
        generated_path=generated_url,
        scene_prompt=result["scene_prompt"],
        style=style,
        ad_caption=result["ad_copy"].get("caption", ""),
        ad_hashtags=result["ad_copy"].get("hashtags", []),
        elapsed_seconds=result["meta"]["elapsed_seconds"],
        status="ok",
    )

    # عرض النتيجة
    st.markdown("### 🖼️ الإعلان النهائي")
    st.image(result["image_bytes"], use_column_width=True)

    st.markdown("### 📝 النص الإعلاني")
    ad = result["ad_copy"]
    st.write(ad.get("caption", ""))
    if ad.get("hashtags"):
        st.write(" ".join(f"`{h}`" for h in ad["hashtags"]))

    st.download_button(
        "⬇️ تحميل الإعلان (JPG)",
        result["image_bytes"],
        file_name=f"{Path(uploaded.name).stem}_ad.jpg",
        mime="image/jpeg",
    )

    st.success(f"✅ اكتمل في {result['meta']['elapsed_seconds']} ثانية")


# --------------------------------------------------------------------------- #
def display_recent_assets():
    remover, engine, storage = get_components()
    try:
        records = storage.list_recent(limit=6)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"تعذّر جلب السجلات: {exc}")
        return

    if not records:
        st.info("لا توجد أصول بعد. ابدأ بمعالجة صورة!")
        return

    for rec in records:
        with st.expander(f"{rec.get('style', '?')} — {rec.get('created_at', '')}"):
            st.write(f"**النص:** {rec.get('ad_caption', '')}")
            if rec.get("ad_hashtags"):
                st.write(" ".join(rec["ad_hashtags"]))
            if rec.get("generated_path", "").startswith("http"):
                st.image(rec["generated_path"], use_column_width=True)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
