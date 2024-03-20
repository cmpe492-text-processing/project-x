import reddit.reddit as rddt
import database as db
from fetcher.src.tagme.tagme_manager import TagmeManager


def main():
    reddit = rddt.Reddit()
    database_manager = db.DatabaseManager()
    tagme_manager = TagmeManager(rho=0.1)

    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("PoliticalDiscussion")
    tagged_post_list, humans = tagme_manager.process_posts(post_list)
    print(tagged_post_list)
    print(humans)
    database_manager.insert_posts(post_list)


if __name__ == "__main__":
    main()
