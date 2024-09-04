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
from hydrogram.enums import ChatType

import backend
import config


""" Initialization """
app = Client(
    name="rateme",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)
root = backend.get_root("storage.db")


""" Functions """


# Greeting Command
@app.on_message(filters=filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        text="Hi there! I am RateMe Bot. I can help you rate and review users based on their behavior. You can also use me to moderate your community by restricting low-rated users.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=(
                [
                    [
                        InlineKeyboardButton(text="Commands", callback_data="commands"),
                        InlineKeyboardButton(text="About bot", callback_data="about"),
                    ]
                ]
                + (
                    [
                        [
                            InlineKeyboardButton(
                                text="Add me to a group",
                                url=f"https://t.me/{client.me.username}?startgroup=true",
                            )
                        ]
                    ]
                    if message.chat.type == ChatType.PRIVATE
                    else []
                )
            ),
        ),
    )


# Debug Command
@app.on_message(filters=filters.command("debug") & filters.user(config.OWNER_ID))
async def debug_message(client: Client, message: Message):
    string = await root.to_string()

    if len(string) < 4088:
        await message.reply_text(text=f"```\n{string}\n```")
    else:
        print(string)
        await message.reply_text(text=f"```\n{string[:4085]}...\n```")


# Commands Callback
@app.on_callback_query(filters=filters.regex("commands"))
async def commands_callback(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text="`@theratemebot` - Use the bot in Inline Mode for rating and reviewing user profiles\n\n"
        "To moderate a community, use the following commands:\n\n"
        "/banlimit [n] - Set the ban limit for a community. [1 ≤ n ≤ 5]\n"
        "/mutelimit [n] - Set the mute limit for a community. [1 ≤ n ≤ 5]\n"
        "/approve [@u] - Approve a user (locally) to prevent them from being restricted [@u - username/reply]\n\n"
        "To know more about the bot, click the button below 👇",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=(
                [
                    [
                        InlineKeyboardButton(text="About bot", callback_data="about"),
                    ]
                ]
            ),
        ),
    )

@app.on_callback_query(filters=filters.regex("about"))
async def about_callback(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text="RateMe Bot is allows users to rate and review other users based on their behavior. It also provides community moderation tools to restrict low-rated users from participating in the community.\n\n"
        "The bot is developed by [XelXen](https://t.me/XelXen) using [Hydrogram](https://hydrogram.org/) and other libraries.\n\n"
        "To know more about the technicalities, you can visit the [GitHub Repository](https://github.com/XelXen/RateMe).",
        disable_web_page_preview=True,
    )

if __name__ == "__main__":
    print("Starting the bot...")
    app.run()
