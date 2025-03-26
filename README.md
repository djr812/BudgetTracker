# Budget Tracker Web Application

A Flask-based web application for tracking personal finances, including both expenses and revenue. This application helps users manage their budget, track spending, and monitor income streams.

## Features

- User authentication (login/register)
- Expense tracking with categories
- Revenue tracking with categories
- Financial dashboard with charts
- Detailed reports and analytics
- Category management
- Password reset functionality
- Responsive design

## Tech Stack

- **Backend**: Python/Flask
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Charts**: Chart.js
- **Email**: Flask-Mail

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd BudgetTrackerWeb
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Database Schema

The application uses the following main tables:

- `users`: User account information
- `transactions`: Expense transactions
- `revenues`: Revenue entries
- `categories`: Expense categories
- `user_transactions`: Many-to-many relationship between users and transactions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 