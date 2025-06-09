from xai_sdk import Client


def get_api_key_info(client: Client) -> None:
    """Get the information regarding your API key."""
    api_key_info = client.auth.get_api_key_info()
    print("--- API key info ---")
    print(f"redacted_api_key: {api_key_info.redacted_api_key}")
    print(f"user_id: {api_key_info.user_id}")
    print(f"name: {api_key_info.name}")
    print(f"create_time: {api_key_info.create_time}")
    print(f"modify_time: {api_key_info.modify_time}")
    print(f"modified_by: {api_key_info.modified_by}")
    print(f"team_id: {api_key_info.team_id}")
    print(f"acls: {api_key_info.acls}")
    print(f"api_key_id: {api_key_info.api_key_id}")
    print(f"api_key_blocked: {api_key_info.api_key_blocked}")
    print(f"team_blocked: {api_key_info.team_blocked}")
    print(f"disabled: {api_key_info.disabled}")


def main() -> None:
    client = Client()
    get_api_key_info(client)


if __name__ == "__main__":
    main()
