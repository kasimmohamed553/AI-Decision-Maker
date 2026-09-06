# AI-Decision-Maker
# 🤖 AI Decision Maker

> An intelligent business decision-support web application that analyzes sales datasets and generates transparent, data-driven recommendations using a rule-based decision engine.

## 📌 Overview

**AI Decision Maker** is a full-stack web application designed to help businesses make decisions from sales data.

Users can:

* Create an account
* Log in securely
* Upload CSV or Excel files
* Automatically analyze sales data
* Detect relevant columns
* Calculate business metrics
* Evaluate sales growth and performance
* Generate a decision score
* Receive an **EXPAND / MAINTAIN / REDUCE** recommendation
* View the reasoning behind the decision

The system is designed to be **transparent and explainable** rather than acting as a black-box AI system.

---

## 🎯 Problem Statement

Businesses often have large amounts of sales data but may struggle to convert that data into actionable decisions.

Traditional analysis requires manually:

* Cleaning datasets
* Identifying important columns
* Calculating sales metrics
* Comparing performance
* Identifying risks
* Making business recommendations

This project automates these steps and converts raw sales data into an easy-to-understand business decision.

---

## ✨ Key Features

### 🔐 User Authentication

The application provides:

* User registration
* Secure login
* Password hashing using bcrypt
* JWT-based authentication
* Protected data-analysis endpoint

Passwords are never stored as plain text.

---

### 📂 Dataset Upload

Users can upload:

* CSV files
* XLSX files
* XLS files

The backend automatically processes the uploaded dataset.

---

### 🧠 Automatic Column Detection

The analyzer does not depend on one fixed dataset format.

It can identify common variations of columns such as:

```text
Amount
Order_Amount
Sales
Revenue
Total
Price
Transaction_Amount
```

It can also detect optional fields such as:

```text
Product
Category
Region
Order_Date
```

If an amount column cannot be identified by name, the system attempts to find the most suitable numeric column automatically.

---

## 📊 Sales Analysis

The system calculates important business metrics including:

* Total sales
* Average order value
* Total orders
* Maximum order value
* Minimum order value
* Top-performing product
* Product sales breakdown
* Top category
* Category sales breakdown
* Top region
* Regional sales breakdown
* Sales growth rate

---

# 🧠 Decision Engine

The core of the application is the **rule-based decision engine**.

It evaluates four major signals:

| Signal           | Purpose                                   |
| ---------------- | ----------------------------------------- |
| 📈 Growth        | Measures sales trend                      |
| 💰 Order Value   | Evaluates average customer spending       |
| 📦 Volume        | Measures order volume                     |
| ⚠️ Concentration | Identifies dependence on a single product |

Each signal contributes points to an overall score.

The final score ranges from:

```text
-100 → +100
```

---

## 📈 Growth Analysis

Sales growth is evaluated using the first and second halves of the dataset.

| Growth        | Score |
| ------------- | ----: |
| ≥ 20%         |   +35 |
| 5% – 19.99%   |   +20 |
| -5% – 4.99%   |     0 |
| -20% – -5.01% |   -20 |
| < -20%        |   -35 |

---

## 💰 Average Order Value

The engine evaluates average order value.

| Average Order Value | Score |
| ------------------- | ----: |
| ≥ 2000              |   +15 |
| 500 – 1999.99       |    +5 |
| < 500               |   -10 |

---

## 📦 Order Volume

Order volume acts as a confidence signal.

| Orders   | Score |
| -------- | ----: |
| ≥ 500    |   +15 |
| 50 – 499 |    +5 |
| < 50     |    -5 |

---

## ⚠️ Product Concentration Risk

The system checks whether too much revenue depends on one product.

| Top Product Sales Share | Score |
| ----------------------- | ----: |
| ≥ 60%                   |   -15 |
| 40% – 59.99%            |    -5 |
| < 40%                   |    +5 |

This helps identify potential business concentration risk.

---

# 🚦 Final Decision

The combined score determines the recommended business direction.

```text
             Score
               │
      ┌────────┼────────┐
      │        │        │
      ▼        ▼        ▼
   REDUCE   MAINTAIN  EXPAND
   < -10    -10 to 29  ≥ 30
```

### 🟢 EXPAND

Recommended when the business shows strong overall signals.

Possible actions:

* Increase inventory
* Increase marketing
* Expand into high-performing regions
* Focus on successful products

### 🟡 MAINTAIN

Recommended when performance is relatively stable.

Possible action:

* Maintain the current strategy
* Continue monitoring key metrics

### 🔴 REDUCE

Recommended when negative signals dominate.

Possible actions:

* Reduce spending
* Review underperforming products
* Reassess pricing
* Review product mix

---

# 💡 Recommendation Engine

In addition to the main decision, the system generates practical recommendations based on the analyzed data.

Examples include:

* Investigating a recent sales decline
* Replicating successful regional strategies
* Promoting high-performing categories
* Increasing average order value through bundling
* Adding additional dataset columns for deeper analysis

---

# 🏗️ System Architecture

