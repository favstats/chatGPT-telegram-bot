"""Make some requests to OpenAI's chatbot"""
import time
import os

import telegram
from playwright.sync_api import sync_playwright
import logging

import dotenv
import nest_asyncio
# from utils.sdAPI import drawWithStability
from functools import wraps
from asyncio import wait_for

nest_asyncio.apply()
dotenv.load_dotenv()


from playwright.sync_api import sync_playwright

PLAY = sync_playwright().start()
BROWSER = PLAY.chromium.launch_persistent_context(
    user_data_dir="/tmp/playwright",
    headless=False,
)

PAGE = BROWSER.new_page()

def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("textarea")

def is_logged_in():
    # See if we have a textarea with data-id="root"
    return get_input_box() is not None


def get_last_message():
    """Get the latest message"""
    page_elements = PAGE.query_selector_all("div[class*='ConversationItem__Message']")
    last_element = page_elements[-1]
    return last_element.inner_text()


async def wait_for_element(page, selector):
    # Wait for up to 10 seconds for the element to be present on the page
    element = await wait_for(page.query_selector(selector), timeout=10)
    return element

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from telegram.helpers import escape, escape_markdown

if os.environ.get('TELEGRAM_USER_ID'):
    USER_ID = int(os.environ.get('TELEGRAM_USER_ID'))

# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)



"""Start the bot."""
# Create the Application and pass it your bot's token.
application = Application.builder().token(os.environ.get('TELEGRAM_API_KEY')).build()

def send_message(message):
    # Send the message
    print("eeeeeee")
    box = get_input_box()
    print("whaaaa")
    box.click()
    print("dssss")
    box.fill(message)
    print("ddddd")
    box.press("Enter")


class AtrributeError:
    pass



# @auth(USER_ID)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

# @auth(USER_ID)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# @auth(USER_ID)
async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    print(f"Got a reload command from user {update.effective_user.id}")
    PAGE.reload()
    await update.message.reply_text("Reloaded the browser!")
    await update.message.reply_text("Let's check if it's workin!")




async def respond_with_image(update, response):
    prompt = response.split("\[prompt:")[1].split("\]")[0]
    await update.message.reply_text(f"Generating image with prompt `{prompt.strip()}`",
                                    parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    await application.bot.send_chat_action(update.effective_chat.id, "typing")
    photo = await drawWithStability(prompt)
    await update.message.reply_photo(photo=photo, caption=f"chatGPT generated prompt: {prompt}",
                                     parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def gptchat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # print(PAGE.get_html())
    text = update.message.text
    text = text.replace("/gptchat ", "")

    send_message(text)
    await check_loading(update)
    
    print("are you ever here?")
    
    # Retrieve the latest message from the chatbot
    message = get_last_message()
    
    print(message)
    print("are you everyy there?")

    # Send the message to the user
    # context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # application.bot.send_message(chat_id=update.effective_chat.id, text=message)
    print("end")
    await update.message.reply_text(message)
    


async def check_loading(update):
    # with a timeout of 45 seconds, created a while loop that checks if loading is done
    loading = PAGE.query_selector_all("button[class^='PromptTextarea__PositionSubmit']>.text-2xl")
    #keep checking len(loading) until it's empty or 45 seconds have passed
    await application.bot.send_chat_action(update.effective_chat.id, "typing")
    start_time = time.time()
    while len(loading) > 0:
        if time.time() - start_time > 45:
            break
        time.sleep(0.5)
        loading = PAGE.query_selector_all("button[class^='PromptTextarea__PositionSubmit']>.text-2xl")
        await application.bot.send_chat_action(update.effective_chat.id, "typing")


def start_browser():

    print("begin")
    
    PAGE.goto("https://chat.openai.com/")

    if not is_logged_in():
        # Click on the first "button.btn-primary" element on the page which is the log in button
        # there are two button.btn-primary buttons, one of them is labelled "Sign Up". I don't want to click on that button
        PAGE.query_selector("button.btn-primary").click()
        
        # Find the email input element and fill it with the email stored in the EMAIL environment variable
        # Wait for the email input field to appear on the page
        email_input = PAGE.wait_for_selector("#username")
        email_input.fill(os.environ["EMAIL"])
    

        # Wait for the "Continue" button to be present on the page
        continue_button = PAGE.query_selector("button[name=action][value=default]")
        continue_button.click()
        
        # Find the password input element and fill it with the password stored in the PASSWORD environment variable
        password_input = PAGE.wait_for_selector("#password")
        # Check for the presence of the password input box using a JavaScript function
        # password_input = PAGE.wait_for_function("document.querySelector('#password') !== null")
        # password_input = PAGE.wait_for_selector("input[name='password']")
        password_input.fill(os.environ["PASSWORD"])
        # password_input.type(os.environ["PASSWORD"])
        # password_input.focus()
        # password_input.send_keys(os.environ["PASSWORD"])

    

        # Wait for the "Continue" button to be present on the page
        continue_button = PAGE.query_selector("button[name=action][value=default]")
        continue_button.click()
        
        # Wait for the login process to complete
        print("Please wait while we log you in...")
        PAGE.wait_for_selector("textarea")
        print("You are now logged in!")
        
        # PAGE.keyboard.press('Enter')
        
        # continue_button = PAGE.query_selector("button[name=next])
        # continue_button.click()
        
        # return PAGE


# if __name__ == "__main__":
start_browser()
    
# print(PAGE.content)

    
# on different commands - answer in Telegram
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("reload", reload))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("gptchat", gptchat))
# on non command i.e message - echo the message on Telegram
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo
# Run the bot until the user presses Ctrl-C
application.run_polling()


# application.bot.send_message(chat_id=update.effective_chat.id, text=message)

# send_message("asd")

# get_input_box()

# PAGE.("textarea")
# 
#  send_message("How are you doing today?")
#     await check_loading(update)
#     
#     print("are you ever here?")
#     
#     # Retrieve the latest message from the chatbot
#     message = get_last_message()
#     
#     print(message)
#     print("are you everyy there?")
# 
#     # Send the message to the user
#     context.bot.send_message(chat_id=update.effective_chat.id, text=message)
# 
# ContextTypes.DEFAULT_TYPE.bo
