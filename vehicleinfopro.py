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
Simply send any vehicle registration number to begin analysis.

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
1. {Style.CAR} Send vehicle registration number
2. {Style.LOADING} Wait for processing
3. {Style.SUCCESS} Receive detailed report

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
Send any vehicle number to begin!
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
        context.user_data['waiting_for_vehicle'] = True

def clean_vehicle_number(number: str) -> str:
    """Clean and validate vehicle number."""
    cleaned = number.upper().strip()
    # Remove spaces and special characters, keep alphanumeric
    cleaned = ''.join(c for c in cleaned if c.isalnum())
    return cleaned

def get_vehicle_info(vehicle_number):
    """Fetch vehicle information from both APIs"""
    results = {}
    
    try:
        # API 1
        api1_response = requests.get(f"{API1_URL}{vehicle_number}", timeout=15)
        if api1_response.status_code == 200:
            results['api1'] = api1_response.json()
        else:
            results['api1'] = {"error": f"API returned status: {api1_response.status_code}"}
    except Exception as e:
        results['api1'] = {"error": f"API Error: {str(e)}"}
    
    try:
        # API 2
        api2_response = requests.get(f"{API2_URL}{vehicle_number}", timeout=15)
        if api2_response.status_code == 200:
            results['api2'] = api2_response.json()
        else:
            results['api2'] = {"error": f"API returned status: {api2_response.status_code}"}
    except Exception as e:
        results['api2'] = {"error": f"API Error: {str(e)}"}
    
    return results

def format_api1_result(api1_data):
    """Format API 1 result with emojis"""
    if 'error' in api1_data:
        return f"{Style.ERROR} *RC Information:* {api1_data['error']}\n"
    
    try:
        data = api1_data
        message = f"{Style.DOCUMENT} *RC INFORMATION*\n\n"
        message += f"{Style.USER} *Owner:* {data.get('owner_name', 'Not Available')}\n"
        message += f"{Style.FATHER} *Father:* {data.get('father_name', 'Not Available')}\n"
        message += f"🔢 *Owner Serial:* {data.get('owner_serial_no', 'Not Available')}\n"
        message += f"{Style.FACTORY} *Manufacturer:* {data.get('model_name', 'Not Available')}\n"
        message += f"{Style.CAR} *Model:* {data.get('maker_model', 'Not Available')}\n"
        message += f"📋 *Vehicle Class:* {data.get('vehicle_class', 'Not Available')}\n"
        message += f"{Style.FUEL} *Fuel Type:* {data.get('fuel_type', 'Not Available')}\n"
        message += f"🌱 *Fuel Norms:* {data.get('fuel_norms', 'Not Available')}\n"
        message += f"{Style.CALENDAR} *Registration Date:* {data.get('registration_date', 'Not Available')}\n"
        message += f"🏢 *Insurance Company:* {data.get('insurance_company', 'Not Available')}\n"
        message += f"{Style.SHIELD} *Insurance Upto:* {data.get('insurance_upto', 'Not Available')}\n"
        message += f"{Style.SUCCESS} *Fitness Upto:* {data.get('fitness_upto', 'Not Available')}\n"
        message += f"{Style.MONEY} *Tax Upto:* {data.get('tax_upto', 'Not Available')}\n"
        message += f"📊 *PUC Upto:* {data.get('puc_upto', 'Not Available')}\n"
        message += f"🏦 *Financier:* {data.get('financier_name', 'Not Available')}\n"
        message += f"🏢 *RTO:* {data.get('rto', 'Not Available')}\n"
        message += f"{Style.LOCATION} *Address:* {data.get('address', 'Not Available')}\n"
        message += f"🏙️ *City:* {data.get('city', 'Not Available')}\n"
        
        return message
    except Exception as e:
        return f"{Style.ERROR} *RC Information:* Data parsing error\n"

