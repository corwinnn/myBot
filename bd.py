from peewee import *
db = SqliteDatabase('wee.db')


class Topic(Model):
    name = CharField()
    href = CharField()
    description = CharField()
    upd = DateTimeField()
    stat_words_len = CharField()
    stat_words_freq = CharField()

    class Meta:
        database = db


class Article(Model):
    topic = CharField()
    name = CharField()
    href = CharField()
    upd = DateTimeField()
    text = CharField()
    stat_words_len = CharField()
    stat_words_freq = CharField()

    class Meta:
        database = db


class Tag(Model):
    article = CharField()
    name = CharField()
    href = CharField()

    class Meta:
        database = db


db.create_tables([Topic, Article, Tag])
db.close()
