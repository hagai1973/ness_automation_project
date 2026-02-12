סגור 👍
הנה Batch נקי ופשוט שיוצר רק קבצים (בלי תיקיות), בהנחה שאתה כבר נמצא בתוך תיקיית pages.

📄 create_pages_files.bat
@echo off
echo Creating page files...

type nul > base_page.py
type nul > home_page.py
type nul > products_page.py
type nul > product_detail_page.py
type nul > cart_page.py

echo.
echo Page files created successfully.
pause