def format_api2_result(api2_data):
    """Format API 2 result with emojis"""
    if 'error' in api2_data:
        return f"{Style.ERROR} *Detailed Information:* {api2_data['error']}\n"
    
    try:
        data = api2_data
        message = f"{Style.INFO} *DETAILED INFORMATION*\n\n"
        message += f"🔢 *Asset Number:* {data.get('asset_number', 'Not Available')}\n"
        message += f"{Style.CAR} *Asset Type:* {data.get('asset_type', 'Not Available')}\n"
        message += f"{Style.CALENDAR} *Registration Year:* {data.get('registration_year', 'Not Available')}\n"
        message += f"🗓️ *Registration Month:* {data.get('registration_month', 'Not Available')}\n"
        message += f"{Style.FACTORY} *Make Model:* {data.get('make_model', 'Not Available')}\n"
        message += f"📋 *Vehicle Type:* {data.get('vehicle_type', 'Not Available')}\n"
        message += f"{Style.ENGINE} *Make Name:* {data.get('make_name', 'Not Available')}\n"
        message += f"{Style.FUEL} *Fuel Type:* {data.get('fuel_type', 'Not Available')}\n"
        message += f"🔩 *Engine Number:* {data.get('engine_number', 'Not Available')}\n"
        message += f"{Style.USER} *Owner Name:* {data.get('owner_name', 'Not Available')}\n"
        message += f"🆔 *Chassis Number:* {data.get('chassis_number', 'Not Available')}\n"
        message += f"🏢 *Previous Insurer:* {data.get('previous_insurer', 'Not Available')}\n"
        message += f"{Style.SHIELD} *Previous Policy Expiry:* {data.get('previous_policy_expiry_date', 'Not Available')}\n"
        message += f"{Style.LOCATION} *Permanent Address:* {data.get('permanent_address', 'Not Available')}\n"
        message += f"📍 *Present Address:* {data.get('present_address', 'Not Available')}\n"
        message += f"{Style.CALENDAR} *Registration Date:* {data.get('registration_date', 'Not Available')}\n"
        message += f"🏢 *Registration Address:* {data.get('registration_address', 'Not Available')}\n"
        message += f"{Style.CAR} *Model Name:* {data.get('model_name', 'Not Available')}\n"
        message += f"{Style.FACTORY} *Make Name 2:* {data.get('make_name2', 'Not Available')}\n"
        message += f"📋 *Model Name 2:* {data.get('model_name2', 'Not Available')}\n"
        message += f"🔄 *Previous Policy Expired:* {data.get('previous_policy_expired', 'Not Available')}\n"
        
        return message
    except Exception as e:
        return f"{Style.ERROR} *Detailed Information:* Data parsing error\n"

async def handle_vehicle_input(update: Update, context: CallbackContext) -> None:
    """Handle vehicle number input from user"""
    
    if not context.user_data.get('waiting_for_vehicle'):
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
    loading_message_id = await show_loading(chat_id, context)
    
    try:
        # Get vehicle information
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
        await context.bot.delete_message(chat_id=chat_id, message_id=loading_message_id)
        
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
        logger.error(f"Error processing vehicle: {e}")
        error_text = f"""
{Style.ERROR} *System Error*

An error occurred while processing your request.

*Vehicle:* `{clean_number}`
*Error:* Service temporarily unavailable

{Style.WARNING} Please try again in a few minutes.
        """
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=loading_message_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Reset the waiting state
    context.user_data['waiting_for_vehicle'] = False

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all other messages."""
    text = update.message.text
    
    # Check if message looks like a vehicle number
    cleaned_text = text.upper().strip()
    if any(c.isalnum() for c in cleaned_text) and len(cleaned_text) >= 5:
        context.user_data['waiting_for_vehicle'] = True
        await handle_vehicle_input(update, context)
    else:
        help_text = f"""
{Style.ERROR} *Invalid Input*

Please send a valid vehicle registration number.

{Style.SEARCH} *Supported Formats:*
• `UP32AB1234`
• `DL1CAB1234`
• `HR26DK7890`

{Style.HELP} Use /help for complete instructions.
        """
        await update.message.reply_text(
            help_text,
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