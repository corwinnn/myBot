import json
from collections import defaultdict
from time import sleep

import requests
from myParser import Parser
from bd import Topic, Article, Tag, db
import dateparser
session = requests.Session()
session.max_redirects = 100
my_site = Parser('https://www.rbc.ru/story/')
titles, description, refs = my_site.get_titles()

while True:
    try:
        db.close()
        db.connect()
        for i in range(len(titles)):
            if len(Topic.select().where(Topic.name == titles[i])) == 0:
                print('new topic')
                all_topic_text = ''
                topic_words_len = defaultdict(int)
                topic_words_freq = defaultdict(int)
                articles = Parser(refs[i])
                times_articles = articles.get_time()
                a_titles, a_description, a_refs = articles.get_titles()
                for j in range(len(a_titles)):
                    print('new article')
                    article_words_len = defaultdict(int)
                    article_words_freq = defaultdict(int)
                    article = Parser(a_refs[j])
                    all_article_text = article.get_paragraphs()
                    all_topic_text += ' ' + all_article_text
                    words = all_article_text.split()
                    for word in words:
                        article_words_freq[word] += 1
                        article_words_len[int(len(word))] += 1
                    new_article = Article(topic=titles[i], name=a_titles[j],
                                          href=a_refs[j],
                                          text=article.get_paragraphs(),
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
                new_topic = Topic(name=titles[i], description=description[i],
                                  href=refs[i],
                                  upd=dateparser.parse(times_articles[0].text),
                                  stat_words_len=json.dumps(topic_words_len),
                                  stat_words_freq=json.dumps(topic_words_freq))
                new_topic.save()
            else:
                cur_topic = Topic.get(Topic.name == titles[i])
                last_upd = cur_topic.upd
                articles = Parser(refs[i])
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
                        words = all_article_text.split()
                        for word in words:
                            article_words_freq[word] += 1
                            article_words_len[len(word)] += 1
                        new_article = Article(topic=titles[i], name=a_titles[j],
                                              href=a_refs[j],
                                              text=article.get_paragraphs(),
                                              upd=dateparser.parse(times_articles[j].text),
                                              stat_words_len=json.dumps(article_words_len),
                                              stat_words_freq=json.dumps(article_words_freq))
                        new_article.save()
                        tags = article.get_tags()
                        for k in tags:
                            new_tag = Tag(name=k.text, article=a_titles[j],
                                          href=k['href'])
                            new_tag.save()
                    else:
                        break
                if have_new:
                    updated_articles = Article.select()\
                                              .where(Article.topic == cur_topic.name)
                    all_topic_text = ''
                    topic_words_len = defaultdict(int)
                    topic_words_freq = defaultdict(int)
                    for article in updated_articles:
                        all_topic_text += ' ' + article.text
                    words = all_topic_text.split()
                    for word in words:
                        topic_words_freq[word] += 1
                        topic_words_len[len(word)] += 1
                    cur_topic.stat_words_len = json.dumps(topic_words_len)
                    cur_topic.stat_words_freq = json.dumps(topic_words_freq)
                    cur_topic.save()
        db.close()
        print('done')
        sleep(0)
    except:
        print('ups')
