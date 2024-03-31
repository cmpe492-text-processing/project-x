import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from spacy import displacy
from spacy.tokens import Span

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

    def tokenize(self, text) -> list[str]:
        return self._nltk.word_tokenize(text)

    def clean_text(self, text: str) -> str:
        # lowercase and remove punctuation
        tk = self.tokenize(text)
        tk = [word.lower() for word in tk]
        tk = [word for word in tk if word.isalnum()]
        # remove stopwords
        stop_words = set(self._nltk.corpus.stopwords.words('english'))
        tk = [word for word in tk if word not in stop_words]
        return " ".join(tk)

    def lemmatize(self, tokens: list[str]) -> list[str]:
        lemmatizer = self._nltk.stem.WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tokens]

    def pos_tag(self, tokens: list[str]) -> list[tuple[str, str]]:
        return self._nltk.pos_tag(tokens, tagset='universal')

    def sentiment_analysis(self, text: str):
        sia = self._nltk.sentiment.SentimentIntensityAnalyzer()
        print("polarity scores: ", sia.polarity_scores(text))
        print("compound: ", sia.polarity_scores(text)["compound"])
        return sia.polarity_scores(text)["compound"]

    def clean_posts(self, posts: list[RedditPost]) -> list[RedditPost]:
        for post in posts:
            post.cleaned_selftext = self.clean_text(post.selftext)
            post.cleaned_title = self.clean_text(post.title)
        return posts

    @property
    def nlp(self):
        return self._nlp

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
    print(tokens)
    cleaned = processor.clean_text(tokens)
    print(cleaned)
    lemmatized = processor.lemmatize(cleaned)
    print(lemmatized)
    pos_tagged = processor.pos_tag(lemmatized)
    print(pos_tagged)

    sentiment = processor.sentiment_analysis(text)
    print(sentiment)

    doc = processor.nlp(" ".join(cleaned))

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


    # Extract sentiment-relevant tokens for the entity
    if entity_span:
        sentiment_tokens = extract_sentiment_phrases(entity_span)
        sentiment_text = " ".join([token.text for token in sentiment_tokens])
        print(f"Sentiment-related text for '{entity}': {sentiment_text}")

        # Analyze sentiment of the relevant text
        sentiment_doc = processor.nlp(sentiment_text)
        sentiment = processor.sentiment_analysis(sentiment_text)
        print(f"Sentiment for '{entity}': {sentiment}")
    else:
        print(f"Entity '{entity}' not found.")

    for token in doc:
        print("=========")
        print(token.text, "->", token.dep_, "->", token.head.text)

    displacy.serve(doc, style="dep", port=6969)

    print("done")