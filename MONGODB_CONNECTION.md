# MongoDB Connection Guide

این راهنما نحوه اتصال به MongoDB با authentication را توضیح می‌دهد.

---

## 🔐 روش‌های اتصال

### روش 1: استفاده از URI کامل (پیشنهادی)

اگر URI کامل دارید (مثلاً از MongoDB Atlas)، مستقیماً در `.env` قرار دهید:

```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/novoxpert?retryWrites=true&w=majority
MONGODB_DB_NAME=novoxpert
```

### روش 2: استفاده از Username/Password جداگانه

اگر MongoDB محلی با authentication دارید:

```env
# Base URI (بدون credentials)
MONGODB_URI=mongodb://localhost:27017

# Credentials
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_AUTH_SOURCE=admin

# Database
MONGODB_DB_NAME=novoxpert
```

API به صورت خودکار این اطلاعات را ترکیب می‌کند و URI نهایی را می‌سازد.

### روش 3: استفاده از Host/Port جداگانه

```env
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_secure_password
MONGODB_AUTH_SOURCE=admin
MONGODB_DB_NAME=novoxpert
```

---

## 📝 نمونه‌های مختلف

### MongoDB بدون Authentication (Development)
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=novoxpert
MONGODB_USERNAME=
MONGODB_PASSWORD=
```

### MongoDB با Authentication (Local)
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=mySecurePassword123
MONGODB_AUTH_SOURCE=admin
MONGODB_DB_NAME=novoxpert
```

### MongoDB Atlas (Cloud)
```env
MONGODB_URI=mongodb+srv://cluster0.abc123.mongodb.net/
MONGODB_USERNAME=myuser
MONGODB_PASSWORD=mypassword
MONGODB_DB_NAME=novoxpert
```

### Docker MongoDB
```env
MONGODB_URI=mongodb://mongodb:27017
MONGODB_USERNAME=root
MONGODB_PASSWORD=example
MONGODB_AUTH_SOURCE=admin
MONGODB_DB_NAME=novoxpert
```

---

## 🔧 تنظیمات اضافی

### Connection Pool
```env
MONGODB_MIN_POOL_SIZE=10    # حداقل تعداد connection
MONGODB_MAX_POOL_SIZE=50    # حداکثر تعداد connection
```

### Authentication Source
```env
# معمولاً admin است، اما می‌تواند نام database دیگری باشه
MONGODB_AUTH_SOURCE=admin
```

---

## ⚠️ نکات امنیتی

### 1. محافظت از Credentials
```bash
# هرگز .env را در Git commit نکنید
echo ".env" >> .gitignore

# فقط .env.example را commit کنید
```

### 2. استفاده از Environment Variables قوی
```env
# ❌ بد
MONGODB_PASSWORD=123456

# ✅ خوب
MONGODB_PASSWORD=mY$ecur3P@ssw0rd!2024
```

### 3. URL Encoding
اگر password شما کاراکترهای خاص دارد (@, :, /, etc.)، API به صورت خودکار آن‌ها را encode می‌کند.

```env
# Password: my@pass:word
MONGODB_PASSWORD=my@pass:word
# Automatically encoded to: my%40pass%3Aword
```

---

## ✅ تست اتصال

### 1. اجرای API
```bash
uvicorn app.main:app --reload
```

### 2. بررسی Health Check
```bash
curl http://localhost:8000/api/v1/health
```

پاسخ موفق:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-20T...",
  "database": {
    "connected": true,
    "ping_ms": 5.2
  },
  "version": "1.0.0"
}
```

### 3. بررسی Logs
در console باید این پیام را ببینید:
```
✅ Connected to MongoDB: novoxpert
```

---

## 🐛 عیب‌یابی

### خطا: Authentication failed
```
❌ Failed to connect to MongoDB: Authentication failed
```

**راه حل:**
- Username و password را بررسی کنید
- مطمئن شوید `MONGODB_AUTH_SOURCE` صحیح است (معمولاً `admin`)
- مطمئن شوید user دسترسی به database دارد

### خطا: Connection timeout
```
❌ Failed to connect to MongoDB: [Errno 111] Connection refused
```

**راه حل:**
- مطمئن شوید MongoDB در حال اجراست: `sudo systemctl status mongod`
- Host و Port را بررسی کنید
- Firewall را بررسی کنید

### خطا: Database not found
```
❌ Database 'novoxpert' not found
```

**راه حل:**
- نام database را در `.env` بررسی کنید
- MongoDB database را به صورت دستی ایجاد کنید:
```bash
mongosh
use novoxpert
db.news.insertOne({test: true})
```

---

## 📚 منابع

- [MongoDB Connection String URI Format](https://docs.mongodb.com/manual/reference/connection-string/)
- [MongoDB Authentication](https://docs.mongodb.com/manual/core/authentication/)
- [Motor Documentation](https://motor.readthedocs.io/)

---

## 💡 نکته

اگر از **Docker Compose** استفاده می‌کنید، در Phase بعدی این تنظیمات را خودکار می‌کنیم!
