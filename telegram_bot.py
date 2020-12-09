from telegram import Update
from telegram.ext.filters import Filters
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                          MessageHandler, ConversationHandler)

import user_crud
from ai_bot import AIBot
from settings import TOKEN, DEFAULT_TOPIC

CHANGE_TOPIC = 1


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def current_topic(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Your current topic is {user_crud.get_or_create(update.effective_user.id).current_topic}')


def get_bot_response(update: Update, context: CallbackContext) -> None:
    user = user_crud.get_or_create(update.effective_user.id)
    bot = AIBot(user.current_topic)
    user_input = update.message.text
    update.message.reply_text(bot.generate_response(user_input))


def start_change_topic(update: Update, context: CallbackContext):
    update.message.reply_text('Enter new topic:')
    return CHANGE_TOPIC


def change_topic(update: Update, context: CallbackContext) -> None:
    user = user_crud.get_or_create(update.effective_user.id)
    topic = update.message.text
    updated_user = user_crud.update(user.id, topic)
    update.message.reply_text(f'Topic has been changed to {updated_user.current_topic!r}')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Good bye')
    return ConversationHandler.END


updater = Updater(TOKEN)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('change_topic', start_change_topic)],
    states={
        CHANGE_TOPIC: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, change_topic)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('current_t', current_topic))
updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_bot_response))


if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
