from bluesky_fetcher import BlueskyFetcher
from add_locations import update_post_locations
from data_manager import DataManager


def main():
    print("Starting tweet analysis pipeline...")
    data_manager = DataManager()
    fetcher = BlueskyFetcher(data_manager)

    print("Fetching and storing new Bluesky posts...")
    fetcher.fetch_posts()

    print("Updating posts with location information...")
    update_post_locations(data_manager)

    print("Tweet analysis pipeline complete.")


if __name__ == "__main__":
    main()
