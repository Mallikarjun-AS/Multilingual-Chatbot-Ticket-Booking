import re
import random

# Enhanced chatbot with conversational flow and button interactions
class MuseumChatbot:
    def __init__(self):
        self.user_state = {}  # Track user conversation state
        self.conversation_flow = {
            'greeting': True,
            'logged_in': False,
            'wants_to_book': False,
            'booking_in_progress': False
        }
    
    def get_response(self, user_message, user_id=None):
        user_message = user_message.lower().strip()
        
        # Handle button clicks (these would come from your frontend)
        if user_message.startswith('btn_'):
            return self.handle_button_click(user_message, user_id)
        
        # Pattern matching with conversational flow
        for pattern, handler in self.patterns.items():
            if re.search(pattern, user_message):
                return handler(user_message, user_id)
        
        # Default response with helpful suggestions
        return self.default_response()
    
    def handle_button_click(self, button_id, user_id):
        """Handle button clicks from the chat interface"""
        responses = {
            'btn_login': {
                'text': "Great! Please click the login button below to access your account.",
                'buttons': [],
                'action': 'redirect_login'
            },
            'btn_register': {
                'text': "Welcome to MuseumHub! Please click the register button below to create your account.",
                'buttons': [],
                'action': 'redirect_register'
            },
            'btn_book_tickets': {
                'text': "Excellent! Let me guide you to our ticket booking page where you can select your preferred date and tickets.",
                'buttons': [],
                'action': 'redirect_booking'
            },
            'btn_view_tickets': {
                'text': "Here are your booked tickets. You can view, download, or print them.",
                'buttons': [],
                'action': 'redirect_my_tickets'
            },
            'btn_cancel_ticket': {
                'text': "I can help you cancel your ticket. Please note that cancellation is allowed within 48 hours of booking.",
                'buttons': [
                    {'id': 'btn_view_tickets', 'text': 'View My Tickets'},
                    {'id': 'btn_main_menu', 'text': 'Main Menu'}
                ]
            },
            'btn_pricing_info': {
                'text': "Here's our pricing information:\n• Adult (18+): ₹150\n• Child (5-17): ₹80\n• Senior (60+): ₹100\n• Student (with ID): ₹60\n• Infant (below 5): Free",
                'buttons': [
                    {'id': 'btn_book_tickets', 'text': 'Book Tickets'},
                    {'id': 'btn_main_menu', 'text': 'Main Menu'}
                ]
            },
            'btn_museum_info': {
                'text': "Museum Information:\n• Hours: 9:00 AM - 6:00 PM (Daily)\n• Location: Culture Street, Art District\n• Contact: +91 98765 43210\n• Facilities: Audio Guide, VR Experience, Photography allowed",
                'buttons': [
                    {'id': 'btn_book_tickets', 'text': 'Book Tickets'},
                    {'id': 'btn_main_menu', 'text': 'Main Menu'}
                ]
            },
            'btn_main_menu': {
                'text': "What would you like to do?",
                'buttons': [
                    {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                    {'id': 'btn_view_tickets', 'text': '📋 My Tickets'},
                    {'id': 'btn_pricing_info', 'text': '💰 Pricing'},
                    {'id': 'btn_museum_info', 'text': '🏛️ Museum Info'}
                ]
            }
        }
        
        return responses.get(button_id, self.default_response())
    
    @property
    def patterns(self):
        return {
            # Greeting patterns
            r'\b(hello|hi|hey|good morning|good evening|start)\b': self.handle_greeting,
            
            # Help and support
            r'\b(help|support|assist|what can you do)\b': self.handle_help,
            
            # Booking related
            r'(book.*ticket|reserve.*ticket|buy.*ticket|want.*book|booking)': self.handle_booking_inquiry,
            
            # Login/Register related
            r'(login|log in|sign in|already registered|have account)': self.handle_login_inquiry,
            r'(register|sign up|create account|new user|new account)': self.handle_register_inquiry,
            
            # Ticket management
            r'(view.*ticket|my.*ticket|see.*ticket|check.*booking)': self.handle_view_tickets,
            r'(cancel.*ticket|refund|delete.*ticket)': self.handle_cancel_inquiry,
            
            # Information requests
            r'(price|cost|pricing|fee|rates|charges)': self.handle_pricing,
            r'(timing|time|hours|open|closing|schedule)': self.handle_timings,
            r'(location|address|where|contact|phone)': self.handle_contact,
            r'(services|facilities|amenities|features)': self.handle_services,
            
            # Policies and rules
            r'(policy|policies|rules|guidelines|terms)': self.handle_policies,
            
            # Goodbye
            r'\b(bye|goodbye|see you|thanks|thank you|exit)\b': self.handle_goodbye,
        }
    
    def handle_greeting(self, message, user_id):
        greetings = [
            "Hello! Welcome to MuseumHub 🏛️",
            "Hi there! Welcome to our museum booking assistant!",
            "Hey! Great to see you at MuseumHub!"
        ]
        
        greeting = random.choice(greetings)
        
        # Check if user is logged in (this would come from your session)
        is_logged_in = self.check_user_login_status(user_id)
        
        if is_logged_in:
            return {
                'text': f"{greeting}\n\nWelcome back! What would you like to do today?",
                'buttons': [
                    {'id': 'btn_book_tickets', 'text': '🎫 Book New Tickets'},
                    {'id': 'btn_view_tickets', 'text': '📋 My Tickets'},
                    {'id': 'btn_museum_info', 'text': '🏛️ Museum Info'},
                    {'id': 'btn_pricing_info', 'text': '💰 Pricing'}
                ]
            }
        else:
            return {
                'text': f"{greeting}\n\nTo get started, please choose an option:",
                'buttons': [
                    {'id': 'btn_login', 'text': '🔐 Login'},
                    {'id': 'btn_register', 'text': '✨ Register'},
                    {'id': 'btn_museum_info', 'text': '🏛️ Museum Info'},
                    {'id': 'btn_pricing_info', 'text': '💰 View Pricing'}
                ]
            }
    
    def handle_help(self, message, user_id):
        return {
            'text': "I'm here to help you with your museum visit! I can assist you with:\n\n• Ticket booking and management\n• Pricing information\n• Museum details and timings\n• Policies and guidelines\n\nWhat would you like to know more about?",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_pricing_info', 'text': '💰 Pricing'},
                {'id': 'btn_museum_info', 'text': '🏛️ Museum Info'},
                {'id': 'btn_view_tickets', 'text': '📋 My Tickets'}
            ]
        }
    
    def handle_booking_inquiry(self, message, user_id):
        is_logged_in = self.check_user_login_status(user_id)
        
        if is_logged_in:
            return {
                'text': "Perfect! I'd love to help you book tickets. Our booking system allows you to:\n\n• Choose your visit date\n• Select ticket types and quantities\n• Add optional services (Audio guide, VR experience)\n• Make secure payment\n\nReady to start booking?",
                'buttons': [
                    {'id': 'btn_book_tickets', 'text': '🎫 Start Booking'},
                    {'id': 'btn_pricing_info', 'text': '💰 View Pricing First'}
                ]
            }
        else:
            return {
                'text': "I'd be happy to help you book tickets! However, you'll need to login or create an account first to proceed with booking.\n\nWould you like to:",
                'buttons': [
                    {'id': 'btn_login', 'text': '🔐 Login to Existing Account'},
                    {'id': 'btn_register', 'text': '✨ Create New Account'},
                    {'id': 'btn_pricing_info', 'text': '💰 View Pricing First'}
                ]
            }
    
    def handle_login_inquiry(self, message, user_id):
        return {
            'text': "Great! If you already have an account, please click below to login:",
            'buttons': [
                {'id': 'btn_login', 'text': '🔐 Login Now'},
                {'id': 'btn_register', 'text': '✨ Create Account Instead'}
            ]
        }
    
    def handle_register_inquiry(self, message, user_id):
        return {
            'text': "Welcome to MuseumHub! Creating an account is quick and easy. You'll be able to:\n\n• Book tickets online\n• Manage your bookings\n• View booking history\n• Get exclusive offers\n\nReady to join us?",
            'buttons': [
                {'id': 'btn_register', 'text': '✨ Create Account'},
                {'id': 'btn_login', 'text': '🔐 Login to Existing Account'}
            ]
        }
    
    def handle_view_tickets(self, message, user_id):
        is_logged_in = self.check_user_login_status(user_id)
        
        if is_logged_in:
            return {
                'text': "Let me show you your tickets. You can view, download, print, or manage your bookings.",
                'buttons': [
                    {'id': 'btn_view_tickets', 'text': '📋 View My Tickets'},
                    {'id': 'btn_book_tickets', 'text': '🎫 Book More Tickets'}
                ]
            }
        else:
            return {
                'text': "To view your tickets, please login to your account first:",
                'buttons': [
                    {'id': 'btn_login', 'text': '🔐 Login'},
                    {'id': 'btn_register', 'text': '✨ Create Account'}
                ]
            }
    
    def handle_cancel_inquiry(self, message, user_id):
        return {
            'text': "I can help you with ticket cancellation. Please note our cancellation policy:\n\n• Cancellation allowed within 48 hours of booking\n• No refund if you miss your scheduled visit\n• Processing may take 3-5 business days\n\nWould you like to view your tickets to proceed with cancellation?",
            'buttons': [
                {'id': 'btn_view_tickets', 'text': '📋 View My Tickets'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_pricing(self, message, user_id):
        return {
            'text': "Here's our current pricing:\n\n🎫 **Ticket Prices:**\n• Adult (18+): ₹150\n• Child (5-17): ₹80\n• Senior Citizen (60+): ₹100\n• Student (with ID): ₹60\n• Infant (below 5): Free\n\n🎯 **Add-on Services:**\n• Audio Guide: ₹50/device\n• VR Experience: ₹100/person\n• Photography Pass: ₹200/group\n• Guided Tour: ₹300/group",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Now'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_timings(self, message, user_id):
        return {
            'text': "🕒 **Museum Hours:**\n• Daily: 9:00 AM - 6:00 PM\n• Last entry: 5:30 PM\n• Closed on national holidays\n\n💻 **Online Services:**\n• Ticket booking: Available 24/7\n• Customer support: 9:00 AM - 9:00 PM",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_contact(self, message, user_id):
        return {
            'text': "📍 **Museum Location & Contact:**\n\n🏛️ MuseumHub\n123 Culture Street, Art District\nCity, State - 123456\n\n📞 Phone: +91 98765 43210\n📧 Email: info@museumhub.com\n🌐 Website: www.museumhub.com",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_services(self, message, user_id):
        return {
            'text': "🏛️ **Our Services:**\n\n✅ **Available Services:**\n• Online ticket booking\n• Audio guides in multiple languages\n• VR experiences\n• Guided tours\n• Photography permissions\n• Wheelchair accessibility\n• Gift shop\n• Cafeteria\n\n🎯 **Digital Services:**\n• Mobile tickets\n• Online cancellation\n• Booking history\n• Email notifications",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_pricing_info', 'text': '💰 View Pricing'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_policies(self, message, user_id):
        return {
            'text': "📋 **Museum Policies:**\n\n🔸 **Booking Rules:**\n• Minimum age for booking: 18 years\n• One booking per person at a time\n• Valid ID required at entry\n\n🔸 **Cancellation Policy:**\n• Cancel within 48 hours of booking\n• No refund for missed visits\n• Processing time: 3-5 business days\n\n🔸 **Visit Guidelines:**\n• Arrive 15 minutes before your slot\n• No outside food or drinks\n• Photography rules apply\n• Follow museum etiquette",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_main_menu', 'text': '🏠 Main Menu'}
            ]
        }
    
    def handle_goodbye(self, message, user_id):
        farewell_messages = [
            "Thank you for visiting MuseumHub! Have a wonderful day! 🏛️",
            "Goodbye! We hope to see you at the museum soon! 👋",
            "Thanks for chatting with me! Enjoy your museum experience! ✨"
        ]
        
        return {
            'text': random.choice(farewell_messages),
            'buttons': [
                {'id': 'btn_main_menu', 'text': '🏠 Start Over'},
                {'id': 'btn_book_tickets', 'text': '🎫 Quick Book'}
            ]
        }
    
    def default_response(self):
        return {
            'text': "I'm not quite sure about that, but I'm here to help! I can assist you with:\n\n• Booking museum tickets\n• Viewing your tickets\n• Pricing information\n• Museum details and policies\n\nWhat would you like to know more about?",
            'buttons': [
                {'id': 'btn_book_tickets', 'text': '🎫 Book Tickets'},
                {'id': 'btn_view_tickets', 'text': '📋 My Tickets'},
                {'id': 'btn_museum_info', 'text': '🏛️ Museum Info'},
                {'id': 'btn_pricing_info', 'text': '💰 Pricing'}
            ]
        }
    
    def check_user_login_status(self, user_id):
        """
        This function should check if the user is logged in
        You'll need to implement this based on your session management
        For now, returning False as default
        """
        # In your Flask app, you can check session['user_id'] here
        # return 'user_id' in session
        return False  # Change this based on your session logic

# Initialize the chatbot
chatbot = MuseumChatbot()

def get_chatbot_response(user_message, user_id=None):
    """
    Main function to get chatbot response
    Returns a dictionary with 'text', 'buttons', and optional 'action'
    """
    return chatbot.get_response(user_message, user_id)