import telebot
import requests
from bs4 import BeautifulSoup
from config import TOKEN, keys
from extensions import Get_Price, ConvertionExeption
from telebot import types

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def handle_help(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("❓ Как начать работу?")
    btn2 = types.KeyboardButton("💰 Доступные валюты")
    btn3 = types.KeyboardButton("🏦 Новости экономики")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Вас приветствует бот для удобной и быстрой конвертации валют',
                     reply_markup=markup)


@bot.message_handler(content_types=['text', ])
def buttons(message: telebot.types.Message):
    texts = ""
    if message.text == "❓ Как начать работу?":
        bot.send_message(message.chat.id, "Для начала работы введите ваш запрос через пробел в формате:"
                                          '\n <Валюта><В какую валюту конвертировать><Количество>'"")
    elif message.text == "🏦 Новости экономики":
        bot.send_message(message.chat.id, news())
    elif message.text == "💰 Доступные валюты":
        for key in keys.keys():
            texts = '\n'.join((texts, key,))
        bot.send_message(message.chat.id, texts)
    elif message.text != "❓ Как начать работу?" or message.text != "💰 Доступные валюты"\
            or message.text != "🏦 Новости экономики":
        convert(message)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    if message.text == '/start' or message.text == '/help':
        handle_help(message)
    else:
        try:
            values = message.text.split(' ')
            if len(values) != 3:
                raise ConvertionExeption('Вы ввели неправильное количество параметров')
            quote, base, amount = values
            total_base = Get_Price.convert(quote, base, amount)
        except ConvertionExeption as e:
            bot.reply_to(message, f'Ошибка пользователя\n{e}')
        except Exception as e:
            bot.reply_to(message, f'Не удалось обработать команду\n{e}')
        else:
            text = f'Цена {amount} {quote} в {base} - {total_base}'
            bot.send_message(message.chat.id, text)




def news():
    base = 'https://lenta.ru/rubrics/economics/companies/'
    html = requests.get(base).content
    soup = BeautifulSoup(html, 'lxml')
    all_links = soup.find('ul', class_='rubric-page__container _subrubric').find_all('a')
    list_ = []
    str_ = ' '
    for item in all_links:
        item_text = item.text
        item_url = "https://lenta.ru" + item.get("href")
        if len(str_) < 1200:
            str_ += f'{item_url} {item_text} '
            list_.append(str_)
        else:
            break
    return str_


bot.polling(none_stop=True)
