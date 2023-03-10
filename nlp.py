import spacy
from spacy.language import Language


class LazyNlp:
    _nlp: Language | None = None
    _nlp_type: str
    _treshold: float

    def __init__(self, nlp_type: str, treshold=0.7) -> None:
        self._nlp_type = nlp_type
        self._treshold = treshold

    def get_nlp(self):
        if self._nlp is None:
            self._nlp = spacy.load(self._nlp_type)
        return self._nlp

    @property
    def nlp(self):
        return self.get_nlp()

    def compare_texts(self, t1: str, t2: str) -> float:
        s1 = self.nlp(t1)
        s2 = self.nlp(t2)
        return s1.similarity(s2)

    def is_text_same(self, t1: str, t2: str):
        similarity = self.compare_texts(t1, t2)
        if similarity > self._treshold:
            print(similarity, 't1:', t1, 't2:', t2)
        return similarity > self._treshold
