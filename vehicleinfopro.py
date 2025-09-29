import os
import logging
from flask import Flask, request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import requests
import json

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8223529849:AAGZmFjRzTDPWi7fcFthjThIuldj1bNv_qs')
PORT = int(os.environ.get('PORT', 5000))

# Initialize bot
bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API endpoints
API1_URL = "https://revangevichelinfo.vercel.app/api/rc?number="
API2_URL = "https://caller.hackershub.shop/info.php?type=address&registration="

def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message with inline keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔍 Vehicle Search", callback_data='search_vehicle')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🚗 *Welcome to Vehicle Info Bot* 🚗

I can help you get detailed information about any vehicle using its registration number.

*Features:*
• 📄 RC Vehicle Information
• 🏠 Address Details  
• ⚡ Quick & Easy Search

Click the button below to start searching!
    """
    
    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle inline button clicks"""
    query = update.callback_query
    query.answer()
    
    if query.data == 'search_vehicle':
        query.edit_message_text(
            "🔍 *Vehicle Search*\n\nPlease enter the vehicle registration number:\n\n*Example:* `UP32AB1234`",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_vehicle'] = True
        
    elif query.data == 'help':
        help_text = """
*🤖 How to Use This Bot:*

1. 📱 Click *"Vehicle Search"* button
2. 🔢 Enter vehicle registration number  
3. 📊 Get detailed information from both APIs

*📝 Format Examples:*
• 🚙 UP32AB1234
• 🚗 DL1CAB1234  
• 🚘 HR26DK7890

*⚡ Features:*
• 📄 RC Information
• 🏠 Address Details
• ⚡ Fast Response
        """
        query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Start Search", callback_data='search_vehicle')]
            ])
        )

def get_vehicle_info(vehicle_number):
    """Fetch vehicle information from both APIs"""
    results = {}
    
    try:
        # API 1
        api1_response = requests.get(f"{API1_URL}{vehicle_number}", timeout=10)
        if api1_response.status_code == 200:
            results['api1'] = api1_response.json()
        else:
            results['api1'] = {"error": f"API1 returned status code: {api1_response.status_code}"}
    except Exception as e:
        results['api1'] = {"error": f"API1 Error: {str(e)}"}
    
    try:
        # API 2
        api2_response = requests.get(f"{API2_URL}{vehicle_number}", timeout=10)
        if api2_response.status_code == 200:
            results['api2'] = api2_response.json()
        else:
            results['api2'] = {"error": f"API2 returned status code: {api2_response.status_code}"}
    except Exception as e:
        results['api2'] = {"error": f"API2 Error: {str(e)}"}
    
    return results

def format_api1_result(api1_data):
    """Format API 1 result with emojis"""
    message = "📄 *RESULT 1 (RC Information):*\n\n"
    
    if 'error' in api1_data:
        message += f"❌ Error: {api1_data['error']}\n"
        return message
    
    try:
        data = api1_data
        message += f"👤 *Owner:* {data.get('owner_name', 'N/A')}\n"
        message += f"👨‍👦 *Father:* {data.get('father_name', 'N/A')}\n"
        message += f"🔢 *Owner Serial:* {data.get('owner_serial_no', 'N/A')}\n"
        message += f"🏭 *Manufacturer:* {data.get('model_name', 'N/A')}\n"
        message += f"🚗 *Model:* {data.get('maker_model', 'N/A')}\n"
        message += f"📋 *Vehicle Class:* {data.get('vehicle_class', 'N/A')}\n"
        message += f"⛽ *Fuel Type:* {data.get('fuel_type', 'N/A')}\n"
        message += f"🌱 *Fuel Norms:* {data.get('fuel_norms', 'N/A')}\n"
        message += f"📅 *Registration Date:* {data.get('registration_date', 'N/A')}\n"
        message += f"🏢 *Insurance Company:* {data.get('insurance_company', 'N/A')}\n"
        message += f"🛡️ *Insurance Upto:* {data.get('insurance_upto', 'N/A')}\n"
        message += f"✅ *Fitness Upto:* {data.get('fitness_upto', 'N/A')}\n"
        message += f"💰 *Tax Upto:* {data.get('tax_upto', 'N/A')}\n"
        message += f"📊 *PUC Upto:* {data.get('puc_upto', 'N/A')}\n"
        message += f"🏦 *Financier:* {data.get('financier_name', 'N/A')}\n"
        message += f"🏢 *RTO:* {data.get('rto', 'N/A')}\n"
        message += f"📍 *Address:* {data.get('address', 'N/A')}\n"
        message += f"🏙️ *City:* {data.get('city', 'N/A')}\n"
        
    except Exception as e:
        message += f"❌ Data parsing error: {str(e)}\n"
    
    return message

