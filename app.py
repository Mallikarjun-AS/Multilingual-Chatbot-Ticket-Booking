from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_cors import CORS
from models import db  # Import the db from model.py
from chatbot import get_chatbot_response
import razorpay
import os
from datetime import datetime

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/chatbot_db'

# Razorpay Keys (use Test Mode keys from dashboard)
app.config['RAZORPAY_KEY_ID'] = "rzp_test_RIjWFnsQXZYCpe"
app.config['RAZORPAY_KEY_SECRET'] = "2TjrqlX1HCi0knyk1mIuDKTM"

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))

# Initialize the app with the db
db.init_app(app)

babel = Babel(app)
CORS(app)

def get_locale():
    return session.get('locale', 'en')

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)


@app.route('/set_locale/<locale>')
def set_locale(locale):
    session['locale'] = locale
    return redirect(request.referrer)

@app.route('/test_locale')
def test_locale():
    return f"Current locale: {get_locale()}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/view')
def view():
    return render_template('view.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        return "Thank you for your message!"  
    return render_template('contact.html')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        from models import User
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from models import User
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username  # Store username for ticket display
            return redirect(url_for('book_ticket'))
        else:
            return "Login failed"
    return render_template('login.html')

@app.route('/book_ticket', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        from models import Ticket
        age = int(request.form['age'])
        if age < 18:
            return "You must be 18 or older to book a ticket."
        ticket = Ticket(
            name=request.form['name'],
            age=age,
            email=request.form['email'],
            user_id=session['user_id']
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('payment', ticket_id=ticket.id))
    return render_template('book_ticket.html')

@app.route('/my_tickets')
def my_tickets():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from models import Ticket
    user_id = session['user_id']
    username = session.get('username', 'Guest')
    
    # Get all tickets for the logged-in user
    tickets = Ticket.query.filter_by(user_id=user_id).all()
    
    # Format tickets data for the template
    formatted_tickets = []
    for ticket in tickets:
        # Calculate amount based on age (same logic as in payment route)
        base_amount = 100
        if ticket.age < 12:
            amount = base_amount * 0.5
        elif ticket.age >= 60:
            amount = base_amount * 0.7
        else:
            amount = base_amount
        
        formatted_ticket = {
            'id': ticket.id,
            'booking_id': f'MUS24{ticket.id:04d}',  # Generate booking ID
            'name': ticket.name,
            'age': ticket.age,
            'email': ticket.email,
            'amount': amount,
            'visit_date': datetime.now().strftime("%d %B %Y"),  # You can modify this
            'status': 'active',  # You can add status field to your Ticket model
            'contact': session.get('phone', '+91 98765 43210'),  # Default or from session
            'addons': 'None'  # You can add addons field to your Ticket model
        }
        formatted_tickets.append(formatted_ticket)
    
    return render_template('my_tickets.html', tickets=formatted_tickets, username=username)

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from models import Ticket
    # Only allow deletion of user's own tickets
    ticket = Ticket.query.filter_by(id=ticket_id, user_id=session['user_id']).first()
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
    return redirect(url_for('my_tickets'))

# --------- Enhanced Razorpay Integration with Ticket Display ----------

@app.route('/create_payment_link', methods=['POST'])
def create_payment_link():
    data = request.json
    amount = int(data.get("amount", 0)) * 100  # Convert to paise
    name = data.get("name", "Guest")
    email = data.get("email", "")
    phone = data.get("phone", "")

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    payment_link = razorpay_client.payment_link.create({
        "amount": amount,
        "currency": "INR",
        "description": "Museum Ticket Booking",
        "customer": {
            "name": name,
            "email": email,
            "contact": phone
        },
        "notify": {"sms": True, "email": True},
        "callback_url": "http://localhost:5000/payment_success",
        "callback_method": "get"
    })

    return jsonify({"short_url": payment_link["short_url"]})


@app.route('/payment/<int:ticket_id>', methods=['GET', 'POST'])
def payment(ticket_id):
    from models import Ticket
    
    if request.method == 'GET':
        # Get ticket details from database
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Calculate amount based on ticket details (you can modify this logic)
        base_amount = 100  # Base ticket price
        if ticket.age < 12:
            amount = base_amount * 0.5  # 50% discount for children
        elif ticket.age >= 60:
            amount = base_amount * 0.7  # 30% discount for seniors
        else:
            amount = base_amount
        
        # Get current date for event date (you can modify this)
        event_date = datetime.now().strftime("%Y-%m-%d")
        
        return render_template('payment.html', 
                             ticket_id=ticket_id,
                             ticket=ticket,
                             amount=amount,
                             event_date=event_date,
                             customer_name=ticket.name,
                             customer_email=ticket.email,
                             razorpay_key=app.config['RAZORPAY_KEY_ID'])
    
    elif request.method == 'POST':
        # Handle Razorpay payment processing
        try:
            data = request.get_json()
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            amount = data.get('amount')
            
            # Create Razorpay order for verification
            order_data = {
                'amount': int(float(amount) * 100),  # Convert to paise
                'currency': 'INR',
                'payment_capture': '1'
            }
            
            # In a real application, you should verify the payment signature
            # For now, we'll assume payment is successful
            
            # Update ticket status in database
            from models import Ticket
            ticket = Ticket.query.get(ticket_id)
            if ticket:
                # You can add payment_id field to your Ticket model
                # ticket.payment_id = razorpay_payment_id
                # ticket.payment_status = 'paid'
                db.session.commit()
            
            return jsonify({
                'success': True,
                'payment_id': razorpay_payment_id,
                'message': 'Payment successful'
            })
            
        except Exception as e:
            print(f"Payment error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Payment processing failed. Please try again.'
            }), 400


@app.route('/create_order', methods=['POST'])
def create_order():
    """Create Razorpay order for payment"""
    try:
        data = request.get_json()
        amount = int(float(data.get('amount', 0)) * 100)  # Convert to paise
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Create order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency']
        })
        
    except Exception as e:
        print(f"Order creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create order'
        }), 400


@app.route('/payment_success')
def payment_success():
    return "<h2>✅ Payment successful — Your booking is confirmed!</h2>"

# -----------------------------------------

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message')
        bot_response = get_chatbot_response(user_message)
        return jsonify({"response": bot_response})
    else:
        return render_template('chatbot.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard route for navigation after ticket booking"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('my_tickets'))

    
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)