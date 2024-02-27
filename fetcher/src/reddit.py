import praw
import os
from dotenv import load_dotenv

def get_comments(subreddit, limit):
    comments = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        submission.comments.replace_more(limit=10)
        for comment in submission.comments.list():
            comments.append(comment.body)

    return comments


if __name__ == "__main__":
    load_dotenv('../.env')
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("PASSWORD"),
        user_agent="Comment Extraction (by u/" + os.getenv("USERNAME") + ")",
        username=os.getenv("USERNAME"),
    )
    print(get_comments("all", 10))
