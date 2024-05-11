# This file currently fetches posts, then creates the corpuses saves both posts and to DB.
# TODO It should also extract the corpuses, and then extract features to create several jsons.
from utils import database as db, reddit as rddt
from corpus_generator.src.corpus_generator import GenerateCorpus
from corpus_generator.src.corpus_generator import Platform


def main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    subreddits = ["trump", "politics", "elections", "democrats", "republican", "PoliticalDiscussion"]
    for subreddit in subreddits:
        post_list: list[rddt.RedditPost] = reddit.get_hot_posts(subreddit, limit=3)

        corpus_list: list = []
        for post in post_list:
            corpus_generator = GenerateCorpus(Platform.REDDIT, subreddit, post.id, post.title, post.selftext)
            corpus = corpus_generator.generate_corpus()
            corpus_list.append(corpus)

        print(
            f"Inserting {len(post_list)} posts and {len(corpus_list)} "
            f"corpuses into the database related to {subreddit}.")

        database_manager.insert_posts(post_list)
        database_manager.insert_corpuses(corpus_list)


if __name__ == "__main__":
    main()
