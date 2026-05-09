import asyncio
import sys
import re
import random
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Initialize the MCP Server
server = Server("insta-caption-manager")

def clean_topic(topic):
    """
    Removes specific names or 'person is doing x' phrasing 
    to make the caption feel more universal.
    """
    # Remove common names or generic 'Abhay' (Case insensitive)
    # You can add more names to this list if needed
    names_to_remove = ["abhay", "someone", "i am", "he is", "she is"]
    cleaned = topic.lower()
    
    for name in names_to_remove:
        cleaned = cleaned.replace(name, "")
    
    # Remove extra spaces left behind
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="suggest_captions",
            description="Generates varied Instagram captions without personal names.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The subject of the photo"},
                    "tone": {"type": "string", "description": "witty, minimalist, or aesthetic"}
                },
                "required": ["topic"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name != "suggest_captions":
        raise ValueError(f"Unknown tool: {name}")

    raw_topic = arguments.get("topic", "the moment")
    tone = arguments.get("tone", "witty").lower()
    
    # Process the topic to remove names
    subject = clean_topic(raw_topic)

    # Caption Libraries
    library = {
        "witty": [
            f"Instant human: just add {subject}. ☕",
            f"I’m not high maintenance, I’m just worth the effort of {subject}. 😉",
            f"{subject.capitalize()} called. I answered. 📞",
            f"Reality called, so I hung up and went back to {subject}. ✌️",
            f"Today's mood is sponsored by {subject}. 💸"
        ],
        "minimalist": [
            f"{subject.capitalize()}. ✨",
            f"Sip, smile, repeat. # {subject.replace(' ', '')}",
            f"Grounded in {subject}. 🌿",
            f"But first, {subject}. ☁️",
            f"Liquid gold and {subject} vibes. 💛"
        ],
        "aesthetic": [
            f"Watching the steam rise and the worries fade with {subject}. ☁️",
            f"Mornings are better when they're unscripted and filled with {subject}. ✨",
            f"A cup of hope and a side of {subject}. 📖",
            f"Inhale the aroma, exhale the chaos. 🧘",
            f"Finding magic in the simple act of {subject}. 📸"
        ]
    }

    # Select category or default to witty
    options = library.get(tone, library["witty"])
    
    # Pick 3 random unique options from the selected tone
    selected = random.sample(options, k=min(3, len(options)))
    
    result_text = f"### 📸 Captions (Refined)\n\n"
    for i, cap in enumerate(selected, 1):
        result_text += f"{i}. {cap}\n"

    return [types.TextContent(type="text", text=result_text)]

async def main():
    sys.stderr.write("MCP Server starting with 'No-Name' filters...\n")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="insta-caption-manager",
                server_version="1.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass