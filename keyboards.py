from pattern import ButtonText

from telegram import ReplyKeyboardMarkup, KeyboardButton


hello_button = KeyboardButton(ButtonText.HELLO.value)
get_topic_btn = KeyboardButton(ButtonText.TOPIC.value)
change_topic_btn = KeyboardButton(ButtonText.CHANGE.value)
cancel_btn = KeyboardButton(ButtonText.CANCEL.value)


keyboard = ReplyKeyboardMarkup([
    [hello_button, get_topic_btn],
    [change_topic_btn],
])

keyboard_only_cancel = ReplyKeyboardMarkup([[cancel_btn]])
