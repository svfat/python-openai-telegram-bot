#!/usr/bin/env python3

import logging

import openai
from telegram import Update

from config import TELEGRAM_TOKEN, OPENAI_API_KEY, OPENAI_MODEL_NAME, DEFAULT_BOT_COMMAND
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, \
    CallbackContext

openai.api_key = OPENAI_API_KEY

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def clean_command_header(text: str, header: str = f'/{DEFAULT_BOT_COMMAND} ') -> str:
    """
    Remove the command header from the text
    :param text:
    :param header:
    :return:
    """
    if text.startswith(header):
        text = text[len(header):]
    return text

def complete_prompt(prompt:str):
    """
    Complete the prompt using OpenAI
    :param prompt:
    :return:
    """
    if len(prompt) > 1024:
        prompt = '[...] ' + prompt[-1024:]
    try:
        r = openai.Completion.create(
            model=OPENAI_MODEL_NAME,
            prompt=prompt,
            temperature=0.6,
            max_tokens=900,
            frequency_penalty=0.1,
            presence_penalty=0.1,
        )
    except Exception as e:
        ret = str(e)
    else:
        try:
            ret = r['choices'][0]['text']
        except:
            ret = r
    logger.info(f"Prompt: {prompt} Response: {ret}")
    return ret

def reply_handler(update: Update, context: CallbackContext):
    """
    Reply to the user with the OpenAI response
    :param update:
    :param context:
    :return:
    """
    print(update)
    try:
        previous_prompt = clean_command_header(update.message.reply_to_message.text)
    except:
        return
    else:
        text = clean_command_header(update.message.text)
        prompt = f"{previous_prompt}\n\n{text}\n\n"
        response = complete_prompt(prompt)
        update.message.reply_text(response)


def complete_handler(update: Update, context: CallbackContext):
    """
    Complete the prompt using OpenAI
    :param update:
    :param context:
    :return:
    """
    text = clean_command_header(update.message.text)
    response = complete_prompt(text)
    update.message.reply_text(response)

def error(update, context):
    """
    Log Errors caused by Updates.
    :param update:
    :param context:
    :return:
    """
    logger.warning(f"{context.error} after update {update}")


def main():
    """
    Start the bot
    :return:
    """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error)

    dispatcher.add_handler(CommandHandler(DEFAULT_BOT_COMMAND, complete_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()