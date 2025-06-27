from datetime import datetime, timedelta, timezone

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.search import SearchParameters, news_source, rss_source, web_source, x_source


def live_search(client: Client):
    chat = client.chat.create(
        model="grok-3",
        # When no search sources are explicitly specified, the model will use the default
        # search sources which are web and X.
        # Mode auto means that the model will decide when to perform a search based on the
        # prompt.
        search_parameters=SearchParameters(mode="auto"),
    )

    user_input = input("Prompt: ")
    chat.append(user(user_input))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations ({len(response.citations)}): {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def live_search_streaming(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(mode="auto"),
    )

    user_input = input("Prompt: ")
    chat.append(user(user_input))

    print("Grok: ", end="", flush=True)
    latest_response = None
    for response, chunk in chat.stream():
        latest_response = response
        print(chunk.content, end="", flush=True)

    assert latest_response is not None

    print("\n")
    print(f"Citations ({len(latest_response.citations)}): {latest_response.citations}")
    print(f"Unique search sources: {latest_response.usage.num_sources_used}")


def live_search_with_x(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(
            mode="auto",
            sources=[x_source(included_x_handles=["xai"], post_favorite_count=1000)],
        ),
    )

    chat.append(user("What are some recent releases from xAI?"))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations: {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def live_search_with_web(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(
            # Mode on means the model will always perform a search and only use the explicit
            # sources that are specified.
            mode="on",
            sources=[web_source(country="US", excluded_websites=["wikipedia.org"])],
        ),
    )

    chat.append(user("Tell me about Nikola Tesla"))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations: {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def live_search_with_news(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(
            mode="on",
            sources=[news_source(country="US", excluded_websites=["foxnews.com"])],
        ),
    )

    chat.append(user("What is the latest news on the stock market?"))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations: {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def live_search_with_web_and_news(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(
            mode="on",
            # Only consider news and web articles from the last 7 days
            from_date=datetime.now(timezone.utc) - timedelta(days=7),
            sources=[web_source(country="US"), news_source(country="US")],
        ),
    )

    chat.append(user("What is the latest news on the stock market?"))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations: {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def live_search_with_rss(client: Client):
    chat = client.chat.create(
        model="grok-3",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                rss_source(links=["https://status.x.ai/feed.xml"]),
            ],
        ),
    )

    chat.append(user("What is the status of xAI's services?"))

    response = chat.sample()
    print(f"Content: {response.content}")
    print(f"Citations: {response.citations}")
    print(f"Unique search sources: {response.usage.num_sources_used}")


def main():
    client = Client()
    live_search(client)

    # Uncomment the respective line to run the example.
    # live_search_streaming(client)
    # live_search_with_x(client)
    # live_search_with_web(client)
    # live_search_with_news(client)
    # live_search_with_web_and_news(client)
    # live_search_with_rss(client)


if __name__ == "__main__":
    main()
