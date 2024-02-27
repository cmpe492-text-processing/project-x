import reddit.reddit as rddt


def main():
    reddit = rddt.Reddit()
    post_list: list[rddt.RedditPost] = reddit.get_hot_posts("galatasaray")


if __name__ == "__main__":
    main()
