import nltk
import numpy as np


class TextProcessor:
    def __init__(self):
        self._nltk = nltk
        self._nltk.download('punkt', quiet=True)
        self._nltk.download('averaged_perceptron_tagger', quiet=True)
        self._nltk.download('maxent_ne_chunker', quiet=True)
        self._nltk.download('words', quiet=True)
        self._nltk.download('stopwords', quiet=True)
        self._nltk.download('wordnet', quiet=True)
        self._nltk.download('vader_lexicon', quiet=True)
        self._nltk.download('omw', quiet=True)
        self._nltk.download('universal_tagset', quiet=True)

    def tokenize(self, text) -> list[str]:
        return self._nltk.word_tokenize(text)

    def clean_text(self, tokens: list[str]) -> list[str]:
        # lowercase and remove punctuation
        tokens = [word.lower() for word in tokens]
        tokens = [word for word in tokens if word.isalnum()]
        # remove stopwords
        stop_words = set(self._nltk.corpus.stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        return tokens

    def lemmatize(self, tokens: list[str]) -> list[str]:
        lemmatizer = self._nltk.stem.WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tokens]

    def pos_tag(self, tokens: list[str]) -> list[tuple[str, str]]:
        return self._nltk.pos_tag(tokens, tagset='universal')


if __name__ == "__main__":
    processor = TextProcessor()
    text = (
        "I wanted to share the talks from last month’s dask demo day, where folks from the dask community give short "
        "demos to show off ongoing work. hopefully this helps elevate some of the great work people are doing.  last "
        "month's talks:) \n- one trillion row challenge \n- deploy dask on databricks with dask-databricks \n- deploy "
        "prefect workflows on the cloud with coiled  \n- scale embedding pipelines (llamaindex + dask)  \n- use aws "
        "cost explorer to see the cost of public ipv4 addresses  \nrecording on youtube: "
        "https://www.youtube.com/watch?v=07e1jl83ur8  join the next one this thursday, march 21st, "
        "11am et https://github.com/dask/community/issues/307"
    )
    tokens = processor.tokenize(text)
    print(tokens)
    cleaned = processor.clean_text(tokens)
    print(cleaned)
    lemmatized = processor.lemmatize(cleaned)
    print(lemmatized)
    pos_tagged = processor.pos_tag(lemmatized)
    print(pos_tagged)
    print("done")
