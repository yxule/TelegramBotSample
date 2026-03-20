import asyncio

import logging

from os import path, getenv
from json import load, dump
from dotenv import load_dotenv

from telegram import Update, Message, CallbackQuery
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, filters
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)

load_dotenv('.env')

TOKEN = getenv('TELEGRAM_BOT_TOKEN')
CALLBACK_DATA_SEPARATORS = getenv('CALLBACK_DATA_SEPARATORS')

def get_data(update: Update, is_query: bool = False) -> dict:
    """Return a structuring `dict` with (`user_id`, `user_name`, `chat_id`, `chat_name`, `message`, `message_id`, `query`)"""
    if is_query:
        query = update.callback_query

        message = query.data
        message_id = query.message.message_id
    else:
        query = None

        message = update.effective_message.text
        message_id = update.effective_message.id
    
    user_id = update.effective_sender.id
    user_name = update.effective_sender.name

    chat_id = update.effective_chat.id
    chat_name = update.effective_chat.full_name

    data = {
        'user_id': user_id,
        'user_name': user_name,
        
        'chat_id': chat_id,
        'chat_name': chat_name,

        'message': message,
        'message_id': message_id,

        'query': query
    }

    return data

class TelegramBotEdit:
    async def _send_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, **kwargs):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                **kwargs
            )
        except Exception as exc: logging.error(exc)
    async def _edit_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, text: str = None, reply_markup: InlineKeyboardMarkup = None):
        if all([not text, not reply_markup]): return
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text if text else '',
                reply_markup=reply_markup
            )
        except Exception as exc: logging.error(exc)
    async def _edit_message_text(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, text: str):
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
        except Exception as exc: logging.error(exc)
    async def _edit_message_reply_markup(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, reply_markup: InlineKeyboardMarkup):
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup
            )
        except Exception as exc: logging.error(exc)

class TelegramBotCallbackQuery(TelegramBotEdit):
    def __init__(self): super().__init__()

    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = get_data(update, is_query=True)

        if any([s in data['message'] for s in list(CALLBACK_DATA_SEPARATORS)]):
            # Handler-part for splitkeyboard return (like 'set_active:0' in callback)
            pass
        else:
            # Handler-part for simple keyboard return (like 'menu' in callback)
            pass

class TelegramBot(TelegramBotCallbackQuery):
    def __init__(self): super().__init__()

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = get_data(update)

        if data['message'] == '': # Sample
            # Text message handler
            pass
        else:
            # Non-key-word
            pass

    ### COMMANDS ###
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = get_data(update)
        # '/start' Command echo-sample
        await self._send_message(context=context, chat_id=data['chat_id'], text=data['message'])
        #
    ################

if __name__ == "__main__":
    builder = ApplicationBuilder()
    app = builder.token(TOKEN).build()

    bot = TelegramBot()

    start_command_handler = CommandHandler('start', bot.start_command)
    callback_query_handler = CallbackQueryHandler(bot.query_handler)
    text_message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), bot.message_handler)

    app.add_handlers(
        {
            -1: [start_command_handler],
            1: [callback_query_handler],
            2: [text_message_handler]
        }
    )
    
    app.run_polling()