import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from spacy import displacy
from spacy.tokens import Span
import re

from fetcher.src.reddit import RedditPost


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
        self._nlp = spacy.load("en_core_web_sm")
        self._link_pattern = r'http\S+'
        self._markdown_link_pattern = r'\[([^\]]+)\]\((http\S+)\)'

    def tokenize(self, txt) -> list[str]:
        return self._nltk.word_tokenize(txt)

    def clean_text(self, txt: str) -> str:
        txt = self.lowercase(txt)
        txt = self.replace_links(txt)
        txt = self.remove_punctuation(txt)
        # txt = self.replace_stopwords(txt)
        return txt

    def replace_stopwords(self, txt: str) -> str:
        stop_words = set(self._nltk.corpus.stopwords.words('english'))
        return " ".join([word for word in txt.split() if word not in stop_words])

    @staticmethod
    def lowercase(txt: str) -> str:
        return txt.lower()

    @staticmethod
    def remove_punctuation(txt: str) -> str:
        # remove punctuation except for hyphens and apostrophes, commas, and periods
        return re.sub(r'[^\w\s\-\'\.,]', '', txt)

    def replace_links(self, txt: str) -> str:

        def replace_plain_links(match):
            if re.match(self._markdown_link_pattern, match.group(0)):
                return match.group(0)
            return '<link>'

        def replace_markdown_link(match):
            return match.group(1)

        txt = re.sub(self._markdown_link_pattern, replace_markdown_link, txt)
        txt = re.sub(r'(\[([^\]]+)\]\((http\S+)\))|' + self._link_pattern, replace_plain_links, txt)
        return txt

    def lemmatize(self, tks: list[str]) -> list[str]:
        lemmatizer = self._nltk.stem.WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tks]

    def pos_tag(self, tks: list[str]) -> list[tuple[str, str]]:
        return self._nltk.pos_tag(tks, tagset='universal')

    def get_sentiment(self, txt: str) -> (float, float, float, float):
        sia = self._nltk.sentiment.SentimentIntensityAnalyzer()
        return sia.polarity_scores(txt)["compound"], sia.polarity_scores(txt)["pos"], sia.polarity_scores(txt)["neg"], sia.polarity_scores(txt)["neu"]

    def clean_posts(self, posts: list[RedditPost]) -> list[RedditPost]:
        for post in posts:
            post.cleaned_selftext = self.clean_text(post.selftext)
            post.cleaned_title = self.clean_text(post.title)
        return posts

    @property
    def nlp(self):
        return self._nlp

    def construct_dependency_graph(self, text: str):
        doc = self._nlp(text)
        # add begin and end attributes to each token
        for token in doc:
            print("token: " + token.__str__())
            print("repr: " + token.__repr__())
            print("idx: " + token.idx.__repr__())
            print("text: " + token.text)
            print("dep: " + token.dep_)
            print("head: " + token.head.text)
            print("children: " + token.children.__str__())


""" 
    list[Corpuses]
    [
        {
            platform: "reddit/politics",
            id: "123",
            title: "title",
            body: "body",
            sentiment: 0.5, # -1 to 1
            entities: [
                {
                    name: "entity1",
                    location: "title",
                    begin: 0,
                    end: 5,
                    sentiment: 0.5,
                    wiki_id: "Q123",
                    wiki_info: {
                        P31: ["Q5"],
                        P21: ["Q123"],
                        P17: ["Q456"]
                    }, 
                    dependent_entities: [
                        {
                            name: "entity2",
                            relatedness: 0.5
                            sentiment: 0.5
                        }, 
                        {
                            name: "entity3",
                            relatedness: 0.5
                            sentiment: 0.5
                        }
                    ]
                }, 
                {
                    name: "entity2",
                    location: "body",
                    begin: 10,
                    end: 20,
                    sentiment: 0.5,
                    related_entities: [
                        {
                            name: "entity1",
                            relatedness: 0.5
                            sentiment: 0.5
                        }, 
                        {
                            name: "entity3",
                            relatedness: 0.5
                            sentiment: 0.5
                        }
                    ]
                }
            ]  
        },
        {
            
        }
        .
        .
        .
        {
            
        }
    ]
    
"""

if __name__ == "__main__":
    processor = TextProcessor()
    text = (
        "South Carolina Gov, Henry McMaster held a ceremony Tuesday to spotlight a new law allowing any adult who can "
        "legally own a gun to carry the weapon openly without a permit."
    )

    tokens = processor.tokenize(text)
    lemmatized = processor.lemmatize(tokens)
    print(lemmatized)
    pos_tagged = processor.pos_tag(lemmatized)
    print(pos_tagged)

    doc = processor.nlp(" ".join(tokens))

    entity = "carolina"
    entity_span = None

    for ent in doc.ents:
        if entity in ent.text:
            entity_span = ent
            break


    # Function to extract sentiment-related words connected to the entity
    def extract_sentiment_phrases(entity_span: Span):
        relevant_tokens = []
        for token in entity_span.root.subtree:
            if token.dep_ in ["amod", "acomp", "advmod", "neg"]:  # adjectives, adverbs, negations
                relevant_tokens.append(token)
        return relevant_tokens


    # # Extract sentiment-relevant tokens for the entity
    # if entity_span:
    #     sentiment_tokens = extract_sentiment_phrases(entity_span)
    #     sentiment_text = " ".join([token.text for token in sentiment_tokens])
    #     print(f"Sentiment-related text for '{entity}': {sentiment_text}")
    #
    #     # Analyze sentiment of the relevant text
    #     sentiment_doc = processor.nlp(sentiment_text)
    #     sentiment = processor.sentiment_analysis(sentiment_text)
    #     print(f"Sentiment for '{entity}': {sentiment}")
    # else:
    #     print(f"Entity '{entity}' not found.")
    #
    # for token in doc:
    #     print("=========")
    #     print(token.text, "->", token.dep_, "->", token.head.text)
    #
    # displacy.serve(doc, style="dep", port=6969)

    print("done")
