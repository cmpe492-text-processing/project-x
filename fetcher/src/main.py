import json
import os
import re
import database as db
from fetcher.src import reddit as rddt
from fetcher.src.processor import TextProcessor
from fetcher.src.tagme_manager import TagmeManager
from fetcher.src.corpus_generator import GenerateCorpus
from fetcher.src.corpus_generator import Platform


def main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    tagme_manager = TagmeManager(rho=0.1)
    processor_manager = TextProcessor()

    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("python", limit=2)
    post_list = processor_manager.clean_posts(post_list)
    database_manager.insert_posts(post_list)
    post_all_annotations, title_all_annotations = tagme_manager.tag_posts(post_list)
    print(post_all_annotations)
    print(title_all_annotations)


def other_main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    # subreddits = ["trump", "politics", "elections", "democrats", "republican", "PoliticalDiscussion"]
    subreddits = ['trump']
    for subreddit in subreddits:
        post_list: list[rddt.RedditPost] = reddit.get_hot_posts(subreddit, limit=3)

        corpus_list: list = []
        for post in post_list:
            corpus_generator = GenerateCorpus(Platform.REDDIT, subreddit, post.id, post.title, post.selftext)
            corpus_list.append(corpus_generator.generate_corpus())

        print(
            f"Inserting {len(post_list)} posts and {len(corpus_list)} corpuses into the database related to {subreddit}.")
        database_manager.insert_posts(post_list)
        database_manager.insert_corpuses(corpus_list)


def exporter():
    dbmng = db.DatabaseManager()
    corpuses = dbmng.get_corpuses()
    corpuses = [corp[3] for corp in corpuses]

    raw_dir = '../../data/raw/'
    pattern = re.compile(r'corpus(\d+)\.json')
    files = os.listdir(raw_dir)
    used_nums = {int(match.group(1)) for match in (pattern.match(f) for f in files) if match}
    max_num = max(used_nums) if used_nums else 0
    available_num = next((num for num in range(1, max_num + 2) if num not in used_nums), 1)

    new_filename = f'corpus{available_num}.json'

    with open(raw_dir + new_filename, 'w') as f:
        json.dump(corpuses, f, indent=2)
        print(f'Exported {len(corpuses)} corpuses to {new_filename}')


if __name__ == "__main__":
    other_main()
