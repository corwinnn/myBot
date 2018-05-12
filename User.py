class User:
    def __init__(self, id):
        self.id = id
        self.status = 'start'
        self.answer = 0
        self.topic_number = -1
        self.articles_refs = None