# StayEase - Hostel Management System

StayEase is a comprehensive, web-based Hostel Management System designed to streamline operations for 
administrators, wardens, security personnel, and students. It features strict Role-Based Access Control (RBAC) to 
ensure secure data isolation and a customized dashboard experience for every user type.

## Features

* **Student Dashboard:** View personal profile details, room allocation, payment history, and raise categorized maintenance complaints.
* **Security Gate Management:** Live tracking of visitors and student in/out movements with an interactive "Live Search" dropdown and one-click sign-in/sign-out functionality.
* **Warden Dashboard:** Oversee student movements, track damaged furniture inventory, and manage hostel-specific operations.
* **Admin Dashboard:** Global oversight of all members, system-wide complaints, overall room capacities, and global logs.
* **Secure Authentication:** JWT-based session management with programmatic backend route protection.

## Technology Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6)
* **Backend:** Python 3 (Flask)
* **Database:** MySQL (InnoDB engine)

---

##  Getting Started

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
Make sure you have the following installed on your system:
* [Python 3.8+](https://www.python.org/downloads/)
* [MySQL Server](https://dev.mysql.com/downloads/installer/) (and a GUI like MySQL Workbench)

### 2. Database Setup
1. Open MySQL Workbench (or your preferred SQL client).
2. Create a new database for the project:
   ```sql
   CREATE DATABASE stayease_db;
   USE stayease_db;
   ```
3. Execute stayease.sql code to create the required tables (`roles`, `hostels`, `rooms`, `members`, `room_allocations`, `visitor_logs`, `member_movement_logs`, `complaints`, etc.) and add sample data.

### 3. Backend Environment Setup
1. **Open your terminal** and navigate to the root directory of the project.
2. **Create a virtual environment** to keep dependencies clean:
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   * **Windows:** `venv\Scripts\activate`
   * **Mac/Linux:** `source venv/bin/activate`
4. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

### 4. Database Configuration
Connect the Flask application to your local MySQL database. Locate your database connection setup (typically in `utils.py`, `app.py`, or a `.env` file) and update the credentials to match your local setup:

```python
# Example Database Configuration
DB_HOST = "localhost"
DB_USER = "root"          # Your MySQL username
DB_PASSWORD = "password"  # Your MySQL password
DB_NAME = "stayease_db"
SECRET_KEY = "your_super_secret_jwt_key"
```

### 5. Run the Application
### 5. Run the Application
Ensure your terminal is navigated inside the `Module_B` directory. With your database running and the virtual environment activated, start the Flask development server by pointing to the app folder:
```bash
python app/app.py
```
* The terminal will output the server address (usually `http://127.0.0.1:5000`).
* Open your web browser and navigate to (http://127.0.0.1:5000/dashboard) to access the StayEase login portal.

---

## Project Structure

```text
CS432_Track1_Submission/
└── Module_B/
    ├── app/
        ├── static/                   # Frontend assets (style.css, script.js)
        ├── templates/                # HTML templates (index.html)
        ├── utils/                    # Helper modules
        ├── app.py                    # Main Flask application entry point
        ├── README.md                 # Project internal documentation
        ├── routes_admin.py           # API routes for Admin dashboard & operations
        ├── routes_auth.py            # Login, authentication, and session validation
        ├── routes_portfolio.py       # API routes for dynamic student dashboards
        ├── routes_security.py        # API routes for gate management & live search
        ├── utils.py                  # Database connection handlers & JWT decorators
    ├── benchmark.py                  # Python script for measuring query performance
    ├── benchmark_results.ipynb       # Raw output from the performance benchmarking
    ├── report.pdf                    # Final Optimization Implementation Report (LaTeX output)
    ├── requirements.txt              # Requirements file
    
    ├── logs/                 
          └── audit.log             # System audit, login tracking, and security logs
    
    ├── sql/                      # Database schema, indexes, and mock data scripts
       └── stayease.sql              # DUmp file to create everything
```

## 🔒 Default Logins (For Testing)
*(Note: Ensure these users exist in your `members` and credentials tables before testing)*
* **Admin:** `admin` / `admin123`
* **Warden:** `riya` / `admin123`
* **Security:** `security` / `admin123`
* **Student:** `priya` / `admin123`

* You can see user_credentials table to get member details, password for everyone is 'admin123'

## 👨‍💻 Developer Notes
* **Frontend Architecture:** This application uses a Single Page Application (SPA) paradigm. The HTML is statically loaded once, and JavaScript dynamically manipulates the DOM to hide/show specific sections (`class="hidden"`) based on the authenticated user's role.
* **Cache Clearing:** If you make updates to `script.js` or `style.css` and do not see the changes reflected in your browser, press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac) to hard refresh and clear the browser cache.
