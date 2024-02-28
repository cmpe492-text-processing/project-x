import reddit.reddit as rddt
import database as db

def main():
    reddit = rddt.Reddit()
    databaseManager = db.DatabaseManager()
    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("galatasaray")
    databaseManager.insert_posts(post_list)


if __name__ == "__main__":
    main()
