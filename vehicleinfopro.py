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
    return "🚗 Vehicle Info Pro Bot is running!"

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

📋 *How to Search:*
1. Click *Vehicle Search* button below
2. Enter vehicle registration number
3. Get instant results

*Examples:* `UP32AB1234`, `DL1CAB1234`, `HR26DK7890`
    """
    
    keyboard = [
        [InlineKeyboardButton(f"{Style.SEARCH} Vehicle Search", callback_data="search_vehicle")],
        [InlineKeyboardButton(f"{Style.HELP} Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message."""
    help_text = f"""
{Style.HELP} *HOW TO USE*

1. Click *Vehicle Search* button
2. Enter registration number
3. Get detailed information

*Supported Formats:*
• UP32AB1234
• DL1CAB1234  
• HR26DK7890

*Information Provided:*
• Owner details
• Vehicle specifications  
• Insurance information
• Address details
    """
    
    keyboard = [
        [InlineKeyboardButton(f"{Style.SEARCH} Start Search", callback_data="search_vehicle")],
        [InlineKeyboardButton(f"{Style.HOME} Main Menu", callback_data="main_menu")]
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

async def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle inline button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await help_command(update, context)
    elif query.data == "main_menu":
        await start(update, context)
    elif query.data == "search_vehicle":
        search_text = f"""
{Style.SEARCH} *VEHICLE SEARCH*

Please enter the vehicle registration number:

*Examples:*
• `UP32AB1234`
• `DL1CAB1234`
• `HR26DK7890`

ℹ️ Enter the number without spaces.
        """
        await query.edit_message_text(
            search_text,
            parse_mode=ParseMode.MARKDOWN
        )
        # Store that we're waiting for vehicle input
        context.user_data['expecting_vehicle'] = True

def clean_vehicle_number(number: str) -> str:
    """Clean and validate vehicle number."""
    cleaned = number.upper().strip()
    # Remove spaces and special characters, keep alphanumeric
    cleaned = ''.join(c for c in cleaned if c.isalnum())
    return cleaned

def get_vehicle_info(vehicle_number):
    """Fetch vehicle information from both APIs"""
    results = {}
    
    # API 1 - RC Information
    try:
        logger.info(f"Calling API1: {API1_URL}{vehicle_number}")
        api1_response = requests.get(f"{API1_URL}{vehicle_number}", timeout=15)
        if api1_response.status_code == 200:
            results['api1'] = api1_response.json()
        else:
            results['api1'] = {"error": f"API1 HTTP {api1_response.status_code}"}
    except Exception as e:
        results['api1'] = {"error": f"API1 Error: {str(e)}"}
    
    # API 2 - Detailed Information  
    try:
        logger.info(f"Calling API2: {API2_URL}{vehicle_number}")
        api2_response = requests.get(f"{API2_URL}{vehicle_number}", timeout=15)
        if api2_response.status_code == 200:
            results['api2'] = api2_response.json()
        else:
            results['api2'] = {"error": f"API2 HTTP {api2_response.status_code}"}
    except Exception as e:
        results['api2'] = {"error": f"API2 Error: {str(e)}"}
    
    return results

def format_vehicle_results(vehicle_number, results):
    """Format the vehicle information results"""
    
    result_text = f"""
{Style.CAR} *VEHICLE INFORMATION REPORT*

*Registration Number:* `{vehicle_number}`
*Report Time:* {time.strftime('%Y-%m-%d %H:%M:%S')}

────────────────────
    """
    
    # API 1 Results
    api1_data = results.get('api1', {})
    if 'error' in api1_data:
        result_text += f"\n{Style.ERROR} *RC Information:* {api1_data['error']}\n"
    else:
        result_text += f"\n{Style.DOCUMENT} *RC INFORMATION*\n\n"
        data = api1_data
        fields = [
            (f"{Style.USER} Owner", data.get('owner_name')),
            (f"{Style.FATHER} Father", data.get('father_name')),
            (f"🔢 Serial", data.get('owner_serial_no')),
            (f"{Style.FACTORY} Manufacturer", data.get('model_name')),
            (f"{Style.CAR} Model", data.get('maker_model')),
            (f"📋 Class", data.get('vehicle_class')),
            (f"{Style.FUEL} Fuel", data.get('fuel_type')),
            (f"{Style.CALENDAR} Reg Date", data.get('registration_date')),
            (f"🏢 Insurance Co", data.get('insurance_company')),
            (f"{Style.SHIELD} Insurance Upto", data.get('insurance_upto')),
            (f"{Style.SUCCESS} Fitness Upto", data.get('fitness_upto')),
            (f"{Style.MONEY} Tax Upto", data.get('tax_upto')),
            (f"{Style.LOCATION} Address", data.get('address')),
            (f"🏙️ City", data.get('city'))
        ]
        
        for label, value in fields:
            if value and str(value).strip() and str(value).lower() not in ['n/a', 'null', 'none', '']:
                result_text += f"• {label}: {value}\n"
    
    result_text += "\n────────────────────\n"
    
    # API 2 Results
    api2_data = results.get('api2', {})
    if 'error' in api2_data:
        result_text += f"\n{Style.ERROR} *Detailed Info:* {api2_data['error']}\n"
    else:
        result_text += f"\n{Style.INFO} *DETAILED INFORMATION*\n\n"
        data = api2_data
        fields = [
            (f"🔢 Asset No", data.get('asset_number')),
            (f"{Style.CAR} Asset Type", data.get('asset_type')),
            (f"{Style.CALENDAR} Reg Year", data.get('registration_year')),
            (f"{Style.FACTORY} Make Model", data.get('make_model')),
            (f"{Style.ENGINE} Make Name", data.get('make_name')),
            (f"{Style.FUEL} Fuel Type", data.get('fuel_type')),
            (f"🔩 Engine No", data.get('engine_number')),
            (f"{Style.USER} Owner Name", data.get('owner_name')),
            (f"🆔 Chassis No", data.get('chassis_number')),
            (f"{Style.LOCATION} Address", data.get('permanent_address')),
            (f"📍 Present Address", data.get('present_address'))
        ]
        
        for label, value in fields:
            if value and str(value).strip() and str(value).lower() not in ['n/a', 'null', 'none', '']:
                result_text += f"• {label}: {value}\n"
    
    result_text += f"\n{Style.SHIELD} *Data Source:* Verified Vehicle Databases"
    
    return result_text

async def handle_vehicle_search(update: Update, context: CallbackContext) -> None:
    """Handle vehicle number input from user"""
    
    # Check if we're expecting a vehicle number
    if not context.user_data.get('expecting_vehicle', False):
        # If user just sends a vehicle number without clicking button first
        vehicle_number = clean_vehicle_number(update.message.text)
        if len(vehicle_number) >= 5:
            # Process it anyway
            await process_vehicle_number(update, context, vehicle_number)
            return
        else:
            await update.message.reply_text(
                f"{Style.INFO} Please use the *Vehicle Search* button first to search for a vehicle.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"{Style.SEARCH} Vehicle Search", callback_data="search_vehicle")]
                ])
            )
            return
    
    vehicle_number = clean_vehicle_number(update.message.text)
    
    # Basic validation
    if len(vehicle_number) < 5:
        await update.message.reply_text(
            f"{Style.ERROR} *Invalid vehicle number!*\n\nPlease enter a valid registration number (minimum 5 characters).\n\n*Examples:*\n• `UP32AB1234`\n• `DL1CAB1234`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await process_vehicle_number(update, context, vehicle_number)

async def process_vehicle_number(update: Update, context: CallbackContext, vehicle_number: str) -> None:
    """Process the vehicle number and send results"""
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"{Style.LOADING} *Searching for vehicle {vehicle_number}...*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Get vehicle information
        logger.info(f"Fetching info for vehicle: {vehicle_number}")
        results = get_vehicle_info(vehicle_number)
        
        # Format and send results
        result_text = format_vehicle_results(vehicle_number, results)
        
        # Delete processing message
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id
        )
        
        # Create keyboard for navigation
        keyboard = [
            [InlineKeyboardButton(f"{Style.RELOAD} Search Again", callback_data="search_vehicle")],
            [InlineKeyboardButton(f"{Style.HOME} Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send result
        await update.message.reply_text(
            result_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Successfully sent results for vehicle: {vehicle_number}")
        
    except Exception as e:
        logger.error(f"Error processing vehicle {vehicle_number}: {str(e)}")
        
        # Update processing message with error
        error_text = f"""
{Style.ERROR} *Search Failed*

Unable to retrieve information for `{vehicle_number}`.

*Possible reasons:*
• Vehicle number not found in databases
• Temporary service outage
• Invalid registration number

{Style.WARNING} Please try again with a different number.
        """
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{Style.RELOAD} Try Again", callback_data="search_vehicle")],
                [InlineKeyboardButton(f"{Style.HOME} Main Menu", callback_data="main_menu")]
            ])
        )
    
    # Clear the expecting state
    context.user_data['expecting_vehicle'] = False

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle all text messages."""
    text = update.message.text
    
    # Check if it might be a vehicle number
    cleaned_text = clean_vehicle_number(text)
    if len(cleaned_text) >= 5:
        # Check if we're expecting a vehicle number or if user might be trying to search
        if context.user_data.get('expecting_vehicle', False) or any(keyword in text.upper() for keyword in ['UP', 'DL', 'HR', 'PB', 'GJ', 'KA', 'TN', 'MH']):
            await handle_vehicle_search(update, context)
            return
    
    # Default response for other messages
    help_text = f"""
{Style.INFO} *Vehicle Info Pro Bot*

I can help you get detailed vehicle information by registration number.

To get started:
1. Click *Vehicle Search* button below
2. Enter the vehicle registration number
3. Receive detailed information

*Example numbers:*
• UP32AB1234
• DL1CAB1234
• HR26DK7890
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
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(help|main_menu|search_vehicle)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    print("🚗 VEHICLE INFO PRO BOT - Starting...")
    print(f"{Style.SERVER} Keep-Alive: http://0.0.0.0:{KEEP_ALIVE_PORT}")
    print(f"{Style.CAR} Bot Token: {BOT_TOKEN[:10]}...")
    print(f"{Style.SUCCESS} Bot is running and ready!")
    
    try:
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"{Style.ERROR} Bot stopped: {e}")

if __name__ == '__main__':
    main()