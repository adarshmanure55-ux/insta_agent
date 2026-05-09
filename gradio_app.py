import asyncio
import gradio as gr
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Updated to look for the new filename
SERVER_FILENAME = "mcp_server.py"
SERVER_PATH = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)

async def get_captions(topic_text, tone_choice):
    """Client logic to spawn server and call tool."""
    # Use sys.executable to ensure we use the current Python environment
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_PATH],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize connection
                await session.initialize()
                
                # Call tool
                result = await session.call_tool(
                    "suggest_captions", 
                    arguments={"topic": topic_text, "tone": tone_choice}
                )
                
                if not result.content:
                    return "⚠️ Server returned no content."
                
                return result.content[0].text
    except Exception as e:
        return f"❌ **MCP Connection Error:** {str(e)}\n\n*Verify {SERVER_FILENAME} is in the same folder.*"

def fast_ui_run(topic, tone):
    """Wrapper to bridge Gradio with Asyncio."""
    if not os.path.exists(SERVER_PATH):
        return f"❌ File Not Found: {SERVER_FILENAME} is missing from {os.path.dirname(SERVER_PATH)}"
    
    return asyncio.run(get_captions(topic, tone))

# Interface Definition
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📸 Instagram Captioner (MCP)")
    
    with gr.Row():
        with gr.Column():
            inp_topic = gr.Textbox(label="Post Topic", placeholder="e.g. Sunny day at the beach")
            inp_tone = gr.Radio(["Witty", "Minimalist", "Aesthetic"], value="Witty", label="Caption Style")
            btn = gr.Button("Generate✨", variant="primary")
        with gr.Column():
            out_md = gr.Markdown("Generated captions will show up here.")

    btn.click(fn=fast_ui_run, inputs=[inp_topic, inp_tone], outputs=out_md)

if __name__ == "__main__":
    demo.launch()