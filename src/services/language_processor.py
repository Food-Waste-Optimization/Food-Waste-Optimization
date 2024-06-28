"""Create a LanguageProcessor class with tools for handling text (menu items).
    """
# Run with python -m src.services.language_processor from root dir
import spacy_stanza
import stanza
import pandas as pd
import numpy as np
from ..repositories.db_repository import DatabaseRepository

class LanguageProcessor:
    """Class to process menu items
    using natural language processing -methods
    """

    def __init__(self):
        self.nlp = None

        self._load_nlp()

    def _load_nlp(self):
        """Load language model.
        """
        stanza.download(lang="fi")
        self.nlp = spacy_stanza.load_pipeline(name="fi", processors="tokenize,lemma")

    def get_lemmas(self, menulist):
        """Divides strings into unique lemmas.

        Args:
            menulist (list): List of strings (Menu items)

        Returns:
            list: List of unique lemmas
        """
        lemmas = []
        for item in menulist:
            doc = self.nlp(item)
            for token in doc:
                if not token.is_stop and not token.is_punct and not token.is_space:
                    lemmas.append(token.lemma_)
                    #print(token.lemma_, flush=True)
        unique_lemmas = list(set(lemmas))
        return unique_lemmas

    def process_learn(self, input_list):
        """Encodes menu items based on lemmas and saves them to database. Run seldom (slow).

        Args:
            input_list (list): List of strings (Menu items)

        Returns:
            list: Corresponding list of one-hot-encodings (lists of ones and zeroes)
        """

        db = DatabaseRepository()
        lemmas = self.get_lemmas(input_list)

        one_hot_encoded_list = []
        encoding_data = []

        lemma_to_index = {lemma: idx for idx, lemma in enumerate(lemmas)}

        for item in input_list:
            item_vector = np.zeros(len(lemmas))
            doc = self.nlp(item)
            item_lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
            for lemma in item_lemmas:
                if lemma in lemmas:
                    idx = lemmas.index(lemma)
                    item_vector[idx] = 1
            one_hot_encoded_list.append(item_vector.tolist())

        for lemma, idx in lemma_to_index.items():
            one_hot_vector = np.zeros(len(lemmas), dtype=int)
            one_hot_vector[idx] = 1
            encoding_data.append({'lemma': lemma, 'encoding': one_hot_vector.tolist()})

        encoding_df = pd.DataFrame(encoding_data)
        encoding_df.set_index('lemma', inplace=True)
        print(encoding_df.head(10))
        db.insert_nlp_encoding(encoding_df)

        return one_hot_encoded_list

    def process(self, input_list):
        """ Work in Progress
            Divide input_list into lemmas
            fetch corresponding one-hot-encodings from database
            return list of encoded dishes

        Args:
            input_list (list): List of strings (Menu items) Recommended maximum: 7 items
        Returns:
            list: Corresponding list of one-hot-encodings (lists of ones and zeroes)
        """
        db = DatabaseRepository()
        lemmas = self.get_lemmas(input_list)
        one_hot_encoded_list = []

        for item in input_list:
            doc = self.nlp(item)
            item_lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]

            for lemma in item_lemmas:
                lemma_encoding = db.get_nlp_encoding(lemma)
                lemma_encoding = lemma_encoding.values.tolist()

                if lemma in lemmas:
                    one_hot_encoded_list.append(lemma_encoding)

        return one_hot_encoded_list


language_processor = LanguageProcessor()

if __name__ == "__main__":
    lm = LanguageProcessor()
    testlist = ["Kalapyörykät", "Kala, take-away", "Uunimakkara", "Kasviskorma", "Haukipyörykkä", "Paneroidut lohipihvit ja yrttikastiketta"]
    encoded = lm.process_learn(testlist)
    print(encoded)
    print(len(testlist), len(encoded))
