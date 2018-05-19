import urllib.request
import re
import requests
from bs4 import BeautifulSoup


class Parser:

    def __init__(self, ref):
        self.site = ref
        self.response = urllib.request.urlopen(ref)
        self.html = self.response.read()
        self.html = self.html.decode('utf-8')
        self.data = BeautifulSoup(requests.get(self.site).text, 'lxml')

    def get_titles(self):
        """
        Парсит заголовки
        :return: заголови, их описание и ссылки
        """
        titles = re.findall(r'<span class="item__title">(.*?)</span>',
                            self.html)
        refs = re.findall(r'<a href="(h.*?)" class="item__link no-injects',
                          self.html)
        description = re.findall(r'<span class="item__text">(.*?)</span>',
                                 self.html, re.DOTALL)
        return titles, description, refs

    def get_time(self):
        """
        :return: время статей
        """
        time = self.data.find_all('span', {'class': "item__info"})
        return time

    def get_paragraphs(self):
        '''
        :return: текст статьи
        '''
        paragraphs = self.data.find_all('p')
        text = ''
        for i in paragraphs:
            text += i.text
        return text

    def get_tags(self):
        """
        :return: теги
        """
        tags = self.data.find_all('a', {'class': "article__tags__link"})
        return tags
