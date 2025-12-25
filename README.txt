# สร้าง venv
python -m venv venv

# เปิดใช้งาน (Windows)
.\venv\Scripts\activate

# ติดตั้งตัวเชื่อมต่อ Postgres
pip install psycopg2-binary

# ใช้ venv
Ctrl + Shift + Postgres
Select: Python: Select Interpreter
Select: ('venv': venv)