# async def get_text_colorized_block(color: str, text: str):
#     return f"```{color}\n{text}\n```"

async def get_ansi_block(text: str):
    "get colorized text block ``` for discord message"
    return f'```ansi\n{text}\n```'

async def colorize (color : dict, text: str):
    """colorize text for discord, need block `````` ansi\\nmessage\\n `````` or get_ansi_block(text)"""
    return f"{color['start']}{text}{color['end']}" 