def format_api2_result(api2_data):
    """Format API 2 result with emojis"""
    message = "🏠 *RESULT 2 (Detailed Information):*\n\n"
    
    if 'error' in api2_data:
        message += f"❌ Error: {api2_data['error']}\n"
        return message
    
    try:
        data = api2_data
        message += f"🔢 *Asset Number:* {data.get('asset_number', 'N/A')}\n"
        message += f"🚗 *Asset Type:* {data.get('asset_type', 'N/A')}\n"
        message += f"📅 *Registration Year:* {data.get('registration_year', 'N/A')}\n"
        message += f"🗓️ *Registration Month:* {data.get('registration_month', 'N/A')}\n"
        message += f"🏭 *Make Model:* {data.get('make_model', 'N/A')}\n"
        message += f"📋 *Vehicle Type:* {data.get('vehicle_type', 'N/A')}\n"
        message += f"🔧 *Make Name:* {data.get('make_name', 'N/A')}\n"
        message += f"⛽ *Fuel Type:* {data.get('fuel_type', 'N/A')}\n"
        message += f"🔩 *Engine Number:* {data.get('engine_number', 'N/A')}\n"
        message += f"👤 *Owner Name:* {data.get('owner_name', 'N/A')}\n"
        message += f"🆔 *Chassis Number:* {data.get('chassis_number', 'N/A')}\n"
        message += f"🏢 *Previous Insurer:* {data.get('previous_insurer', 'N/A')}\n"
        message += f"🛡️ *Previous Policy Expiry:* {data.get('previous_policy_expiry_date', 'N/A')}\n"
        message += f"🏠 *Permanent Address:* {data.get('permanent_address', 'N/A')}\n"
        message += f"📍 *Present Address:* {data.get('present_address', 'N/A')}\n"
        message += f"📅 *Registration Date:* {data.get('registration_date', 'N/A')}\n"
        message += f"🏢 *Registration Address:* {data.get('registration_address', 'N/A')}\n"
        message += f"🚗 *Model Name:* {data.get('model_name', 'N/A')}\n"
        message += f"🏭 *Make Name 2:* {data.get('make_name2', 'N/A')}\n"
        message += f"📋 *Model Name 2:* {data.get('model_name2', 'N/A')}\n"
        message += f"🔄 *Previous Policy Expired:* {data.get('previous_policy_expired', 'N/A')}\n"
        
    except Exception as e:
        message += f"❌ Data parsing error: {str(e)}\n"
    
    return message

def format_results(vehicle_number, results):
    """Format the API results into a readable message"""
    
    message = f"🚗 *Vehicle Information for {vehicle_number}*\n\n"
    message += "═" * 40 + "\n\n"
    
    # Result 1 from API 1
    api1_data = results.get('api1', {})
    message += format_api1_result(api1_data)
    
    message += "\n" + "─" * 35 + "\n\n"
    
    # Result 2 from API 2
    api2_data = results.get('api2', {})
    message += format_api2_result(api2_data)
    
    message += "\n" + "═" * 40 + "\n"
    message += "🔄 *Search again? Use the button below!*"
    
    return message

def handle_vehicle_input(update: Update, context: CallbackContext) -> None:
    """Handle vehicle number input from user"""
    
    if not context.user_data.get('waiting_for_vehicle'):
        return
    
    vehicle_number = update.message.text.upper().strip()
    
    # Basic validation
    if len(vehicle_number) < 5:
        update.message.reply_text(
            "❌ *Invalid vehicle number!*\nPlease enter a valid registration number.\n\n*Example:* 🚙 UP32AB1234",
            parse_mode='Markdown'
        )
        return
    
    # Send processing message
    processing_msg = update.message.reply_text(
        f"🔍 *Searching for {vehicle_number}...*\n\n⏳ Please wait while we fetch the information...",
        parse_mode='Markdown'
    )
    
    try:
        # Get vehicle information
        results = get_vehicle_info(vehicle_number)
        
        # Format and send results
        result_message = format_results(vehicle_number, results)
        
        # Create keyboard for new search
        keyboard = [
            [InlineKeyboardButton("🔄 Search Again", callback_data='search_vehicle')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit the processing message with results
        context.bot.edit_message_text(
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
            text=result_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        error_text = f"❌ *Error occurred!*\n\nPlease try again later.\n\n⚡ Error: {str(e)}"
        context.bot.edit_message_text(
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
            text=error_text,
            parse_mode='Markdown'
        )
    
    # Reset the waiting state
    context.user_data['waiting_for_vehicle'] = False

def home_handler(update: Update, context: CallbackContext) -> None:
    """Handle home button"""
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔍 Vehicle Search", callback_data='search_vehicle')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🚗 *Welcome to Vehicle Info Bot* 🚗

I can help you get detailed information about any vehicle using its registration number.

*Features:*
• 📄 RC Vehicle Information
• 🏠 Address Details  
• ⚡ Quick & Easy Search

Click the button below to start searching!
    """
    
    query.edit_message_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main() -> None:
    """Start the bot"""
    # Create updater and dispatcher
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler, pattern='^(search_vehicle|help)$'))
    dispatcher.add_handler(CallbackQueryHandler(home_handler, pattern='^home$'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_vehicle_input))
    
    # Start the Bot
    updater.start_polling()
    updater.idle()

@app.route('/')
def index():
    return "🤖 Vehicle Info Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook handler for production"""
    update = telegram.Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return 'OK'

if __name__ == '__main__':
    # For development
    main()