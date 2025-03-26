from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
import csv
from io import StringIO
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = "mx3594.syd1.mymailhosting.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

# Load email credentials from environment variables
email_user = os.getenv('EMAIL_USER')
email_password = os.getenv('EMAIL_PASSWORD')

if not email_user or not email_password:
    app.logger.error("Email credentials not found in environment variables")
    raise ValueError("Email credentials must be set in environment variables")

app.config['MAIL_USERNAME'] = email_user
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_DEFAULT_SENDER'] = email_user
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True  # Enable debug mode

# Debug logging for email configuration (without exposing sensitive data)
print("Email Configuration:")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'None'}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_reset_token(user_id):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return user_id
    except:
        return None

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.String(20), primary_key=True)
    userPwd = db.Column(db.String(256), nullable=False)  # Increased length for hash
    fName = db.Column(db.String(15), nullable=False)
    lName = db.Column(db.String(15), nullable=False)
    userBudget = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Add email field

    def get_id(self):
        return str(self.userID)

    def set_password(self, password):
        self.userPwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.userPwd, password)

class Category(db.Model):
    __tablename__ = 'categories'
    catID = db.Column(db.String(20), primary_key=True)
    catName = db.Column(db.String(30), nullable=False)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    tranID = db.Column(db.String(20), primary_key=True)
    tranDate = db.Column(db.Date, nullable=False)
    tranTime = db.Column(db.String(5), nullable=False)
    catID = db.Column(db.String(20), db.ForeignKey('categories.catID'), nullable=False)
    tranDescription = db.Column(db.String(50), nullable=False)
    tranAmount = db.Column(db.Float, nullable=False)

