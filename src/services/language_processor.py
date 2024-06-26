"""Create a LanguageProcessor class with tools for handling text (menu items).
    """
# Run with python -m src.services.language_processor from root dir
import spacy
import spacy_stanza
import stanza
import pandas as pd
import numpy as np

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
        self.nlp = spacy_stanza.load_pipeline(name="fi")

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
        print(unique_lemmas)
        return unique_lemmas

    def process_learn(self, input_list):
        """Encodes menu items based on lemmas. Run seldom (slow).

        Args:
            input_list (list): List of strings (Menu items)

        Returns:
            list: Corresponding list of one-hot-encodings (lists of ones and zeroes)
        """

        lemmas = self.get_lemmas(input_list)

        one_hot_encoded_list = []

        for item in input_list:
            item_vector = np.zeros(len(lemmas))
            doc = self.nlp(item)
            item_lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
            for lemma in item_lemmas:
                if lemma in lemmas:
                    idx = lemmas.index(lemma)
                    item_vector[idx] = 1
            one_hot_encoded_list.append(item_vector.tolist())

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
        lemmas = self.get_lemmas(input_list)
        one_hot_encoded_list = []

        # For item in input_list:
        #   doc = self.nlp(item)
        #   item_lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]

        #   Fetch corresponding one-hot-encoding from PSQL
        #   item_encoding = fetch_encoding_from_db(item_lemmas)

        #   if all(lemma in lemmas for lemma in item_lemmas):
        #       Append encoding to one_hot_encoded_list
        #       one_hot_encoded_list.append(item_encoding)

        return one_hot_encoded_list


language_processor = LanguageProcessor()

if __name__ == "__main__":
    lm = LanguageProcessor()
    testlist = ["Kalapyörykät", "Kala, take-away", "Uunimakkara", "Kasviskorma", "Haukipyörykkä", "Paneroidut lohipihvit ja yrttikastiketta"]
    encoded = lm.process_learn(testlist)
    print(encoded)
    print(len(testlist), len(encoded))
