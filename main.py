# Description: This file contains the main code for the bot.

""" Libraries """
import hydrogram.filters as filters
from hydrogram import Client
from hydrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

import backend
import config


""" Initialization """
app = Client(name="rateme", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
root = backend.get_root("storage.db")


""" Functions """


# Greeting Command
@app.on_message(filters=filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        text="Hi there! I am RateMe Bot. I can help you rate and review users based on their behavior. You can also use me to moderate your community by restricting low-rated users.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Add me to a group", url=f"https://t.me/{client.me.username}?startgroup=true"),
                ],
                [
                    InlineKeyboardButton(text="Commands", callback_data="commands"),
                    InlineKeyboardButton(text="About", callback_data="about"),
                ],
            ]
        ),
    )


# Debug Command
@app.on_message(filters=filters.command("debug") & filters.user(config.OWNER_ID))
async def debug_message(client: Client, message: Message):
    string = await root.to_string()

    if len(string) < 4096:
        await message.reply_text(text=string)
    else:
        print(string)
        await message.reply_text(text=string[:4093] + "...")


if __name__ == "__main__":
    print("Starting the bot...")
    app.run()
