import json
from collections import defaultdict
from time import sleep

import requests
import config
from myParser import Parser
from bd import Topic, Article, Tag, db
from bdFill import make_topic, titles, description, refs, fill_words, make_tags
import dateparser
session = requests.Session()
session.max_redirects = config.MAX_REDIRECTS

def update_topic_stat(topic, articles):
    """
    Обновляет статистику данной темы, по новым статьям
    :param topic: Тема
    :param articles: новые статьи
    """
    all_topic_text = ''
    topic_words_len = defaultdict(int)
    topic_words_freq = defaultdict(int)
    for article in articles:
        all_topic_text += ' ' + article.text
    fill_words(all_topic_text.split(), topic_words_freq, topic_words_len)
    topic.stat_words_len = json.dumps(topic_words_len)
    topic.stat_words_freq = json.dumps(topic_words_freq)
    topic.save()



while True:
    try:
        db.close()
        db.connect()
        for index in range(len(titles)):
            if len(Topic.select().where(Topic.name == titles[index])) == 0:
                make_topic(refs[index], titles[index], description[index])
            else:
                cur_topic = Topic.get(Topic.name == titles[index])
                last_upd = cur_topic.upd
                articles = Parser(refs[index])
                times_articles = articles.get_time()
                cur_topic.upd = dateparser.parse(times_articles[0].text)
                cur_topic.save()
                a_titles, a_description, a_refs = articles.get_titles()
                have_new = False
                for j in range(len(times_articles)):
                    if dateparser.parse(times_articles[j].text) > last_upd:
                        have_new = True
                        print('new article')
                        article = Parser(a_refs[j])
                        article_words_len = defaultdict(int)
                        article_words_freq = defaultdict(int)
                        all_article_text = article.get_paragraphs()
                        fill_words(all_article_text.split(), article_words_freq, article_words_len)
                        new_article = Article(topic=titles[index], name=a_titles[j],
                                              href=a_refs[j],
                                              text=article.get_paragraphs(),
                                              upd=dateparser.parse(times_articles[j].text),
                                              stat_words_len=json.dumps(article_words_len),
                                              stat_words_freq=json.dumps(article_words_freq))
                        new_article.save()
                        make_tags(article.get_tags(), a_titles[j])
                    else:
                        break
                if have_new:
                    updated_articles = Article.select()\
                                              .where(Article.topic == cur_topic.name)
                    update_topic_stat(cur_topic, updated_articles)

        db.close()
        print('done')
        sleep(1000)
    except:
        print('ups')
