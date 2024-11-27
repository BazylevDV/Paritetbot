from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=[
        [KeyboardButton(text="Каталог оборудования"), KeyboardButton(text="Склад на сегодня")],
        [KeyboardButton(text="Успей купить по акции-1"), KeyboardButton(text="Успей купить по акции-2")],
        [KeyboardButton(text="Запросить КП"), KeyboardButton(text="Информация")]
    ])
    return keyboard

def preferred_contact_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мобильная связь", callback_data="mobile_contact")],
        [InlineKeyboardButton(text="Мессенджер", callback_data="messenger")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])
    return keyboard

def messenger_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", callback_data="telegram")],
        [InlineKeyboardButton(text="WhatsApp", callback_data="whatsapp")],
        [InlineKeyboardButton(text="Viber", callback_data="viber")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])
    return keyboard

def manager_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дружинина Татьяна", callback_data="Дружинина Татьяна")],
        [InlineKeyboardButton(text="Ковач Александр", callback_data="Ковач Александр")],
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])
    return keyboard

def back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])
    return keyboard

def reminder_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue")],
        [InlineKeyboardButton(text="Завершить сеанс", callback_data="finish")]
    ])
    return keyboard