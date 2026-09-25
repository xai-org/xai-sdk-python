"""Example demonstrating Home Assistant integration with file attachments and attachment search.

This example shows how to create an effective Home Assistant AI assistant using Grok with file-based
context and device information. It addresses common issues like file usage in messages, server-side
tool integration, and provides comprehensive error handling and debugging.
"""

import json
import os
import tempfile
from typing import Dict, Any, Optional

from xai_sdk import Client
from xai_sdk.chat import user, system, file
from xai_sdk.tools import attachment_search


def create_home_assistant_context() -> Dict[str, Any]:
    """Create sample Home Assistant device context data."""
    return {
        "areas": {
            "bedroom": {
                "devices": [
                    {
                        "name": "Bedroom Light",
                        "entity_id": "light.bedroom_main",
                        "domain": "light",
                        "state": "off",
                        "attributes": {
                            "brightness": 255,
                            "color_temp": 3000,
                            "supported_features": ["brightness", "color_temp"]
                        }
                    },
                    {
                        "name": "Bedroom Temperature Sensor",
                        "entity_id": "sensor.bedroom_temperature",
                        "domain": "sensor",
                        "state": "22.5",
                        "attributes": {
                            "unit_of_measurement": "°C",
                            "device_class": "temperature"
                        }
                    },
                    {
                        "name": "Bedroom Door Sensor",
                        "entity_id": "binary_sensor.bedroom_door",
                        "domain": "binary_sensor",
                        "state": "closed",
                        "attributes": {
                            "device_class": "door"
                        }
                    }
                ]
            },
            "living_room": {
                "devices": [
                    {
                        "name": "Living Room Light",
                        "entity_id": "light.living_room_main",
                        "domain": "light",
                        "state": "on",
                        "attributes": {
                            "brightness": 180,
                            "supported_features": ["brightness"]
                        }
                    },
                    {
                        "name": "Living Room Thermostat",
                        "entity_id": "climate.living_room_thermostat",
                        "domain": "climate",
                        "state": "heat",
                        "attributes": {
                            "current_temperature": 21.0,
                            "target_temperature": 22.0,
                            "hvac_modes": ["heat", "cool", "off"]
                        }
                    },
                    {
                        "name": "Living Room Motion Sensor",
                        "entity_id": "binary_sensor.living_room_motion",
                        "domain": "binary_sensor",
                        "state": "off",
                        "attributes": {
                            "device_class": "motion"
                        }
                    }
                ]
            },
            "kitchen": {
                "devices": [
                    {
                        "name": "Kitchen Light",
                        "entity_id": "light.kitchen_main",
                        "domain": "light",
                        "state": "off",
                        "attributes": {}
                    },
                    {
                        "name": "Refrigerator Temperature",
                        "entity_id": "sensor.refrigerator_temp",
                        "domain": "sensor",
                        "state": "4.0",
                        "attributes": {
                            "unit_of_measurement": "°C",
                            "device_class": "temperature"
                        }
                    }
                ]
            }
        },
        "total_devices": 8,
        "total_entities": 8
    }


def create_system_prompt() -> str:
    """Create a comprehensive system prompt for Home Assistant integration."""
    return """You are Grok, a helpful Home Assistant AI assistant. You have access to the user's smart home devices through uploaded context files.

Your capabilities:
1. You can search through uploaded device context files using the attachment_search tool
2. You can count, list, and analyze devices by area, domain, or other criteria
3. You understand Home Assistant entity IDs and device domains
4. You can help control devices by providing entity_id information to the user

When asked about devices:
- Use the attachment_search tool to query the device data
- Provide accurate counts and lists
- Include entity_ids so the user can control devices
- Be specific about device states and capabilities

The device context is stored in JSON files that you can search through. Use the attachment_search tool when you need to look up device information.

Always be helpful, accurate, and provide actionable information."""


def upload_context_files(client: Client) -> tuple[str, str]:
    """Upload system prompt and device context files.

    Returns:
        Tuple of (prompt_file_id, context_file_id)
    """
    try:
        # Create system prompt file
        system_prompt = create_system_prompt()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(system_prompt)
            prompt_file_path = f.name

        # Create device context file
        device_context = create_home_assistant_context()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(device_context, f, indent=2)
            context_file_path = f.name

        # Upload files
        print("Uploading system prompt file...")
        prompt_file = client.files.upload(prompt_file_path)
        print(f"System prompt uploaded with ID: {prompt_file.id}")

        print("Uploading device context file...")
        context_file = client.files.upload(context_file_path)
        print(f"Device context uploaded with ID: {context_file.id}")

        # Clean up temp files
        os.unlink(prompt_file_path)
        os.unlink(context_file_path)

        return prompt_file.id, context_file.id

    except Exception as e:
        print(f"Error uploading files: {e}")
        raise


