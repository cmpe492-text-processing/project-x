import praw
import os
from dotenv import load_dotenv


class Reddit:
    def __init__(self):
        load_dotenv('../.env')
        self.reddit: praw.Reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            password=os.getenv("PASSWORD"),
            user_agent="Comment Extraction (by u/" + os.getenv("USERNAME") + ")",
            username=os.getenv("USERNAME"),
        )

    def get

    def get_comments(self, subreddit, limit):
        comments = []
        for submission in self.reddit.subreddit(subreddit).hot(limit=limit):
            submission.comments.replace_more(limit=10)
            for comment in submission.comments.list():
                comments.append(comment.body)

        return comments


if __name__ == "__main__":
    reddit: Reddit = Reddit()
    reddit.get_comments("all", 10)

