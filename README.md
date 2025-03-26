# Expense Tracker Web Application

A Flask-based web application for tracking personal expenses. This application allows users to manage their expenses, create categories, set budgets, and generate reports.

## Features

- User authentication (login/register)
- Add, view, and manage expense transactions
- Create and manage expense categories
- Set and track budget limits
- Generate various expense reports
- Search transactions by category, date, or time
- Responsive web interface

## Prerequisites

- Python 3.8 or higher
- SQL Server (Azure SQL Database)
- ODBC Driver 18 for SQL Server

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd expense-tracker-web
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and update the following variables:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=mssql+pyodbc://username:password@server:port/database?driver=ODBC+Driver+18+for+SQL+Server
FLASK_ENV=development
FLASK_APP=app.py
```

## Database Setup

1. Create a new database in SQL Server
2. Run the following SQL scripts to create the required tables:
```sql
CREATE TABLE users (
    userID VARCHAR(20) PRIMARY KEY,
    userPwd VARCHAR(20) NOT NULL,
    fName VARCHAR(15) NOT NULL,
    lName VARCHAR(15) NOT NULL,
    userBudget FLOAT NOT NULL
);

CREATE TABLE categories (
    catID VARCHAR(20) PRIMARY KEY,
    catName VARCHAR(30) NOT NULL
);

CREATE TABLE transactions (
    tranID VARCHAR(20) PRIMARY KEY,
    tranDate DATE NOT NULL,
    tranTime VARCHAR(5) NOT NULL,
    catID VARCHAR(20) NOT NULL,
    tranDescription VARCHAR(50) NOT NULL,
    tranAmount FLOAT NOT NULL,
    FOREIGN KEY (catID) REFERENCES categories(catID)
);

CREATE TABLE userTransactions (
    userID VARCHAR(20),
    tranID VARCHAR(20),
    PRIMARY KEY (userID, tranID),
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (tranID) REFERENCES transactions(tranID)
);
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
flask run
```

3. Open your web browser and navigate to `http://localhost:5000`

## Project Structure

```
expense-tracker-web/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── main.js      # JavaScript functions
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── login.html       # Login page
    ├── register.html    # Registration page
    └── dashboard.html   # Main dashboard
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 