def handle_home_assistant_query(
    client: Client,
    prompt_file_id: str,
    context_file_id: str,
    query: str
) -> None:
    """Handle a Home Assistant query with proper file attachments and tools."""

    # Create chat with attachment search tool
    chat = client.chat.create(
        model="grok-4-fast",
        tools=[attachment_search(limit=20)],
        include=[
            "attachment_search_call_output",  # Include tool output for debugging
            "verbose_streaming",  # More detailed streaming
        ],
    )

    # Note: We cannot use system(file(prompt_file_id)) as file() only works in user() messages
    # Instead, we'll include the prompt content in the user message
    try:
        # First message with context files and query
        chat.append(user(
            "Here is the system prompt and device context for Home Assistant integration:",
            file(prompt_file_id),
            file(context_file_id),
            f"\n\nUser query: {query}"
        ))

        print("Processing query with attachments...")
        print("-" * 80)

        # Stream the response
        final_response = None
        for response, chunk in chat.stream():
            final_response = response

            # Show tool calls for debugging
            for tool_call in chunk.tool_calls:
                tool_type = getattr(tool_call, 'type', 'unknown')
                print(f"\n[DEBUG] Tool call: {tool_call.function.name} (type: {tool_type})")
                if hasattr(tool_call.function, 'arguments'):
                    print(f"[DEBUG] Arguments: {tool_call.function.arguments}")

            # Show tool outputs
            for tool_output in chunk.tool_outputs:
                if tool_output.content:
                    print(f"\n[DEBUG] Tool output: {tool_output.content[:200]}...")

            # Show response content
            if chunk.content:
                print(chunk.content, end="", flush=True)

        print("\n" + "-" * 80)

        if final_response:
            print("\nUsage statistics:")
            print(f"Total tokens: {final_response.usage.total_tokens}")
            print(f"Reasoning tokens: {final_response.usage.reasoning_tokens}")
            if hasattr(final_response, 'server_side_tool_usage'):
                print(f"Server-side tools used: {final_response.server_side_tool_usage}")

            # Show tool calls summary
            if final_response.tool_calls:
                print(f"\nTool calls made: {len(final_response.tool_calls)}")
                for i, tc in enumerate(final_response.tool_calls[:3]):  # Show first 3
                    print(f"  {i+1}. {tc.function.name}")

    except Exception as e:
        print(f"Error processing query: {e}")
        raise


def interactive_home_assistant_session(client: Client) -> None:
    """Run an interactive Home Assistant session with file-based context."""

    print("Setting up Home Assistant integration...")

    try:
        # Upload context files
        prompt_file_id, context_file_id = upload_context_files(client)

        print("\nHome Assistant AI Assistant ready!")
        print("You can ask questions like:")
        print("- 'How many devices are in the bedroom?'")
        print("- 'List all lights and their current states'")
        print("- 'What sensors do I have?'")
        print("- 'Show me devices by area'")
        print("\nType 'quit' to exit.\n")

        # Main interaction loop
        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break

                if not query:
                    continue

                handle_home_assistant_query(client, prompt_file_id, context_file_id, query)

                # For multi-turn conversations, we would append the response
                # But for this example, we'll start fresh each time for simplicity

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error in conversation: {e}")
                continue

        # Clean up files
        print("Cleaning up uploaded files...")
        client.files.delete(prompt_file_id)
        client.files.delete(context_file_id)
        print("Cleanup complete.")

    except Exception as e:
        print(f"Setup failed: {e}")
        raise


def demo_attachment_search(client: Client, context_file_id: str) -> None:
    """Demonstrate attachment search functionality."""

    print("\nDemonstrating attachment search...")

    chat = client.chat.create(
        model="grok-4-fast",
        tools=[attachment_search(limit=10)],
        include=["attachment_search_call_output"],
    )

    # Attach the context file and ask for a search
    chat.append(user(
        "Search the attached device context file for bedroom devices:",
        file(context_file_id),
        "Count the total number of devices in the 'bedroom' area. List their names and domains."
    ))

    print("Query: Count bedroom devices and list their names/domains")
    print("-" * 60)

    for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            if hasattr(tool_call, 'function'):
                print(f"Tool called: {tool_call.function.name}")
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n" + "-" * 60)


def main() -> None:
    """Main function demonstrating Home Assistant integration."""
    client = Client()

    try:
        # Upload files once
        prompt_file_id, context_file_id = upload_context_files(client)

        # Demo attachment search
        demo_attachment_search(client, context_file_id)

        # Run interactive session
        interactive_home_assistant_session(client)

    except Exception as e:
        print(f"Error in main: {e}")
        raise
    finally:
        # Ensure cleanup even if something fails
        try:
            if 'prompt_file_id' in locals():
                client.files.delete(prompt_file_id)
            if 'context_file_id' in locals():
                client.files.delete(context_file_id)
        except Exception as e:
            print(f"Warning: Could not clean up files: {e}")


if __name__ == "__main__":
    main()
