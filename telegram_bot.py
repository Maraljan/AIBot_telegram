import random

import nltk
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    ConversationHandler,
)
from telegram.ext.filters import Filters

import keyboards
import logger
import user_crud
from ai_bot import AIBot
from pattern import ButtonPattern
from settings import TOKEN

CHANGE_TOPIC = 1

GREETINGS = [
    'hi',
    'hello',
    'hey',
    'hola',
    'salam',
]

log = logger.get_logger('Telegram')


def is_greeting(user_input: str) -> bool:
    for word in user_input.split():
        if word in GREETINGS:
            return True
    return False


def hello(update: Update, context: CallbackContext) -> None:
    user_name = update.effective_user.first_name
    log.debug(f'User {user_name} send command "/hello"')
    update.message.reply_text(f'Hello {user_name}. I can answer to your questions.\n'
                              f'Use command /change_topic to change topic. '
                              f'For example: tennis, sport, math...',
                              reply_markup=keyboards.keyboard)


def current_topic(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'we are talking about {user_crud.get_or_create(update.effective_user.id).current_topic}')
    log.debug(f'User {update.effective_user.first_name!r} got current topic.')


def get_bot_response(update: Update, context: CallbackContext) -> None:

    user_input = update.message.text

    if is_greeting(user_input):
        update.message.reply_text(f'{random.choice(GREETINGS)} {update.effective_user.first_name}')
        return

    log.debug(f'User {update.effective_user.first_name} asked question.')
    user = user_crud.get_or_create(update.effective_user.id)
    bot = AIBot(user.current_topic)
    update.message.reply_text(bot.generate_response(user_input))


def start_change_topic(update: Update, context: CallbackContext):
    update.message.reply_text(
        'About what do you want to talk?',
        reply_markup=keyboards.keyboard_only_cancel
    )
    return CHANGE_TOPIC


def _download_nltk_resources():
    nltk.download('punkt')
    nltk.download('wordnet')


def change_topic(update: Update, context: CallbackContext) -> None:
    user = user_crud.get_or_create(update.effective_user.id)
    topic = update.message.text
    updated_user = user_crud.update(user.id, topic)
    update.message.reply_text(
        f'OK, let`s talk about {updated_user.current_topic!r}',
        reply_markup=keyboards.keyboard,
    )
    log.debug(f'User {update.effective_user.first_name!r} changed topic to: {updated_user.current_topic!r}.')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'ok, no problem',
        reply_markup=keyboards.keyboard,
    )
    log.debug(f'User {update.effective_user.first_name!r} canceled an action')
    return ConversationHandler.END


updater = Updater(TOKEN)

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('change_topic', start_change_topic),
        MessageHandler(Filters.regex(ButtonPattern.CHANGE.value), start_change_topic)
    ],
    states={
        CHANGE_TOPIC: [
            CommandHandler('cancel', cancel),
            MessageHandler(Filters.regex(ButtonPattern.CANCEL.value), cancel),
            MessageHandler(Filters.text, change_topic)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel),
        MessageHandler(Filters.regex(ButtonPattern.CANCEL.value), cancel),
    ]
)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('start', hello))
updater.dispatcher.add_handler(CommandHandler('current_topic', current_topic))

updater.dispatcher.add_handler(MessageHandler(Filters.regex(ButtonPattern.HELLO.value), hello))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(ButtonPattern.TOPIC.value), current_topic))

updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_bot_response))


if __name__ == '__main__':
    _download_nltk_resources()
    logger.logger_config(level='DEBUG', root_level='WARNING')

    log.info('Bot has been started... \n Press ctrl + C to STOP the bot')
    updater.start_polling()
    updater.idle()
    log.info('Bot has been started')
