import json
import re
from database import queries
import config
import telebot
from User import User


users = dict()
bot = telebot.TeleBot(config.token)

with open('botCommands.json') as bot_activity_file:
    bot_activity = json.loads(bot_activity_file.read())


def setUser(id):
    if id not in users:
        users[id] = User(id)


@bot.message_handler(commands=['start', 'help', 'stop'])
def handle_start_help_stop(message):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)
    bot.send_message(message.chat.id, bot_activity['commands'][message.text])
    users[message.chat.id].status = 'start'


@bot.message_handler(commands=['new_docs'])
def new_docs(message):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)
    users[message.chat.id].status = 'new_docs'
    bot.send_message(message.chat.id, 'How many?')


@bot.message_handler(content_types=['text'])
def get_message(message):
    print(message.text, message.chat.first_name, message.chat.last_name)
    if users[message.chat.id].status == 'start':
        bot.send_message(message.chat.id, 'What do you want? Use commands, please.')
    if users[message.chat.id].status == 'new_docs':
        s = message.text
        number = int(s)
        print(number, type(number))
        articles = queries.new_docs(number)
        print('oe')
        print(len(articles))
        for a in articles:
            bot.send_message(message.chat.id, a.name, a.href)
        users[message.chat.id].status = 'start'



''''@bot.message_handler(commands=['get_articles_from_title'])
def get_articles(message):
    setUser(message.chat.id)
    print(message.text, message.chat.first_name, message.chat.last_name)
    users[message.chat.id].status = 'read_number_topic'
    bot.send_message(message.chat.id, 'Which topic?')


@bot.message_handler(content_types=['text'])
def repeat_message(message):
    print(message.text, message.chat.first_name, message.chat.last_name)
    setUser(message.chat.id)
    if users[message.chat.id].status == 'start':
        s = message.text[:100]
        bot.send_message(message.chat.id, 'ok')
    elif users[message.chat.id].status == 'read_number' or users[message.chat.id].status == 'read_number_topic' or users[message.chat.id].status == 'read_number_of_articles':
        s = message.text
        this_topics = ('', '', '')
        times_articles = ''
        try:
            info = parser.get_titles()
            if users[message.chat.id].topic_number != -1:
                this_topics = Parser(info[2][users[message.chat.id].topic_number - 1]).get_titles()
                times_articles = Parser(info[2][users[message.chat.id].topic_number - 1]).get_time()
            if users[message.chat.id].status != 'read_number_topic' and (s == 'all' or s == 'All'):
                s = str(len(info[0]))
            if users[message.chat.id].status == 'read_number':
                number = min(int(s), len(info[0]))
            if users[message.chat.id].status == 'read_number_topic':
                number = min(int(s), len(info[0]))
            if users[message.chat.id].status == 'read_number_of_articles':
                number = min(int(s), len(this_topics[0]))
            if int(s) < 0:
                raise ValueError
            if users[message.chat.id].status == 'read_number':
                for i in range(number):
                    bot.send_message(message.chat.id, str(i+1) + '. ' + info[0][i] + '\n' + info[1][i] + '\n' + info[2][i])
                users[message.chat.id].status = 'start'
            elif users[message.chat.id].status == 'read_number_topic':
                users[message.chat.id].topic_number = number
                users[message.chat.id].status = 'read_number_of_articles'
                bot.send_message(message.chat.id, 'How many?')
            elif users[message.chat.id].status == 'read_number_of_articles':
                for i in range(number):
                    bot.send_message(message.chat.id, str(i+1) + '. ' + times_articles[i].text + '\n' + this_topics[0][i] + '\n' + this_topics[1][i] + '\n' + this_topics[2][i])
                users[message.chat.id].articles_refs = this_topics[2]
                bot.send_message(message.chat.id, 'Want to read something? List numbers, separated by commas')
                users[message.chat.id].status = 'read_articles'
        except ValueError:
            bot.send_message(message.chat.id, 'Try again, please ')
    elif users[message.chat.id].status == 'read_articles':
        s = re.sub(' ', '', message.text).split(',')
        print(s)
        try:
            for i in s:
                ind = int(i)
                if ind > len(users[message.chat.id].articles_refs):
                    raise ValueError
                text = ''
                article = Parser(users[message.chat.id].articles_refs[ind]).get_paragraphs()
                for paragraph in article:
                    text += paragraph.text
                bot.send_message(message.chat.id, text)
                users[message.chat.id].status = 'start'

        except ValueError:
            bot.send_message(message.chat.id, 'Try again, please')


'''

if __name__ == '__main__':
    bot.polling(none_stop=True)
