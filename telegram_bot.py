from telegram import Update
from telegram.ext.filters import Filters
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                          MessageHandler, ConversationHandler)
import logger
import user_crud
from ai_bot import AIBot
from settings import TOKEN, DEFAULT_TOPIC

CHANGE_TOPIC = 1

log = logger.get_logger('Telegram')


def hello(update: Update, context: CallbackContext) -> None:
    user_name = update.effective_user.first_name
    log.debug(f'User {user_name} send command "/hello"')
    update.message.reply_text(f'Hello {user_name}')


def current_topic(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Your current topic is {user_crud.get_or_create(update.effective_user.id).current_topic}')
    log.debug(f'User {update.effective_user.first_name!r} got current topic.')


def get_bot_response(update: Update, context: CallbackContext) -> None:

    log.debug(f'User {update.effective_user.first_name} asked question.')
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
    log.debug(f'User {update.effective_user.first_name!r} changed topic to: {updated_user.current_topic!r}.')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Good bye')
    log.debug(f'User {update.effective_user.first_name!r} canceled an action')
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
    logger.logger_config(level='DEBUG', root_level='WARNING')

    log.info('Bot has been started... \n Press ctrl + C to STOP the bot')
    updater.start_polling()
    updater.idle()
    log.info('Bot has been started')
