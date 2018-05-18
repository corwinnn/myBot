from collections import defaultdict
import json
import requests
from myParser import Parser
from bd import Topic, Article, Tag, db
import dateparser
import config
session = requests.Session()
session.max_redirects = config.MAX_REDIRECTS
my_site = Parser(config.MY_SITE)
titles, description, refs = my_site.get_titles()
all_titles = set(titles)
db.connect()


def make_tags(tags, title):
    """
    Заполняет таблицу с тегами.
    :param tags: лист тегов
    :param title: статья, откуда мы взяли теги
    """
    for tag in tags:
        new_tag = Tag(name=tag.text, article=title, href=tag['href'])
        new_tag.save()


def fill_words(text, words_freq, words_len):
    """
    Заполняет данные словари для статистики словами
    :param text: слова
    :param words_freq: словарь частоты
    :param words_len: словарь длины
    :return:
    """
    for word in text:
        words_freq[word] += 1
        words_len[int(len(word))] += 1


def make_topic(ref, title, desc):
    """
    Добавляет новую тему в таблицу
    :param ref: ссылка
    :param title: название
    :param desc: описание
    """
    print('new topic')
    all_topic_text = ''
    topic_words_len = defaultdict(int)
    topic_words_freq = defaultdict(int)
    articles = Parser(ref)
    times_articles = articles.get_time()
    a_titles, a_description, a_refs = articles.get_titles()
    for j in range(len(a_titles)):
        print('new article')
        article_words_len = defaultdict(int)
        article_words_freq = defaultdict(int)
        article = Parser(a_refs[j])
        all_article_text = article.get_paragraphs()
        all_topic_text += ' ' + all_article_text
        fill_words(all_article_text.split(), article_words_freq, article_words_len)
        new_article = Article(topic=title, name=a_titles[j],
                              href=a_refs[j],
                              text=article.get_paragraphs(),
                              upd=dateparser.parse(times_articles[j].text),
                              stat_words_len=json.dumps(article_words_len),
                              stat_words_freq=json.dumps(article_words_freq))
        new_article.save()
        make_tags(article.get_tags(), a_titles[j])
    fill_words(all_topic_text.split(), topic_words_freq, topic_words_len)
    new_topic = Topic(name=title, description=desc, href=ref,
                      upd=dateparser.parse(times_articles[0].text),
                      stat_words_len=json.dumps(topic_words_len),
                      stat_words_freq=json.dumps(topic_words_freq))
    new_topic.save()


for index in range(len(titles)):
    make_topic(refs[index], titles[index], description[index])

db.close()
