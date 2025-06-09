from xai_sdk import Client


def tokenize_text(client: Client):
    prompt = input("Enter a prompt: ")
    tokens = client.tokenize.tokenize_text(prompt, model="grok-3")
    for token in tokens:
        print(f"Token ID: {token.token_id}")
        print(f"Token Text: {token.string_token}")
        print(f"Token Bytes: {token.token_bytes}")


def main():
    client = Client()
    tokenize_text(client)


if __name__ == "__main__":
    main()
