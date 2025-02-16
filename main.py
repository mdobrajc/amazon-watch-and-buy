import time
from threading import Thread, Event
from amazon import AmazonBot


# Main function
def main():
    # Stop event across the threads
    stop_event = Event()

    # Initial print
    print("Starting up...")
    print("-" * 32)

    # Print per bot, currently only Amazon, therefor no special .env checks needed
    print("Loading Amazon Bot...")
    amazonBot = AmazonBot()

    # Create threads
    amazon_thread = Thread(target=amazonBot.run, kwargs={"stop_event": stop_event})

    try:
        amazon_thread.start()

        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_event.set()

        for thread in [amazon_thread]:
            try:
                thread.join(timeout=1.0)
            except KeyboardInterrupt:
                continue

        print("Threads stopped successfully")

    return


if __name__ == "__main__":
    main()
