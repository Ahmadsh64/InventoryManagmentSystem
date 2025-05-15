📦 Inventory Management System

A smart inventory management system for managing inventory in chain stores, including managing items, branches, purchases and reports.

## 🚀 System Requirements
Python (3.10 or 3.11 recommended)
MySQL Server (and make sure MySQL Workbench is installed)

## ⚙️ System Installation

1️⃣ Clone the project
Open the command prompt (Command Prompt / Terminal) and type:
git clone https://github.com/Ahmadsh64/InventoryManagmentSystem.git

2️⃣ Go to the project folder
cd InventoryManagmentSystem

3️⃣ Create a workspace and install libraries
python -m venv venv
Activate the environment:
Windows:
venv\Scripts\activate
Mac / Linux:
source venv/bin/activate

Then install the dependencies:
pip install -r requirements.txt

🛠️ Step 4 — Import the database on the new computer (Import)
1️⃣ Install MySQL on the computer
2️⃣ Create an empty database:
In MySQL Workbench or via the command line:
CREATE DATABASE inventory_system;

3️⃣ Import the file inventory_system.sql
via MySQL Workbench:
Server → Data Import
Choose Import from Self-Contained File

Select inventory_system.sql

In Default Target Schema - select the database: inventory_system

Click Start Import

via command line:

mysql -u root -p inventory_system < inventory_system.sql
⚙️ Step 3 — Update the connection function (if necessary)
The connection details should be the same (user, password, DB name) — your code works without change ✅

🖥️ Running the system

python main.py
or run in the main file

///////////////////////////////////////////////////////////////////

📦 Inventory Management System

מערכת ניהול מלאי חכמה לניהול מלאי בחנויות רשת, כולל ניהול פריטים, סניפים, רכישות ודוחות.

## 🚀 דרישות מערכת
Python (מומלץ 3.10 או 3.11 )
MySQL Server (ולוודא ש-MySQL Workbench מותקן)

## ⚙️ התקנת המערכת

1️⃣ לשכפל (clone) את הפרויקט
פתח את שורת הפקודה (Command Prompt / Terminal) והקלד:
git clone https://github.com/Ahmadsh64/InventoryManagmentSystem.git


2️⃣ לעבור לתיקיית הפרויקט
cd InventoryManagmentSystem

3️⃣ ליצור סביבת עבודה ולהתקין ספריות 
python -m venv venv
להפעיל את הסביבה:
Windows:
venv\Scripts\activate
Mac / Linux:
source venv/bin/activate

ואז להתקין את התלויות :
pip install -r requirements.txt

🛠️ שלב 4 — ייבוא למסד הנתונים במחשב החדש (Import)
1️⃣ התקן MySQL על המחשב
2️⃣ צור מסד נתונים ריק:
ב־MySQL Workbench  או דרך שורת הפקודה:
CREATE DATABASE inventory_system;

3️⃣ ייבא את הקובץ inventory_system.sql
דרך MySQL Workbench :
Server → Data Import
בחר Import from Self-Contained File

בחר את inventory_system.sql

ב Default Target Schema - בחר את המסד: inventory_system

לחץ Start Import

דרך שורת פקודה:

mysql -u root -p inventory_system < inventory_system.sql
⚙️ שלב 3 — לעדכן את פונקציית החיבור (אם צריך)
פרטי ההתחברות צריך להיות זהים (יוזר, סיסמה, שם DB) — הקוד שלך עובד בלי שינוי ✅

🖥️ הפעלת המערכת

python main.py
או run בקובץ main