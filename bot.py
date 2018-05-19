import json
import re
import queries
import config
import telebot
from User import User


users = dict()
bot = telebot.TeleBot(config.token)
commands = dict()

with open('botCommands.json') as bot_activity_file:
    bot_activity = json.loads(bot_activity_file.read())


def setUser(id):
    if id not in users:
        users[id] = User(id)


def get_info_from_user(message, status, answer):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)
    users[message.chat.id].status = status
    bot.send_message(message.chat.id, answer)

def new_docs(message):
    user_text = message.text
    if user_text.isdigit():
        number = int(user_text)
        if number > 0:
            articles = queries.new_docs(number)
            for a in articles:
                bot.send_message(message.chat.id, a.name + '\n' + a.href)
        users[message.chat.id].status = 'start'
    else:
        bot.send_message(message.chat.id, 'Try again, please.')

commands['new_docs'] = new_docs()

@bot.message_handler(commands=['start', 'help', 'stop'])
def handle_start_help_stop(message):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)
    bot.send_message(message.chat.id, bot_activity['commands'][message.text])
    users[message.chat.id].status = 'start'


@bot.message_handler(commands=['new_docs'])
def new_docs(message):
    get_info_from_user(message, 'new_docs', 'How many? Send me the number.')


@bot.message_handler(commands=['new_topics'])
def new_topics(message):
    get_info_from_user(message, 'new_topic', 'How many? Send me the number.')


@bot.message_handler(commands=['topic'])
def topic(message):
    get_info_from_user(message, 'topic', 'Which topic? Send me a name.')


@bot.message_handler(commands=['doc'])
def doc(message):
    get_info_from_user(message, 'doc', 'Which article? Send me a name.')


@bot.message_handler(commands=['words'])
def words(message):
    get_info_from_user(message, 'words', 'Which topic? Send me a name.')


@bot.message_handler(commands=['describe_doc'])
def describe_doc(message):
    get_info_from_user(message, 'describe_doc', 'Which article? Send me a name.')


@bot.message_handler(commands=['describe_topic'])
def describe_topic(message):
    get_info_from_user(message, 'describe_doc', 'Which topic? Send me a name.')


@bot.message_handler(commands=['beautiful_topic'])
def beautiful_topic(message):
    get_info_from_user(message, 'beautiful_topic', 'Which topic? Send me a name.')


@bot.message_handler(content_types=['text'])
def get_message(message):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)

    if users[message.chat.id].status == 'start':
        bot.send_message(message.chat.id, 'Use commands, please.')

    if users[message.chat.id].status == 'new_docs':
        commands['new_docs'](message)


    if users[message.chat.id].status == 'new_topics':
        user_text = message.text
        if user_text.isdigit():
            number = int(user_text)
            if number > 0:
                topics = queries.new_topics(number)
                for t in topics:
                    bot.send_message(message.chat.id, t.name + '\n' + t.href)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')

    if users[message.chat.id].status == 'topic':
        user_text = message.text
        desc, art = queries.topic(user_text)
        if desc is not None:
            bot.send_message(message.chat.id, desc)
            for a in art:
                bot.send_message(message.chat.id, a.name + '\n' + a.href)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')

    if users[message.chat.id].status == 'doc':
        user_text = message.text
        text = queries.doc(user_text)
        if text is not None:
            bot.send_message(message.chat.id, text)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')

    if users[message.chat.id].status == 'words':
        user_text = message.text
        words = queries.words(user_text)
        if len(words) == 0:
            bot.send_message(message.chat.id, 'Try again, please.')
        else:
            for word in words:
                bot.send_message(message.chat.id, word.name)
            users[message.chat.id].status = 'start'

    if users[message.chat.id].status == 'describe_doc':
        user_text = message.text
        files = queries.describe_doc(user_text, 'doc' + str(message.chat.id))
        if files[0] is not None:
            with open(files[0], 'rb') as plot1:
                bot.send_photo(message.chat.id, plot1)
            with open(files[1], 'rb') as plot2:
                bot.send_photo(message.chat.id, plot2)
            with open(files[2], 'rb') as plot3:
                bot.send_photo(message.chat.id, plot3)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')

    if users[message.chat.id].status == 'describe_topic':
        user_text = message.text
        files = queries.describe_topic(user_text, 'top' + str(message.chat.id))
        img_files = files[2]
        if files[0] is not None:
            bot.send_message(message.chat.id, str(files[0]) + ' articles' + '\n' + str(files[1]) + ' words in the article on average')
            with open(img_files[0], 'rb') as plot1:
                bot.send_photo(message.chat.id, plot1)
            with open(img_files[1], 'rb') as plot2:
                bot.send_photo(message.chat.id, plot2)
            with open(img_files[2], 'rb') as plot3:
                bot.send_photo(message.chat.id, plot3)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')

    if users[message.chat.id].status == 'beautiful_topic':
        user_text = message.text
        isBeautifuled = queries.beautiful(user_text, 'awesome' + str(message.chat.id) + '.png')
        if isBeautifuled:
            with open('awesome' + str(message.chat.id) + '.png', 'rb') as btf:
                bot.send_photo(message.chat.id, btf)
            users[message.chat.id].status = 'start'
        else:
            bot.send_message(message.chat.id, 'Try again, please.')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            pass