```text
                    USER
                     │
                     ▼
            ┌─────────────────┐
            │    FRONTEND     │
            │ HTML/CSS/JS     │
            └────────┬────────┘
                     │
                     │ HTTP / JSON
                     ▼
            ┌─────────────────┐
            │   FLASK API     │
            │     app.py      │
            └────────┬────────┘
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
      ┌────────┐ ┌────────┐ ┌──────────────┐
      │  AUTH  │ │ANALYZER│ │RECOMMENDATION│
      │  JWT   │ │        │ │    ENGINE    │
      └────────┘ └───┬────┘ └──────┬───────┘
                      │             │
                      ▼             │
                ┌──────────────┐    │
                │   DECISION   │◄───┘
                │    ENGINE    │
                └──────┬───────┘
                       │
                       ▼
              ┌─────────────────┐
              │ EXPAND /        │
              │ MAINTAIN /      │
              │ REDUCE          │
              └─────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

* Python
* Flask
* Flask-CORS
* Flask-SQLAlchemy
* Flask-Bcrypt
* Flask-JWT-Extended
* python-dotenv

## Data Analysis

* Pandas
* OpenPyXL

## Frontend

* HTML5
* CSS3
* JavaScript

## Database

* SQLite

## Authentication

* JWT
* Bcrypt password hashing

---

# 📁 Project Structure

```text
ai_decision_maker/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── auth.py
│   ├── analyzer.py
│   ├── decision_engine.py
│   ├── recommendation_engine.py
│   ├── requirements.txt
│   ├── .env.example
│   └── uploads/
│       └── .gitkeep
│
└── frontend/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    │
    ├── css/
    │   └── style.css
    │
    └── js/
        ├── config.js
        └── script.js
```

---

# 🔄 Application Workflow

```text
Register
   ↓
Login
   ↓
JWT Token Generated
   ↓
Upload CSV / Excel
   ↓
Dataset Analysis
   ↓
Automatic Column Detection
   ↓
Business Metrics Calculation
   ↓
Decision Engine
   ↓
Score Generation
   ↓
EXPAND / MAINTAIN / REDUCE
   ↓
Recommendations
   ↓
Dashboard
```

---

# 🔌 API Endpoints

## Home

```http
GET /
```

Returns backend status.

---

## Health Check

```http
GET /health
```

Checks whether the backend is running.

---

## Register

```http
POST /register
```

Creates a new user account.

---

## Login

```http
POST /login
```

Authenticates the user and returns a JWT token.

---

## Current User

```http
GET /me
```

Returns authenticated user information.

---

## Upload Dataset

```http
POST /upload
```

Protected endpoint requiring a valid JWT token.

Accepts CSV/XLS/XLSX files and returns:

```text
Dataset Summary
+
Recommendations
+
Decision
```

---

# 📋 Dataset Requirements

The system is designed to work with different sales datasets.

### Recommended columns

```text
Order_Amount
Product
Category
Region
Order_Date
```

Only a usable **numeric column** is required for basic analysis.

For example:

```csv
Order_Amount,Product,Category,Region,Order_Date
1200,Laptop,Electronics,Chennai,2026-01-10
850,Phone,Electronics,Bangalore,2026-01-12
2400,Monitor,Electronics,Chennai,2026-02-05
```

The analyzer can automatically recognize common alternative names such as:

```text
Amount
Sales
Revenue
Total
Price
Transaction_Amount
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-decision-maker.git
```

```bash
cd ai-decision-maker
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Set your JWT secret:

```env
JWT_SECRET_KEY=your_secure_secret_key
```

**Do not commit `.env` to GitHub.**

---

# ▶️ Run the Backend

From the `backend` directory:

```bash
python app.py
```

The backend will run at:

```text
http://127.0.0.1:5000
```

---

# 🌐 Run the Frontend

From the `frontend` directory:

```bash
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/login.html
```

Make sure `frontend/js/config.js` contains the correct backend URL.

---

# 🔐 Security

The application includes:

* Password hashing with Bcrypt
* JWT authentication
* Protected upload endpoint
* Environment variables for secrets
* CORS support
* Temporary upload cleanup

Uploaded datasets are removed from the server after processing.

---

# 🚀 Future Enhancements

Potential improvements include:

* Machine-learning-based decision prediction
* LLM-powered business explanations
* Advanced sales forecasting
* Time-series analysis
* Interactive charts
* PDF report generation
* Excel report generation
* PostgreSQL/MySQL support
* Cloud deployment
* Role-based access control
* Business KPI monitoring
* Automated email reports
* Scheduled data analysis
* Historical decision tracking

---

# 🎓 Learning Outcomes

This project demonstrates practical knowledge of:

* Python
* Flask
* REST APIs
* JWT Authentication
* Bcrypt
* SQLAlchemy
* SQLite
* Pandas
* Data Analysis
* CSV/Excel Processing
* Automatic Column Detection
* Rule-Based AI
* Business Intelligence
* Frontend-Backend Integration
* JSON APIs

---

# 🤖 Is This Really AI?

The decision engine in this project is **rule-based**, not an LLM or machine-learning model.

It uses predefined business rules to calculate a score and generate a decision.

This makes the system:

* Explainable
* Deterministic
* Easy to modify
* Independent of external AI APIs
* Usable without internet access or API keys

The architecture can later be extended with machine learning or an LLM.

---

# 💼 Use Cases

The project can be used as a decision-support tool for:

* Small businesses
* Retail businesses
* Sales teams
* Business analysts
* Data analysts
* Students
* Entrepreneurs

---

# 📜 License

This project is licensed under the MIT License.

---

## ⭐ Project Highlights

```text
✔ Full-stack application
✔ Flask REST API
✔ JWT Authentication
✔ Bcrypt Password Security
✔ CSV / Excel Processing
✔ Automatic Column Detection
✔ Sales Analytics
✔ Rule-Based Decision Engine
✔ Explainable Recommendations
✔ No External AI API Required
✔ Works Locally
```

---

**Built as a practical AI/Data Analytics project for automated business decision support.**
