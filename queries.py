from collections import defaultdict

import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bd import Topic, Article, Tag
import peewee
import stop_words
import wordcloud
import config


def make_plot(data, label, xlabel, ylabel, view):
    '''
    Строит график
    :param data: наши данные
    :param label: подпись
    :param xlabel: ось х
    :param ylabel: ось у
    :param view: вид
    :return: график
    '''
    data_frame = pd.DataFrame(data)
    plot = data_frame.plot(kind=view,
                           title=label,
                           colormap='jet')
    plot.set_xlabel(xlabel)
    plot.set_ylabel(ylabel)
    plot.legend_.remove()
    return plot


def new_docs(n):
    '''
    :param n: количество
    :return: n последних статей
    '''
    articles = Article.select()\
        .order_by(-Article.upd)\
        .limit(n)
    return articles


def new_topics(n):
    '''

    :param n: количество
    :return: n последних тем
    '''

    topics = Topic.select()\
        .order_by(-Topic.upd)\
        .limit(n)
    return topics


def topic(topic_name):
    '''
    описание темы
    :param topic_name: название
    :return: описание, последние статьи
    '''
    try:
        desc = Topic.get(Topic.name == topic_name).description
        articles = Article.select()\
            .where(Article.topic == topic_name)\
            .order_by(-Article.upd)\
            .limit(5)
        return desc, articles
    except:
        return None, None


def doc(doc_title):
    '''
    :param doc_title: название статьи
    :return: текст
    '''
    try:
        text = Article.get(Article.name == doc_title).text
        return text
    except:
        return None


def words(topic):
    """
    5 самых важных слов
    :param topic: название темы
    :return: слова
    """
    words = Tag.select()\
        .join(Article, on=(Article.name == Tag.article))\
        .where(Article.topic == topic)\
        .group_by(Tag.name)\
        .order_by(-peewee.fn.count(Tag.name))\
        .limit(10)
    right_words= []
    cur_word = 0
    while cur_word < 10 and len(right_words) < 5:
        isRight = True
        for j in right_words:
            if words[cur_word].name.lower() == j.name.lower():
                isRight = False
        if isRight:
            right_words.append(words[cur_word])
        cur_word += 1

    return right_words


def make_plots(file_name, data_kol, data_freq, data_part, part_type):
    """
    Делает три графика для статистики тем ыили статьи
    :param file_name: базовое название файла
    :param data_kol: данные об длине/количестве
    :param data_freq: данные о частоте
    :param data_part: данные о чаастях объекта
    :param part_type: название части
    :return: названия 3х файлов
    """
    file_name1 = file_name + '1.png'
    file_name2 = file_name + '2.png'
    file_name3 = file_name + '3.png'
    make_plot(data=data_kol,
              label="distribution of the word length",
              xlabel='word\'s length',
              ylabel='Number of words with this length',
              view="bar"
              )
    plt.savefig(file_name1)
    plt.close()
    freq = defaultdict(int)
    for value in data_freq:
        freq[value] += 1
    end_data = [freq[i] for i in range(max(freq.keys()))]
    make_plot(data=end_data,
              label="distribution of the different words",
              xlabel='different words',
              ylabel='Number of these words',
              view="bar"
              )

    plt.savefig(file_name2)
    plt.close()
    make_plot(data=data_part,
              label="distribution of the number words in " + part_type,
              xlabel='sentences',
              ylabel='Number of words',
              view="bar"
              )

    plt.savefig(file_name3)
    plt.close()
    return file_name1, file_name2, file_name3


def describe_doc(doc_name, file_name):
    """
    Cоздает описание файла, статистику
    :param doc_name: имя статьи
    :param file_name: базовое имя файлов с инфографикой
    :return: названия 3х файлов с графиками
    """
    try:
        article = Article.get(Article.name == doc_name)
        article_words_len = json.loads(article.stat_words_len)
        article_words_freq = json.loads(article.stat_words_freq)
        keys = [int(x) for x in article_words_len.keys()]
        len_max = max(keys)
        kol_with_len = [0 for i in range(len_max + 1)]
        for i in range(1, len_max + 1):
            if str(i) in article_words_len.keys():
                kol_with_len[i] = article_words_len[str(i)]
            else:
                kol_with_len[i] = 0
        kol_freq = sorted(article_words_freq.values())
        sentences = article.text.split('.')
        sentences = sentences[:-1]
        sent_len = [len(sent.split()) for sent in sentences]
        return make_plots(file_name, kol_with_len, kol_freq, sent_len, 'sentence')
    except:
        return None, None, None


def describe_topic(topic_name, file_name):
    """
    Cоздает описание темы, статистику
    :param topic_name: название темы
    :param file_name: имя базового файла
    :return: количество статей, их среднюю длину и три графика
    """
    try:
        topic = Topic.get(Topic.name == topic_name)
        topic_words_len = json.loads(topic.stat_words_len)
        topic_words_freq = json.loads(topic.stat_words_freq)
        articles_amount = len(Article.select().where(Article.topic == topic.name))
        articles_len = [len(art.text.split()) for art in Article.select().where(Article.topic == topic.name)]
        aver = sum(articles_len)/len(articles_len)
        keys = [int(x) for x in topic_words_len.keys()]
        len_max = max(keys)
        kol_with_len = [0 for i in range(len_max + 1)]
        for i in range(1, len_max + 1):
            if str(i) in topic_words_len.keys():
                kol_with_len[i] = topic_words_len[str(i)]
            else:
                kol_with_len[i] = 0
        kol_freq = sorted(topic_words_freq.values())
        files = make_plots(file_name, kol_with_len, kol_freq, articles_len, 'articles')
        return articles_amount, aver, files
    except:
        return None, None, None, None, None


def beautiful(topic_name, file_name):
    """
    Делает красивую картинку из главныз слов темы
    :param topic_name: название темы
    :param file_name: название выходного файла
    :return: True или False, в зависимости от того, получилось ли сделать картинку
    """
    tags = Tag.select() \
        .join(Article, on=(Article.name == Tag.article)) \
        .where(Article.topic == topic_name) \
        .group_by(Tag.name) \
        .order_by(-peewee.fn.count(Tag.name)) \
        .limit(config.WORDS_IN_WORDCLOUD)
    if len(tags) == 0:
        return False
    text = ' '.join(word.name for word in tags)
    stopwords = set(stop_words.get_stop_words('ru'))
    word_cloud = wordcloud.WordCloud(max_words=config.WORDS_IN_WORDCLOUD,
                                     height=config.WORDCLOUD_HEIGHT,
                                     width=config.WORDCLOUD_WIDTH,
                                     background_color='white',
                                     stopwords=stopwords).generate(text)

    image = word_cloud.to_image()
    image.save(file_name)
    return True


def guess(text):
    """
    По данному тексту находит предполагаемую статью
    :param text: текст
    :return: название темы
    """
    words = text.split()
    name_of_topic = 'I don\'t know'
    cur_grade = 0
    topics = Topic.select()
    for topic in topics:
        grade = 0
        topic_words = json.loads(topic.stat_words_freq)
        for word in words:
            if word in topic_words:
                grade += 1/topic_words[word]
        if grade > cur_grade:
            cur_grade = grade
            name_of_topic = topic.name
    return name_of_topic