class UserTransaction(db.Model):
    __tablename__ = 'userTransactions'
    userID = db.Column(db.String(20), db.ForeignKey('users.userID'), primary_key=True)
    tranID = db.Column(db.String(20), db.ForeignKey('transactions.tranID'), primary_key=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        user = User.query.get(user_id)
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid user ID or password')
    return render_template('login.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = get_reset_token(user.userID)
            reset_url = url_for('reset_token', token=token, _external=True)
            
            # Ensure we have valid email configuration
            if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
                app.logger.error("Email configuration is missing")
                flash('Email service is not properly configured. Please contact support.', 'error')
                return redirect(url_for('login'))
            
            msg = Message('Password Reset Request',
                        sender=(app.config['MAIL_USERNAME'], app.config['MAIL_USERNAME']),  # Use email as both name and address
                        recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
'''
            try:
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.', 'info')
                return redirect(url_for('login'))
            except Exception as e:
                app.logger.error(f"Failed to send email: {str(e)}")
                flash('Error sending email. Please try again later.', 'error')
        else:
            flash('No account found with that email address.', 'error')
    
    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user_id = verify_reset_token(token)
    if user_id is None:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_token.html')
        
        user = User.query.get(user_id)
        user.set_password(password)
        
        try:
            db.session.commit()
            flash('Your password has been updated! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating password. Please try again.', 'error')
    
    return render_template('reset_token.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        budget = float(request.form.get('budget'))

        # Check if user already exists
        if User.query.get(user_id):
            flash('User ID already exists')
            return redirect(url_for('register'))
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email address already registered')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(
            userID=user_id,
            fName=first_name,
            lName=last_name,
            email=email,
            userBudget=budget
        )
        new_user.set_password(password)  # Hash the password before saving
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get the 5 most recent transactions
    recent_transactions = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID
    ).order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).limit(5).all()
    
    return render_template('dashboard.html', recent_transactions=recent_transactions)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Transaction Management Routes
@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        # Get form data
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        time = request.form.get('time')
        category_id = request.form.get('category')
        description = request.form.get('description')
        amount = float(request.form.get('amount'))

        # Create new transaction
        transaction = Transaction(
            tranID=str(uuid.uuid4())[:8],
            tranDate=date,
            tranTime=time,
            catID=category_id,
            tranDescription=description,
            tranAmount=amount
        )
        db.session.add(transaction)
        
        # Create user-transaction association
        user_transaction = UserTransaction(
            userID=current_user.userID,
            tranID=transaction.tranID
        )
        db.session.add(user_transaction)
        
        try:
            db.session.commit()
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('view_transactions'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding transaction. Please try again.', 'error')
    
    # Get all categories for the form
    categories = Category.query.all()
    return render_template('add_transaction.html', categories=categories)

@app.route('/transactions')
@login_required
def view_transactions():
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Build query
    query = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID
    )

    # Apply filters
    if category:
        query = query.filter(Transaction.catID == category)
    if date_from:
        query = query.filter(Transaction.tranDate >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Transaction.tranDate <= datetime.strptime(date_to, '%Y-%m-%d').date())

    # Order by date and time
    query = query.order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc())

    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items

    # Get all categories for the filter
    categories = Category.query.all()

    return render_template('view_transactions.html',
                         transactions=transactions,
                         categories=categories,
                         selected_category=category,
                         date_from=date_from,
                         date_to=date_to,
                         current_page=page,
                         total_pages=pagination.pages)

@app.route('/transactions/<tran_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(tran_id):
    # Get transaction and verify ownership
    transaction = Transaction.query.join(UserTransaction).filter(
        Transaction.tranID == tran_id,
        UserTransaction.userID == current_user.userID
    ).first_or_404()

    if request.method == 'POST':
        # Update transaction
        transaction.tranDate = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        transaction.tranTime = request.form.get('time')
        transaction.catID = request.form.get('category')
        transaction.tranDescription = request.form.get('description')
        transaction.tranAmount = float(request.form.get('amount'))

        try:
            db.session.commit()
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('view_transactions'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating transaction. Please try again.', 'error')

    # Get all categories for the form
    categories = Category.query.all()
    return render_template('edit_transaction.html', transaction=transaction, categories=categories)

@app.route('/transactions/<tran_id>/delete', methods=['POST'])
@login_required
def delete_transaction(tran_id):
    # Get transaction and verify ownership
    transaction = Transaction.query.join(UserTransaction).filter(
        Transaction.tranID == tran_id,
        UserTransaction.userID == current_user.userID
    ).first_or_404()

    try:
        # Delete user-transaction association first
        UserTransaction.query.filter_by(
            userID=current_user.userID,
            tranID=tran_id
        ).delete()
        
        # Delete transaction
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error deleting transaction'}), 500

# Category Management Routes
@app.route('/categories')
@login_required
def view_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    category_id = request.form.get('categoryId')
    category_name = request.form.get('categoryName')

    # Validate category ID format
    if not category_id.isdigit() or len(category_id) != 4 or int(category_id) < 1000 or int(category_id) > 9999:
        flash('Category ID must be a 4-digit number between 1000 and 9999.', 'error')
        return redirect(url_for('view_categories'))

    # Check if category ID already exists
    if Category.query.get(category_id):
        flash('Category ID already exists.', 'error')
        return redirect(url_for('view_categories'))

    # Create new category
    new_category = Category(
        catID=category_id,
        catName=category_name
    )

    try:
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding category. Please try again.', 'error')

    return redirect(url_for('view_categories'))

@app.route('/categories/<cat_id>/edit', methods=['POST'])
@login_required
def edit_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    category_name = request.form.get('categoryName')

    try:
        category.catName = category_name
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating category'}), 500

@app.route('/categories/<cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)

    # Check if category is being used in transactions
    if Transaction.query.filter_by(catID=cat_id).first():
        return jsonify({
            'success': False, 
            'message': 'Cannot delete category that is being used in transactions'
        }), 400

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error deleting category'}), 500

# Report Routes
@app.route('/reports')
@login_required
def reports():
    # Get filter parameters
    category_id = request.args.get('category')
    
    # Get current transactions and total amount
    query = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID
    )
    
    # Apply category filter if specified
    if category_id:
        query = query.filter(Transaction.catID == category_id)
    
    current_transactions = query.order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).all()
    
    total_amount = sum(t.tranAmount for t in current_transactions)
    total_transactions = len(current_transactions)
    avg_transaction = total_amount / total_transactions if total_transactions > 0 else 0
    
    # Prepare data for charts
    category_data = {}
    monthly_data = {}
    
    for t in current_transactions:
        # Category data
        if t.category.catName not in category_data:
            category_data[t.category.catName] = 0
        category_data[t.category.catName] += t.tranAmount
        
        # Monthly data
        month_key = t.tranDate.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = 0
        monthly_data[month_key] += t.tranAmount
    
    # Sort monthly data
    monthly_data = dict(sorted(monthly_data.items()))
    
    # Get all categories for the category report form
    categories = Category.query.all()
    
    # Prepare category report data if category is selected
    category_report = None
    category_total = 0
    category_avg = 0
    category_count = 0
    category_trend_labels = []
    category_trend_data = []
    
    if category_id:
        category_report = current_transactions
        category_total = total_amount
        category_avg = avg_transaction
        category_count = total_transactions
        
        # Prepare category trend data
        for t in category_report:
            date_key = t.tranDate.strftime('%Y-%m-%d')
            if date_key not in category_trend_data:
                category_trend_data[date_key] = 0
            category_trend_data[date_key] += t.tranAmount
        
        category_trend_data = dict(sorted(category_trend_data.items()))
        category_trend_labels = list(category_trend_data.keys())
        category_trend_data = list(category_trend_data.values())
    
    # Initialize date report variables with empty values
    date_report = None
    date_total = 0
    date_count = 0
    date_daily_avg = 0
    date_range_labels = []
    date_range_data = []
    
    return render_template('reports.html',
                         current_transactions=current_transactions,
                         total_amount=total_amount,
                         total_transactions=total_transactions,
                         avg_transaction=avg_transaction,
                         category_labels=list(category_data.keys()),
                         category_data=list(category_data.values()),
                         monthly_labels=list(monthly_data.keys()),
                         monthly_data=list(monthly_data.values()),
                         categories=categories,
                         category_report=category_report,
                         category_total=category_total,
                         category_avg=category_avg,
                         category_count=category_count,
                         category_trend_labels=category_trend_labels,
                         category_trend_data=category_trend_data,
                         date_report=date_report,
                         date_total=date_total,
                         date_count=date_count,
                         date_daily_avg=date_daily_avg,
                         date_range_labels=date_range_labels,
                         date_range_data=date_range_data)

@app.route('/reports/category')
@login_required
def category_report():
    category_id = request.args.get('category')
    
    if not category_id:
        flash('Please select a category.', 'error')
        return redirect(url_for('reports'))
    
    # Get transactions for the selected category
    category_report = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID,
        Transaction.catID == category_id
    ).order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).all()
    
    category_total = sum(t.tranAmount for t in category_report)
    category_count = len(category_report)
    category_avg = category_total / category_count if category_count > 0 else 0
    
    # Prepare data for category trend chart
    category_trend_data = {}
    for t in category_report:
        date_key = t.tranDate.strftime('%Y-%m-%d')
        if date_key not in category_trend_data:
            category_trend_data[date_key] = 0
        category_trend_data[date_key] += t.tranAmount
    
    # Sort trend data
    category_trend_data = dict(sorted(category_trend_data.items()))
    
    # Get all categories for the form
    categories = Category.query.all()
    
    return render_template('reports.html',
                         category_report=category_report,
                         category_total=category_total,
                         category_count=category_count,
                         category_avg=category_avg,
                         category_trend_labels=list(category_trend_data.keys()),
                         category_trend_data=list(category_trend_data.values()),
                         categories=categories)

@app.route('/reports/date')
@login_required
def date_report():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if not date_from or not date_to:
        flash('Please select both start and end dates.', 'error')
        return redirect(url_for('reports'))
    
    # Convert string dates to datetime objects
    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Get transactions within the date range
    date_report = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID,
        Transaction.tranDate.between(date_from, date_to)
    ).order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).all()
    
    date_total = sum(t.tranAmount for t in date_report)
    date_count = len(date_report)
    days_diff = (date_to - date_from).days + 1
    date_daily_avg = date_total / days_diff if days_diff > 0 else 0
    
    # Prepare data for daily expenses chart
    date_range_data = {}
    for t in date_report:
        date_key = t.tranDate.strftime('%Y-%m-%d')
        if date_key not in date_range_data:
            date_range_data[date_key] = 0
        date_range_data[date_key] += t.tranAmount
    
    # Sort date range data
    date_range_data = dict(sorted(date_range_data.items()))
    
    # Get all categories for the form
    categories = Category.query.all()
    
    return render_template('reports.html',
                         date_report=date_report,
                         date_total=date_total,
                         date_count=date_count,
                         date_daily_avg=date_daily_avg,
                         date_range_labels=list(date_range_data.keys()),
                         date_range_data=list(date_range_data.values()),
                         categories=categories)

@app.route('/reports/time')
@login_required
def time_report():
    time_from = request.args.get('time_from')
    time_to = request.args.get('time_to')
    
    if not time_from or not time_to:
        flash('Please select both start and end times.', 'error')
        return redirect(url_for('reports'))
    
    # Get transactions within the time range
    time_report = Transaction.query.join(UserTransaction).filter(
        UserTransaction.userID == current_user.userID,
        Transaction.tranTime.between(time_from, time_to)
    ).order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).all()
    
    time_total = sum(t.tranAmount for t in time_report)
    time_count = len(time_report)
    time_avg = time_total / time_count if time_count > 0 else 0
    
    # Prepare data for hourly distribution chart
    time_range_data = {}
    for t in time_report:
        hour_key = t.tranTime.split(':')[0] + ':00'
        if hour_key not in time_range_data:
            time_range_data[hour_key] = 0
        time_range_data[hour_key] += t.tranAmount
    
    # Sort time range data
    time_range_data = dict(sorted(time_range_data.items()))
    
    # Get all categories for the form
    categories = Category.query.all()
    
    return render_template('reports.html',
                         time_report=time_report,
                         time_total=time_total,
                         time_count=time_count,
                         time_avg=time_avg,
                         time_range_labels=list(time_range_data.keys()),
                         time_range_data=list(time_range_data.values()),
                         categories=categories)

@app.route('/reports/export/<report_type>/<format>')
@login_required
def export_report(report_type, format):
    if report_type == 'current':
        transactions = Transaction.query.join(UserTransaction).filter(
            UserTransaction.userID == current_user.userID
        ).order_by(Transaction.tranDate.desc(), Transaction.tranTime.desc()).all()
    else:
        flash('Invalid report type.', 'error')
        return redirect(url_for('reports'))
    
    if format == 'csv':
        # Create CSV data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Time', 'Category', 'Description', 'Amount'])
        
        # Write data
        for t in transactions:
            writer.writerow([
                t.tranDate.strftime('%d-%m-%Y'),
                t.tranTime,
                t.category.catName,
                t.tranDescription,
                f"{t.tranAmount:.2f}"
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=expense_report_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    
    elif format == 'excel':
        import pandas as pd
        from io import BytesIO
        
        # Create DataFrame
        data = []
        for t in transactions:
            data.append({
                'Date': t.tranDate.strftime('%d-%m-%Y'),
                'Time': t.tranTime,
                'Category': t.category.catName,
                'Description': t.tranDescription,
                'Amount': t.tranAmount
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Expenses')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Expenses']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        output.seek(0)
        return Response(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment;filename=expense_report_{datetime.now().strftime("%Y%m%d")}.xlsx'}
        )
    
    elif format == 'pdf':
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from io import BytesIO
        
        # Create PDF
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        # Prepare data
        data = [['Date', 'Time', 'Category', 'Description', 'Amount']]
        for t in transactions:
            data.append([
                t.tranDate.strftime('%d-%m-%Y'),
                t.tranTime,
                t.category.catName,
                t.tranDescription,
                f"{t.tranAmount:.2f}"
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        output.seek(0)
        return Response(
            output,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename=expense_report_{datetime.now().strftime("%Y%m%d")}.pdf'}
        )
    
    else:
        flash('Invalid export format.', 'error')
        return redirect(url_for('reports'))

if __name__ == '__main__':
    app.run(debug=True) 