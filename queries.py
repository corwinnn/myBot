import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bd import Topic, Article, Tag
import peewee
import stop_words
import wordcloud


def make_plot(data, label, xlabel, ylabel, view):
    data_frame = pd.DataFrame(data)
    plot = data_frame.plot(kind=view,
                           title=label,
                           colormap='jet')
    plot.set_xlabel(xlabel)
    plot.set_ylabel(ylabel)
    return plot


def new_docs(n):
    articles = Article.select()\
        .order_by(-Article.upd)\
        .limit(n)
    return articles


def new_topics(n):
    topics = Topic.select()\
        .order_by(-Topic.upd)\
        .limit(n)
    return topics


def topic(topic_name):
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
    try:
        text = Article.get(Article.name == doc_title).text
        return text
    except:
        return None


def words(topic):
    words = Tag.select()\
        .join(Article, on=(Article.name == Tag.article))\
        .where(Article.topic == topic)\
        .group_by(Tag.name)\
        .order_by(-peewee.fn.count(Tag.name))\
        .limit(5)
    return words


def describe_doc(doc_name, file_name):
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
        file_name1 = file_name + '1.png'
        file_name2 = file_name + '2.png'
        file_name3 = file_name + '3.png'
        make_plot(data=kol_with_len,
                  label="distribution of the word length",
                  xlabel='word\'s length',
                  ylabel='Number of words with this length',
                  view="bar"
                  )
        plt.savefig(file_name1)
        plt.close()
        make_plot(data=kol_freq,
                  label="distribution of the different words",
                  xlabel='different words',
                  ylabel='Number of these words',
                  view="line"
                  )

        plt.savefig(file_name2)
        plt.close()
        make_plot(data=sent_len,
                  label="distribution of the number words in sentence",
                  xlabel='sentences',
                  ylabel='Number of words',
                  view="line"
                  )

        plt.savefig(file_name3)
        plt.close()
        return file_name1, file_name2, file_name3
    except:
        return None, None, None


def describe_topic(topic_name, file_name):
    try:
        topic = Topic.get(Topic.name == topic_name)
        topic_words_len = json.loads(topic.stat_words_len)
        topic_words_freq = json.loads(topic.stat_words_freq)
        articles_amount= len(Article.select().where(Article.topic == topic.name))
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
        file_name1 = file_name + '1.png'
        file_name2 = file_name + '2.png'
        file_name3 = file_name + '3.png'
        make_plot(data=kol_with_len,
                  label="distribution of the word length",
                  xlabel='word\'s length',
                  ylabel='Number of words with this length',
                  view="bar"
                  )
        plt.savefig(file_name1)
        plt.close()
        make_plot(data=kol_freq,
                  label="distribution of the different words",
                  xlabel='different words',
                  ylabel='Number of these words',
                  view="line"
                  )

        plt.savefig(file_name2)
        plt.close()
        make_plot(data=articles_len,
                  label="distribution of the number words in articles",
                  xlabel='Articles',
                  ylabel='Number of words',
                  view="line"
                  )

        plt.savefig(file_name3)
        plt.close()
        return articles_amount, aver, file_name1, file_name2, file_name3
    except:
        return None, None, None, None, None


def beautiful(topic_name):
    words = Tag.select() \
        .join(Article, on=(Article.name == Tag.article)) \
        .where(Article.topic == topic) \
        .group_by(Tag.name) \
        .order_by(-peewee.fn.count(Tag.name)) \
        .limit(50)
    text = ' '.join(word.name for word in words)
    stopwords = set(stop_words.get_stop_words('ru'))
    word_cloud = wordcloud.WordCloud(max_words=50,
                                     height=800,
                                     width=800,
                                     background_color='white',
                                     stopwords=stopwords).generate(text)

    image = word_cloud.to_image()
    image.save('image.png')
