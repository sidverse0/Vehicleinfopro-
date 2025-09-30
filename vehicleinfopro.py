import os
import logging
import requests
import json
import time
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

# Bot Configuration
BOT_TOKEN = "8223529849:AAGZmFjRzTDPWi7fcFthjThIuldj1bNv_qs"
KEEP_ALIVE_PORT = 8081

# API endpoints
API1_URL = "https://revangevichelinfo.vercel.app/api/rc?number="
API2_URL = "https://caller.hackershub.shop/info.php?type=address&registration="

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user data
user_sessions = {}

# Stylish fonts and symbols
class Style:
    CAR = "🚗"
    SEARCH = "🔍"
    HELP = "❓"
    HOME = "🏠"
    RELOAD = "🔄"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    LOADING = "⏳"
    DOCUMENT = "📄"
    LOCATION = "📍"
    CALENDAR = "📅"
    ENGINE = "🔧"
    FUEL = "⛽"
    USER = "👤"
    FATHER = "👨‍👦"
    FACTORY = "🏭"
    SHIELD = "🛡️"
    MONEY = "💰"
    ROCKET = "🚀"
    SERVER = "🌐"
    INFO = "ℹ️"

# Create Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vehicle Info Pro Bot - Status</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            .status {{
                background: green;
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
            }}
            .info-box {{
                background: rgba(255, 255, 255, 0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
            }}
            .feature {{
                background: rgba(255, 255, 255, 0.15);
                padding: 10px;
                margin: 5px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Vehicle Info Pro Bot</h1>
            <div class="status">🟢 ONLINE & RUNNING</div>
            
            <div class="info-box">
                <h3>📊 Bot Information</h3>
                <p><strong>Status:</strong> Active & Monitoring</p>
                <p><strong>Uptime:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Service:</strong> Telegram Vehicle Information Bot</p>
            </div>
            
            <div class="info-box">
                <h3>🚀 Features</h3>
                <div class="feature">📄 RC Vehicle Information</div>
                <div class="feature">🏠 Address Details</div>
                <div class="feature">🔧 Technical Specifications</div>
                <div class="feature">🛡️ Insurance & Tax Details</div>
            </div>
            
            <div class="info-box">
                <h3>🌐 Keep Alive Server</h3>
                <p>This server keeps the bot running 24/7</p>
                <p><strong>Port:</strong> {KEEP_ALIVE_PORT}</p>
                <p><strong>Status:</strong> Active</p>
            </div>
            
            <div class="info-box">
                <h3>📞 Contact Bot</h3>
                <p>Search for <strong>@vehicle_info_pro_bot</strong> on Telegram</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": time.time(), "service": "vehicle_info_pro_bot"}

def run_keep_alive():
    """Run the keep-alive server in a separate thread"""
    print(f"{Style.SERVER} Starting keep-alive server on port {KEEP_ALIVE_PORT}...")
    app.run(host='0.0.0.0', port=KEEP_ALIVE_PORT, debug=False, use_reloader=False)

async def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    
    welcome_text = f"""
{Style.ROCKET} *WELCOME TO VEHICLE INFO PRO BOT* {Style.ROCKET}

👋 Hello *{user.first_name}*!

{Style.CAR} *Advanced Vehicle Intelligence Platform*
{Style.SHIELD} *Secure • Fast • Professional*

✨ *Features:*
• {Style.DOCUMENT} Complete RC Information
• {Style.LOCATION} Address Verification  
• {Style.ENGINE} Technical Specifications
• {Style.SHIELD} Insurance & Tax Details
• {Style.FACTORY} Manufacturer Details

📋 *Quick Start:*
Click the button below and enter vehicle registration number.

*Formats Supported:*
• `UP32AB1234`
• `DL1CAB1234`
• `HR26DK7890`

{Style.WARNING} *Legal Notice:* Use responsibly in compliance with applicable laws.
    """
    
    keyboard = [
        [InlineKeyboardButton(f"{Style.SEARCH} Vehicle Search", callback_data="search_vehicle")],
        [InlineKeyboardButton(f"{Style.HELP} Get Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message."""
    help_text = f"""
{Style.HELP} *VEHICLE INFO PRO BOT - HELP GUIDE* {Style.HELP}

{Style.SEARCH} *How to Use:*
1. Click *"Vehicle Search"* button
2. Enter vehicle registration number  
3. Wait for processing
4. Receive detailed report

{Style.INFO} *Supported Formats:*
• Standard format: `UP32AB1234`
• Delhi numbers: `DL1CAB1234`  
• Haryana numbers: `HR26DK7890`

{Style.SHIELD} *Security Features:*
• Encrypted communication
• No data storage
• Privacy focused

{Style.WARNING} *Important Notes:*
• Service availability depends on data sources
• Results may vary by region
• Always verify information from official sources

*Ready to search?*
Click the button below to begin!
    """
    
    keyboard = [
        [InlineKeyboardButton(f"{Style.HOME} Main Menu", callback_data="main_menu")],
        [InlineKeyboardButton(f"{Style.SEARCH} Start Search", callback_data="search_vehicle")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            help_text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.callback_query.edit_message_text(
            help_text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def show_loading(chat_id, context: CallbackContext):
    """Show single loading message."""
    loading_text = f"{Style.LOADING} *Processing your request...*"
    
    message = await context.bot.send_message(
        chat_id=chat_id,
        text=loading_text,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return message.message_id

async def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "main_menu":
        await start(update, context)
    elif query.data == "search_vehicle":
        await query.edit_message_text(
            f"{Style.SEARCH} *VEHICLE SEARCH*\n\nPlease enter the vehicle registration number:\n\n*Examples:*\n• `UP32AB1234`\n• `DL1CAB1234`\n• `HR26DK7890`",
            parse_mode=ParseMode.MARKDOWN
        )
        # Set the state to wait for vehicle input
        context.user_data['waiting_for_vehicle'] = True

def clean_vehicle_number(number: str) -> str:
    """Clean and validate vehicle number."""
    cleaned = number.upper().strip()
    # Remove spaces and special characters, keep alphanumeric
    cleaned = ''.join(c for c in cleaned if c.isalnum())
    return cleaned

def get_vehicle_info(vehicle_number):
    """Fetch vehicle information from both APIs with enhanced error handling"""
    results = {}
    
    try:
        # API 1 - RC Information
        logger.info(f"Calling API1 for vehicle: {vehicle_number}")
        api1_response = requests.get(f"{API1_URL}{vehicle_number}", timeout=20)
        logger.info(f"API1 Response Status: {api1_response.status_code}")
        
        if api1_response.status_code == 200:
            try:
                api1_data = api1_response.json()
                results['api1'] = api1_data
                logger.info(f"API1 Data received: {bool(api1_data)}")
            except json.JSONDecodeError:
                results['api1'] = {"error": "Invalid JSON response from API1"}
                logger.error("API1 returned invalid JSON")
        else:
            results['api1'] = {"error": f"API1 returned status: {api1_response.status_code}"}
            logger.error(f"API1 Error: {api1_response.status_code}")
            
    except requests.exceptions.Timeout:
        results['api1'] = {"error": "API1 request timeout"}
        logger.error("API1 timeout")
    except Exception as e:
        results['api1'] = {"error": f"API1 Error: {str(e)}"}
        logger.error(f"API1 Exception: {str(e)}")
    
    try:
        # API 2 - Detailed Information
        logger.info(f"Calling API2 for vehicle: {vehicle_number}")
        api2_response = requests.get(f"{API2_URL}{vehicle_number}", timeout=20)
        logger.info(f"API2 Response Status: {api2_response.status_code}")
        
        if api2_response.status_code == 200:
            try:
                api2_data = api2_response.json()
                results['api2'] = api2_data
                logger.info(f"API2 Data received: {bool(api2_data)}")
            except json.JSONDecodeError:
                results['api2'] = {"error": "Invalid JSON response from API2"}
                logger.error("API2 returned invalid JSON")
        else:
            results['api2'] = {"error": f"API2 returned status: {api2_response.status_code}"}
            logger.error(f"API2 Error: {api2_response.status_code}")
            
    except requests.exceptions.Timeout:
        results['api2'] = {"error": "API2 request timeout"}
        logger.error("API2 timeout")
    except Exception as e:
        results['api2'] = {"error": f"API2 Error: {str(e)}"}
        logger.error(f"API2 Exception: {str(e)}")
    
    return results

def format_api1_result(api1_data):
    """Format API 1 result with emojis"""
    if 'error' in api1_data:
        return f"{Style.ERROR} *RC Information:* {api1_data['error']}\n"
    
    try:
        data = api1_data
        # Check if data is empty
        if not data or len(data) == 0:
            return f"{Style.WARNING} *RC Information:* No data available\n"
            
        message = f"{Style.DOCUMENT} *RC INFORMATION*\n\n"
        
        # Safely get values with defaults
        fields = [
            (f"{Style.USER} *Owner:*", data.get('owner_name')),
            (f"{Style.FATHER} *Father:*", data.get('father_name')),
            (f"🔢 *Owner Serial:*", data.get('owner_serial_no')),
            (f"{Style.FACTORY} *Manufacturer:*", data.get('model_name')),
            (f"{Style.CAR} *Model:*", data.get('maker_model')),
            (f"📋 *Vehicle Class:*", data.get('vehicle_class')),
            (f"{Style.FUEL} *Fuel Type:*", data.get('fuel_type')),
            (f"🌱 *Fuel Norms:*", data.get('fuel_norms')),
            (f"{Style.CALENDAR} *Registration Date:*", data.get('registration_date')),
            (f"🏢 *Insurance Company:*", data.get('insurance_company')),
            (f"{Style.SHIELD} *Insurance Upto:*", data.get('insurance_upto')),
            (f"{Style.SUCCESS} *Fitness Upto:*", data.get('fitness_upto')),
            (f"{Style.MONEY} *Tax Upto:*", data.get('tax_upto')),
            (f"📊 *PUC Upto:*", data.get('puc_upto')),
            (f"🏦 *Financier:*", data.get('financier_name')),
            (f"🏢 *RTO:*", data.get('rto')),
            (f"{Style.LOCATION} *Address:*", data.get('address')),
            (f"🏙️ *City:*", data.get('city'))
        ]
        
        for label, value in fields:
            if value and str(value).strip() and str(value).lower() != 'n/a':
                message += f"{label} {value}\n"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting API1 data: {str(e)}")
        return f"{Style.ERROR} *RC Information:* Data formatting error\n"

def format_api2_result(api2_data):
    """Format API 2 result with emojis"""
    if 'error' in api2_data:
        return f"{Style.ERROR} *Detailed Information:* {api2_data['error']}\n"
    
    try:
        data = api2_data
        # Check if data is empty
        if not data or len(data) == 0:
            return f"{Style.WARNING} *Detailed Information:* No data available\n"
            
        message = f"{Style.INFO} *DETAILED INFORMATION*\n\n"
        
        # Safely get values with defaults
        fields = [
            (f"🔢 *Asset Number:*", data.get('asset_number')),
            (f"{Style.CAR} *Asset Type:*", data.get('asset_type')),
            (f"{Style.CALENDAR} *Registration Year:*", data.get('registration_year')),
            (f"🗓️ *Registration Month:*", data.get('registration_month')),
            (f"{Style.FACTORY} *Make Model:*", data.get('make_model')),
            (f"📋 *Vehicle Type:*", data.get('vehicle_type')),
            (f"{Style.ENGINE} *Make Name:*", data.get('make_name')),
            (f"{Style.FUEL} *Fuel Type:*", data.get('fuel_type')),
            (f"🔩 *Engine Number:*", data.get('engine_number')),
            (f"{Style.USER} *Owner Name:*", data.get('owner_name')),
            (f"🆔 *Chassis Number:*", data.get('chassis_number')),
            (f"🏢 *Previous Insurer:*", data.get('previous_insurer')),
            (f"{Style.SHIELD} *Previous Policy Expiry:*", data.get('previous_policy_expiry_date')),
            (f"{Style.LOCATION} *Permanent Address:*", data.get('permanent_address')),
            (f"📍 *Present Address:*", data.get('present_address')),
            (f"{Style.CALENDAR} *Registration Date:*", data.get('registration_date')),
            (f"🏢 *Registration Address:*", data.get('registration_address')),
            (f"{Style.CAR} *Model Name:*", data.get('model_name')),
            (f"{Style.FACTORY} *Make Name 2:*", data.get('make_name2')),
            (f"📋 *Model Name 2:*", data.get('model_name2')),
            (f"🔄 *Previous Policy Expired:*", data.get('previous_policy_expired'))
        ]
        
        for label, value in fields:
            if value and str(value).strip() and str(value).lower() != 'n/a':
                message += f"{label} {value}\n"
        
        return message
        
    except Exception as e:
        logger.error(f"Error formatting API2 data: {str(e)}")
        return f"{Style.ERROR} *Detailed Information:* Data formatting error\n"

async def handle_vehicle_search(update: Update, context: CallbackContext) -> None:
    """Handle vehicle number input from user"""
    
    # Check if we're waiting for vehicle input
    if not context.user_data.get('waiting_for_vehicle', False):
        # If not in waiting state, ask user to use the button first
        await update.message.reply_text(
            f"{Style.INFO} Please use the 'Vehicle Search' button first to start a search.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    vehicle_number = update.message.text
    clean_number = clean_vehicle_number(vehicle_number)
    
    # Basic validation
    if len(clean_number) < 5:
        await update.message.reply_text(
            f"{Style.ERROR} *Invalid vehicle number!*\n\nPlease enter a valid registration number.\n\n*Examples:*\n• `UP32AB1234`\n• `DL1CAB1234`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    chat_id = update.effective_chat.id
    
    # Show loading message
    loading_message = await update.message.reply_text(
        f"{Style.LOADING} *Searching for vehicle {clean_number}...*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Get vehicle information
        logger.info(f"Processing vehicle: {clean_number}")
        results = get_vehicle_info(clean_number)
        
        # Format results
        result_text = f"""
{Style.CAR} *VEHICLE INTELLIGENCE REPORT* {Style.CAR}

*Registration Number:* `{clean_number}`
{Style.CALENDAR} *Report Generated:* {time.strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━
        """
        
        # Add API 1 results
        api1_message = format_api1_result(results.get('api1', {}))
        result_text += f"\n{api1_message}"
        
        result_text += "\n━━━━━━━━━━━━━━━━━━━━\n"
        
        # Add API 2 results
        api2_message = format_api2_result(results.get('api2', {}))
        result_text += f"\n{api2_message}"
        
        result_text += f"\n{Style.SHIELD} *Data Source:* Verified Vehicle Databases"
        
        # Delete loading message
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=loading_message.message_id
        )
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton(f"{Style.RELOAD} New Search", callback_data="search_vehicle")],
            [InlineKeyboardButton(f"{Style.HOME} Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send result
        await update.message.reply_text(
            result_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error processing vehicle {clean_number}: {str(e)}")
        
        # Update loading message with error
        error_text = f"""
{Style.ERROR} *System Error*

An error occurred while processing your request.

*Vehicle:* `{clean_number}`
*Error:* Service temporarily unavailable

{Style.WARNING} Please try again in a few minutes.
        """
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=loading_message.message_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Reset the waiting state
    context.user_data['waiting_for_vehicle'] = False

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all text messages."""
    
    # Check if we're waiting for vehicle input
    if context.user_data.get('waiting_for_vehicle', False):
        await handle_vehicle_search(update, context)
    else:
        # If not in waiting state, show help
        help_text = f"""
{Style.INFO} *Vehicle Info Pro Bot*

I can help you get detailed information about any vehicle.

To get started:
1. Click the *'Vehicle Search'* button
2. Enter the vehicle registration number
3. Receive detailed information

*Example vehicle numbers:*
• `UP32AB1234`
• `DL1CAB1234` 
• `HR26DK7890`

Click below to start searching!
        """
        
        keyboard = [
            [InlineKeyboardButton(f"{Style.SEARCH} Vehicle Search", callback_data="search_vehicle")],
            [InlineKeyboardButton(f"{Style.HELP} Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

def main() -> None:
    """Start the bot and keep-alive server."""
    
    # Start keep-alive server in a separate thread
    keep_alive_thread = threading.Thread(target=run_keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Create Telegram Bot Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(help|main_menu|search_vehicle)$"))
    
    # Start the Bot with enhanced logging
    print("🚗 VEHICLE INFO PRO BOT - Starting Services...")
    print("=" * 50)
    print(f"{Style.SERVER} Keep-Alive Server: http://0.0.0.0:{KEEP_ALIVE_PORT}")
    print(f"{Style.CAR} Telegram Bot: Active & Monitoring")
    print(f"{Style.SHIELD} Status: ONLINE & READY")
    print("=" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Start polling with better error handling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"{Style.ERROR} Bot service stopped due to error: {e}")
    finally:
        print("⏹️ All services stopped.")

if __name__ == '__main__':
    main()