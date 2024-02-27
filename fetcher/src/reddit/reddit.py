import praw
import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class RedditPost:
    id: str
    author_id: str
    created_utc: int
    name: str
    permalink: str
    score: int
    selftext: str
    subreddit: str
    title: str
    upvote_ratio: float


class Reddit:
    def __init__(self):
        load_dotenv('/Users/bgezer/Documents/_root/_boun/8.Donem/senior-project/project-x/fetcher/.env')
        self.reddit: praw.Reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            password=os.getenv("PASSWORD"),
            user_agent="Comment Extraction (by u/" + os.getenv("USERNAME") + ")",
            username=os.getenv("USERNAME"),
        )

    def get_hot_posts(self, subreddit) -> list[RedditPost]:
        posts: list[RedditPost] = []
        for submission in self.reddit.subreddit(subreddit).hot(limit=10):
            post = RedditPost(
                id=submission.id,
                author_id=submission.author.id,
                created_utc=submission.created_utc,
                name=submission.name,
                permalink=submission.permalink,
                score=submission.score,
                selftext=submission.selftext,
                subreddit=submission.subreddit.display_name,
                title=submission.title,
                upvote_ratio=submission.upvote_ratio
            )
            posts.append(post)

        return posts
