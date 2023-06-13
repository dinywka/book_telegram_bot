import telebot
from telebot import types
import json
import datetime

bot = telebot.TeleBot('6245702932:AAFJ2qQErLLQTiUxANoomO128X-Y2xyaBFc')

ERROR_TEXT = "Произошла ошибка, попробуйте ещё раз или обратитесь к администратору"
DEBUG = False


def decorator_exception_1(func):
    def wrapper(*args, **kwargs):
        message: telebot.types.Message = args[0]
        try:
            func(*args, **kwargs)
        except Exception as error:
            _error = f"error: {error}"
            print(_error)
            with open("lib/books.txt", mode="a", encoding="utf-8") as file:
                file.write(f"[{datetime.datetime.now()}] {error}\n")
            if DEBUG:
                bot.send_message(message.chat.id, _error, parse_mode='html')
            else:
                bot.send_message(message.chat.id, ERROR_TEXT, parse_mode='html')

    return wrapper


# todo КОМАНДА - 'start' - telegram - '/start'
@decorator_exception_1
@bot.message_handler(commands=['start'])
def f_start(message):

    commands = """
<strong>Давай опубликуем новую книгу!</strong>

<b>Ниже список команда с описанием:</b>

<i>Базовые:</i>
/start - начальное меню

<i>Работа с товаром:</i>
/create - создание новой книги

<i>Базовые:</i>
/all - посмотреть весь список

"""
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, commands, parse_mode='html', reply_markup=markup)


@decorator_exception_1
@bot.message_handler(commands=['create'])
def f_sale(message):
    bot.send_message(message.chat.id, """<b>Введите через запятую название, автора и описание книги:</b>""", parse_mode='html')
    bot.register_next_step_handler(message, f_sale_step1)


@decorator_exception_1
def f_sale_step1(message: telebot.types.Message):
    data = message.text.split(",")

    title: str = data[0].strip().capitalize()
    author: str = data[1].strip()
    description: str = data[2].strip()
    print(title, author, description)

    with open("data/items.json", mode="r", encoding="utf-8") as file:
        items: list[dict] = json.load(file)
        items.append({"id": int(items[-1]["id"]) + 1, "title": title, "author": author, "description": description})

    with open("data/items.json", mode="w", encoding="utf-8") as file:
        json.dump(items, file)


@decorator_exception_1
@bot.message_handler(commands=['all'])
def all_books(message):
    try:
        first_mess = f"<b>{message.from_user.first_name}</b>, привет!\nХочешь посмотреть список книг?"
        markup = types.InlineKeyboardMarkup()
        with open("data/items.json", mode="r", encoding="utf-8") as file:
            for item in json.load(file):
                markup.add(types.InlineKeyboardButton(text=f"{item['title']} ({item['author']})", callback_data=str(item['id'])))
        bot.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)
    except Exception as error:
        print("error: ", error)

@bot.callback_query_handler(func=lambda call: True)
def response(function_call):
    try:
        if function_call.message:
            print(function_call.data)
            with open("data/items.json", mode="r", encoding="utf-8") as file:
                for item in json.load(file):
                    if function_call.data == str(item["id"]):
                        markup = types.InlineKeyboardMarkup()
                        bot.send_message(function_call.message.chat.id, f"[{item['id']}] {item['title']} ({item['author']})\n {item['description']}",
                                         parse_mode='html', reply_markup=markup)

            print(function_call.data, type(function_call.data))
            if function_call.data == "yes":

                with open("data/items.json", mode="r", encoding="utf-8") as file:
                    items = json.load(file)
                    # print(items, type(items))

                second_mess = "<b>Вот список товаров:</b>\n\n"
                for item in items:
                    second_mess += f"[{item['id']}] {item['title']} = {item['author']}\n"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Перейти на сайт", url="https://timeweb.cloud/"))
                bot.send_message(function_call.message.chat.id, second_mess, parse_mode='html', reply_markup=markup)
                bot.answer_callback_query(function_call.id)
    except Exception as error:
        print("error: ", error)






if __name__ == "__main__":
    print("bot started...")
    try:
        bot.infinity_polling()
    except Exception as error:
        print("error: ", error)
    print("bot stopped...")