# دستیار تحلیل داده با هوش مصنوعی

[English](README.md) | [فارسی](README.fa.md)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://da-agent.streamlit.app/)

**نسخه آنلاین:** [da-agent.streamlit.app](https://da-agent.streamlit.app/)

یک ایجنت چندزبانه برای خواندن فایل‌های CSV، Excel و JSON، درک درخواست‌های چندبخشی فارسی یا انگلیسی، اجرای تحلیل‌های آماری و تولید نمودار.

## قابلیت‌ها

- تشخیص نام ستون‌ها با وجود تفاوت حروف، فاصله، غلط‌های جزئی و معادل‌های فارسی و انگلیسی.
- اجرای چند تحلیل و چند نمودار در یک درخواست.
- تحلیل‌های توصیفی، داده‌های گمشده، همبستگی، نقاط پرت، فراوانی، گروه‌بندی و روند.
- نمودارهای هیستوگرام، جعبه‌ای، پراکندگی، خطی، میله‌ای، دایره‌ای و heatmap همبستگی.
- نمایش درست متن ترکیبی فارسی، انگلیسی و عدد با تشخیص خودکار راست‌به‌چپ و چپ‌به‌راست.
- استفاده از فونت Vazirmatn برای متن فارسی و برچسب نمودارها.
- پشتیبانی از جداکنندهٔ غیرمعمول فایل نمونهٔ فارسی داخل پوشهٔ `uploads`.

## اجرای محلی

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env
# کلید OpenRouter را در .env قرار دهید
.venv\Scripts\streamlit run streamlit_app.py
```

در ویندوز می‌توانید از `run_app.bat` استفاده کنید. رابط اختیاری FastAPI نیز با `run_backend.bat` اجرا می‌شود و مستندات آن در آدرس زیر قرار دارد:

```text
http://127.0.0.1:8000/docs
```

## نمونه درخواست

```text
سن را توصیف کن، نقاط پرت آن را بررسی کن، هیستوگرام و نمودار جعبه‌ای بساز و رابطهٔ سن و BMI را تحلیل کن.
```

مدل ابتدا schema واقعی فایل را دریافت می‌کند، مفهوم درخواست را به نام ستون‌های واقعی نگاشت می‌کند، تمام ابزارهای لازم را اجرا می‌کند و نتیجه را به زبان کاربر در قالب Markdown برمی‌گرداند.

## ساختار پروژه

```text
app/
  agent/orchestrator.py   # حلقهٔ چندمرحله‌ای ایجنت
  tools/                  # تحلیل و نمودارسازی
  loaders/                # خواندن CSV، Excel و JSON
  api/                    # endpointهای اختیاری FastAPI
streamlit_app.py          # دموی محلی و ابری
notebooks/ai_data_analyst_demo.ipynb
tests/
```

## تست

```powershell
.venv\Scripts\python -m pytest -q -p no:cacheprovider
```

تست‌ها بارگذاری فایل فارسی، تطبیق مفهومی ستون، روش‌های تحلیل، انواع نمودار، اجرای چند tool call، endpoint سلامت API و شروع Streamlit را پوشش می‌دهند.

فونت bundle‌شدهٔ [Vazirmatn](https://github.com/rastikerdar/vazirmatn) تحت مجوز SIL Open Font License 1.1 منتشر شده و متن مجوز آن در `assets/fonts/OFL.txt` قرار دارد.
