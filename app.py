from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from io import BytesIO
import datetime
from database import init_db, generate_unique_id, get_db_connection
from telegram_notify import telegram_notifier
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Simple user class for admin authentication
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':  # Simple admin user
        return User('1', Config.ADMIN_USERNAME)
    return None

# Initialize database
with app.app_context():
    init_db()

# User routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/property-tax', methods=['GET', 'POST'])
def property_tax():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Generate unique ID
        unique_id = generate_unique_id('PT')
        
        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO property_tax (unique_id, name, phone, address)
                VALUES (?, ?, ?, ?)
            ''', (unique_id, name, phone, address))
            conn.commit()
        
        # Send Telegram notification
        message = f"👤 *Name:* {name}\n"
        message += f"📞 *Phone:* {phone}\n"
        message += f"🏠 *Address:* {address}"
        telegram_notifier.send_notification(message, "Property Tax", unique_id)
        
        return render_template('property_tax.html', submitted=True, unique_id=unique_id)
    
    return render_template('property_tax.html', submitted=False)

@app.route('/echallan', methods=['GET', 'POST'])
def echallan():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        vehicle_number = request.form.get('vehicle_number')
        
        # Generate unique ID
        unique_id = generate_unique_id('EC')
        
        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO echallan (unique_id, name, phone, vehicle_number)
                VALUES (?, ?, ?, ?)
            ''', (unique_id, name, phone, vehicle_number))
            conn.commit()
        
        # Send Telegram notification
        message = f"👤 *Name:* {name}\n"
        message += f"📞 *Phone:* {phone}\n"
        message += f"🚗 *Vehicle Number:* {vehicle_number}"
        telegram_notifier.send_notification(message, "EChallan", unique_id)
        
        return render_template('echallan.html', submitted=True, unique_id=unique_id)
    
    return render_template('echallan.html', submitted=False)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            user = User('1', username)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/property-tax')
@login_required
def admin_property_tax():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build query based on filters
        query = "SELECT * FROM property_tax WHERE 1=1"
        params = []
        
        if status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        if date_filter:
            query += " AND DATE(created_at) = ?"
            params.append(date_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        records = cursor.fetchall()
    
    return render_template('property_tax_admin.html', 
                         records=records, 
                         status=status,
                         date_filter=date_filter)

@app.route('/admin/echallan')
@login_required
def admin_echallan():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build query based on filters
        query = "SELECT * FROM echallan WHERE 1=1"
        params = []
        
        if status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        if date_filter:
            query += " AND DATE(created_at) = ?"
            params.append(date_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        records = cursor.fetchall()
    
    return render_template('echallan_admin.html', 
                         records=records, 
                         status=status,
                         date_filter=date_filter)

@app.route('/admin/update-status', methods=['POST'])
@login_required
def update_status():
    data = request.json
    record_type = data.get('type')
    record_id = data.get('id')
    status = data.get('status')
    amount_paid = data.get('amount_paid', 0)
    
    table = 'property_tax' if record_type == 'property_tax' else 'echallan'
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute(f"SELECT status FROM {table} WHERE id = ?", (record_id,))
        old_status = cursor.fetchone()['status']
        
        # Update status
        if status == 'completed':
            cursor.execute(f'''
                UPDATE {table} 
                SET status = ?, amount_paid = ?, completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, amount_paid, record_id))
        else:
            cursor.execute(f'''
                UPDATE {table} 
                SET status = ?, amount_paid = ? 
                WHERE id = ?
            ''', (status, amount_paid, record_id))
        
        conn.commit()
        
        # Get unique_id for notification
        cursor.execute(f"SELECT unique_id FROM {table} WHERE id = ?", (record_id,))
        unique_id = cursor.fetchone()['unique_id']
    
    # Send status update notification
    telegram_notifier.send_status_update(
        "Property Tax" if record_type == 'property_tax' else "EChallan",
        unique_id,
        old_status,
        status,
        amount_paid
    )
    
    return jsonify({'success': True})

@app.route('/admin/stats')
@login_required
def admin_stats():
    record_type = request.args.get('type', 'property_tax')
    period = request.args.get('period', 'today')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        table = 'property_tax' if record_type == 'property_tax' else 'echallan'
        
        # Build date filter
        date_filter = ""
        if period == 'today':
            date_filter = "DATE(created_at) = DATE('now')"
        elif period == 'this_month':
            date_filter = "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"
        elif period == 'last_month':
            date_filter = "strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', '-1 month')"
        
        # Get statistics
        cursor.execute(f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(amount_paid) as total_amount
            FROM {table}
            WHERE {date_filter if date_filter else '1=1'}
        ''')
        
        stats = cursor.fetchone()
    
    return jsonify({
        'total': stats['total'] or 0,
        'pending': stats['pending'] or 0,
        'completed': stats['completed'] or 0,
        'total_amount': stats['total_amount'] or 0
    })

@app.route('/admin/download-excel')
@login_required
def download_excel():
    record_type = request.args.get('type')
    status = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')
    
    table = 'property_tax' if record_type == 'property_tax' else 'echallan'
    
    with get_db_connection() as conn:
        # Build query based on filters
        query = f"SELECT * FROM {table} WHERE 1=1"
        params = []
        
        if status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        if date_filter:
            query += " AND DATE(created_at) = ?"
            params.append(date_filter)
        
        query += " ORDER BY created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Records', index=False)
    
    output.seek(0)
    
    filename = f"{record_type}_{status}_{date_filter if date_filter else 'all'}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)