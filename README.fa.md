# دستیار تحلیل داده با هوش مصنوعی

[English](README.md) | [فارسی](README.fa.md) | [دموی آنلاین](http://82.22.175.58:8080/)

یک ایجنت چندزبانه برای خواندن فایل‌های CSV، Excel و JSON، درک درخواست‌های چندبخشی فارسی یا انگلیسی، اجرای تحلیل‌های آماری و تولید نمودار.

## دموی آنلاین

**[اجرای دستیار تحلیل داده](http://82.22.175.58:8080/)**

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

## انتشار رایگان در وب

برنامهٔ Streamlit در یک فرایند اجرا می‌شود و برای دموی عمومی به backend جداگانه نیاز ندارد:

1. پروژه را در GitHub قرار دهید.
2. در [Streamlit Community Cloud](https://share.streamlit.io) یک App بسازید.
3. branch و فایل `streamlit_app.py` را انتخاب کنید.
4. در بخش Secrets مقادیر زیر را وارد کنید:

```toml
OPENROUTER_API_KEY = "کلید-جدید-شما"
LLM_MODEL = "qwen/qwen3-8b"
```

5. Deploy را بزنید و لینک HTTPS ساخته‌شده را به اشتراک بگذارید.

هرگز کلید واقعی را در GitHub یا فایل `.env.example` commit نکنید.

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

## استقرار با Docker

پیش‌نیازهای میزبان فقط Docker Engine و Docker Compose نسخهٔ ۲ هستند. برنامه داخل کانتینر با کاربر غیر root روی پورت `8501` اجرا می‌شود و فایل‌های بارگذاری‌شده و نمودارها در volumeهای Docker نگهداری می‌شوند.

فایل تنظیمات خصوصی را از نمونه بسازید و کلید لازم را در آن قرار دهید:

```bash
cp .env.example .env
chmod 600 .env
```

متغیر `OPENROUTER_API_KEY` برای تحلیل مبتنی بر هوش مصنوعی الزامی است. متغیرهای `LLM_MODEL`، `SITE_ADDRESS`، `PUBLIC_HTTP_PORT` و `STREAMLIT_HOST_PORT` قابل تنظیم‌اند. فایل `.env`، کلید API، رمز عبور، secretهای Streamlit و کلید خصوصی certificate نباید commit شوند.

ساخت و اجرای برنامه و Reverse Proxy مبتنی بر Caddy:

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f
```

بررسی سلامت Streamlit از اتصال خصوصی میزبان و توقف سرویس:

```bash
curl http://127.0.0.1:8601/_stcore/health
docker compose down
```

هر دو سرویس از `restart: unless-stopped` استفاده می‌کنند؛ بنابراین در صورت فعال‌بودن Docker service، پس از restart سرور دوباره اجرا می‌شوند، مگر اینکه قبلاً دستی متوقف شده باشند.

## استقرار روی VPS

معماری استقرار به‌شکل زیر است:

```text
Internet
  -> Caddy / Reverse Proxy (:8080)
  -> Docker network
  -> Streamlit (:8501)
  -> Data Analyst Agent
```

نسخهٔ فعلی روی VPS از آدرس **[http://82.22.175.58:8080/](http://82.22.175.58:8080/)** در دسترس است. در سرور دیگر، IP را جایگزین کنید و برای هر پروژه `PUBLIC_HTTP_PORT` و `STREAMLIT_HOST_PORT` متفاوتی در فایل خصوصی `.env` در نظر بگیرید. پورت داخلی Streamlit نباید مستقیماً public شود.

بدون دامنه، برنامه با قالب `http://SERVER_PUBLIC_IP:PUBLIC_HTTP_PORT` باز می‌شود. پس از تهیه دامنه فقط DNS و تنظیم Reverse Proxy تغییر می‌کنند و Docker یا کد برنامه نیاز به تغییر ندارند. Caddy، Let's Encrypt/Certbot یا راهکار ACME مشابه می‌تواند HTTPS را فراهم کند؛ فایل‌های certificate خصوصی را commit نکنید.

به‌روزرسانی نسخهٔ مستقر:

```bash
git pull
docker compose up -d --build
```

عیب‌یابی پایه:

```bash
docker compose ps
docker compose logs
docker inspect ai-data-analyst-app
curl http://127.0.0.1:8601/_stcore/health
curl http://SERVER_PUBLIC_IP:PUBLIC_HTTP_PORT/_stcore/health
```
