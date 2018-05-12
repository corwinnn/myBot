from collections import defaultdict
import json
import requests
from database.myParser import Parser
from database.bd import Topic, Article, Tag, db
import dateparser
session = requests.Session()
session.max_redirects = 100
my_site = Parser('https://www.rbc.ru/story/')
titles, description, refs = my_site.get_titles()
all_titles = set(titles)
db.connect()
for i in range(len(titles)):
    all_topic_text = ''
    topic_words_len = defaultdict(int)
    topic_words_freq = defaultdict(int)
    articles = Parser(refs[i])
    times_articles = articles.get_time()
    a_titles, a_description, a_refs = articles.get_titles()
    for j in range(len(a_titles)):
        article_words_len = defaultdict(int)
        article_words_freq = defaultdict(int)
        article = Parser(a_refs[j])
        all_article_text = article.get_paragraphs()
        all_topic_text += ' ' + all_article_text
        words = all_article_text.split()
        for word in words:
            article_words_freq[word] += 1
            article_words_len[int(len(word))] += 1
        new_article = Article(topic=titles[i], name=a_titles[j], href=a_refs[j], text=article.get_paragraphs(),
                              upd=dateparser.parse(times_articles[j].text),
                              stat_words_len=json.dumps(article_words_len),
                              stat_words_freq=json.dumps(article_words_freq))
        new_article.save()
        tags = article.get_tags()
        for k in tags:
            new_tag = Tag(name=k.text, article=a_titles[j], href=k['href'])
            new_tag.save()
    words = all_topic_text.split()
    for word in words:
        topic_words_freq[word] += 1
        topic_words_len[int(len(word))] += 1
    new_topic = Topic(name=titles[i], description=description[i], href=refs[i],
                      upd=dateparser.parse(times_articles[0].text),stat_words_len=json.dumps(topic_words_len),
                      stat_words_freq=json.dumps(topic_words_freq))
    new_topic.save()
db.close()