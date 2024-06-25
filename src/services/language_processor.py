"""Create a LanguageProcessor class with tools for handling text (menu items).
    """
# Run with python -m src.services.language_processor 
import spacy
import spacy_stanza
import stanza
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class LanguageProcessor:
    """Class to process menu items
    using natural language processing -methods
    """

    def __init__(self):
        self.nlp = None

        self._load_nlp()

    def _load_nlp(self):
        stanza.download(lang="fi")
        self.nlp = spacy_stanza.load_pipeline(name="fi")

    def process(self, item):
        return self.nlp(item)

    def is_date(self, row):
        try:
            pd.to_datetime(row)
            return True
        except:
            return False

    def read_menu(self):
        path = 'src/data/basic_mvp_data/kumpula_menu.xlsx'
        menu_data = pd.read_excel(path)
        menu_data = menu_data.drop([0, 1], axis=0)
        menu_data = menu_data.drop(columns=menu_data.columns[0:-3])
        menu_data.drop(axis='columns', columns='Total.2', inplace=True)
        menu_data.dropna(axis=0, how='all', inplace=True)
        menu_data.rename(columns={menu_data.columns[0]: 'Menu item'}, inplace=True)
        menu_data.rename(columns={menu_data.columns[1]: 'Meals sold'}, inplace=True)
        menu_data.reset_index()

        menu_items = []

        for item in menu_data['Menu item']:
            if not self.is_date(item) and not item == "Total":
                menu_items.append(item)

        return menu_items

    def get_lemmas(self, menulist):
        lemmas = []
        for item in menulist:
            doc = self.nlp(item)
            for token in doc:
                if not token.is_stop and not token.is_punct and not token.is_space:
                    lemmas.append(token.lemma_)
        unique_lemmas = list(set(lemmas))

        return unique_lemmas

    def one_hot(self, lemmas):
        lemma_vectors = {}

        for i, lemma in enumerate(lemmas):
            vector = np.zeros(shape=len(lemmas))
            vector[i] = 1
            lemma_vectors[lemma] = vector

        return lemma_vectors

language_processor = LanguageProcessor()

if __name__ == "__main__":
    lm = LanguageProcessor()
    print(lm.process("kasvoin"))
    menulist = lm.read_menu()
    print(type(menulist))
    print(menulist[1:10])
    lemmas = lm.get_lemmas(menulist)
    print(lemmas)
    vectors = lm.one_hot(lemmas)
    print(list(vectors.items())[1:10])
