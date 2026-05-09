import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_instagram_captions(prompt_details):
    # 1. Configure the server connection
    # Replace 'path/to/server.py' with your actual MCP server location
    server_params = StdioServerParameters(
        command="python",
        args=["path/to/your_mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # 2. Construct the request
            # We wrap the user's intent with specific 'Instagram' instructions
            full_prompt = (
                f"Write 3 engaging Instagram captions for: {prompt_details}. "
                "Include relevant hashtags and emojis. "
                "Make one short, one witty, and one storytelling-focused."
            )

            # 3. Call the tool provided by your MCP server
            # Note: 'generate_content' should match the tool name defined in your server
            result = await session.call_tool(
                "generate_content", 
                arguments={"prompt": full_prompt}
            )

            return result

async def main():
    print("--- 📸 Instagram Caption Generator ---")
    topic = input("What is your post about? (e.g., 'sunset at the beach'): ")
    
    try:
        response = await get_instagram_captions(topic)
        print("\n✨ Suggested Captions:\n")
        print(response.content[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())