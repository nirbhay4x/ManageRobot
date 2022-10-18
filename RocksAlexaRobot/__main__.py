import importlib
import random
import time
import re

from sys import argv
from typing import Optional
import RocksAlexaRobot.modules.sql.users_sql as sql
from RocksAlexaRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,UPDATES_CHANNEL,
    dispatcher,
    StartTime,
    telethn,
    updater)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from RocksAlexaRobot.modules import ALL_MODULES
from RocksAlexaRobot.modules.helper_funcs.chat_status import is_user_admin
from RocksAlexaRobot.modules.helper_funcs.misc import paginate_modules
from RocksAlexaRobot.modules.disable import DisableAbleCommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, __version__ as ptbver
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown



def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time



PM_START_TEXT = """
 ──『[ֆǟʀӄǟʀ](https://te.legra.ph/file/ab3acc65de7d85857d595.jpg)』

*𝐇𝐞𝐥𝐥𝐨 𝐁𝐚𝐛𝐲 ❣️ !*
✪ 𝐈"𝐦 𝐭𝐡𝐞 𝐌𝐨𝐬𝐭 𝐏𝐨𝐰𝐞𝐫𝐟𝐮𝐥 𝐆𝐫𝐨𝐮𝐩 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐁𝐨𝐭 𝐨𝐟 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦.

𝐈 𝐡𝐚𝐯𝐞 𝐀𝐰𝐞𝐬𝐨𝐦𝐞 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐚𝐧𝐝 𝐧𝐨 𝐨𝐧𝐞 𝐜𝐚𝐧 𝐛𝐞𝐚𝐭 𝐦𝐞.
────────────────────────
✪ 𝐈"𝐦 𝐡𝐞𝐫𝐞 𝐭𝐨 𝐦𝐚𝐤𝐞 𝐲𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐟𝐮𝐧 𝐚𝐧𝐝 𝐞𝐚𝐬𝐲! 𝐈 𝐡𝐚𝐯𝐞 𝐥𝐨𝐭𝐬 𝐨𝐟 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬, 𝐒𝐮𝐜𝐡 𝐚𝐬 𝐅𝐥𝐨𝐨𝐝 𝐂𝐨𝐧𝐭𝐫𝐨𝐥, 𝐀 𝐖𝐚𝐫𝐧𝐢𝐧𝐠 𝐒𝐲𝐬𝐭𝐞𝐦, 𝐚 𝐧𝐨𝐭𝐞 𝐊𝐞𝐞𝐩𝐢𝐧𝐠 𝐒𝐲𝐬𝐭𝐞𝐦, 𝐚𝐧𝐝 𝐞𝐯𝐞𝐧 𝐫𝐞𝐩𝐥𝐢𝐞𝐬 𝐨𝐧 𝐏𝐫𝐞𝐝𝐞𝐭𝐞𝐫𝐦𝐢𝐧𝐞𝐝 𝐟𝐢𝐥𝐭𝐞𝐫𝐬.
✪𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 [ֆǟʀӄǟʀ](https://t.me/nirbhay_2x) 𝐚𝐧𝐝 [SARKAR 𝐍𝐞𝐭𝐰𝐨𝐫𝐤](https://t.me/sarkar_network)
────────────────────────
✪ 𝐇𝐢𝐭 /help 𝐭𝐨 𝐦𝐲 𝐏𝐨𝐰𝐞𝐫 𝐁𝐮𝐝𝐝𝐲 ✌️.
────────────────────────
✪ [𝐂𝐇𝐀𝐍𝐍𝐄𝐋](t.me/sarkar_network) ❤️ [𝐆𝐑𝐎𝐔𝐏](t.me/yaari_apni_apni)
────────────────────────
✪ ──『*ᴛʜᴀɴᴋs  ғᴏʀ  ᴜsɪɴɢ*』
"""
PMSTART_CHAT = (
    "[𝐆𝐞𝐭 𝐁𝐮𝐬𝐲 𝐋𝐢𝐯𝐢𝐧𝐠 𝐨𝐫 𝐆𝐞𝐭 𝐁𝐮𝐬𝐲 𝐃𝐲𝐢𝐧𝐠!!!](https://telegra.ph/file/362b0e068701bf0b06c10.jpg)",
    "[ɪ'ᴍ ֆǟʀӄǟʀ ᴘʀᴏᴊᴇᴄᴛ](https://telegra.ph/file/dbf549700d813ef6ddbe6.jpg)",
    "[ᴛᴜʀɴ ʏᴏᴜʀ ᴡᴏᴜɴᴅs ɪɴᴛᴏ ᴡɪsᴅᴏᴍ 🔥](https://telegra.ph/file/35e730dea457c85cc367b.mp4)",
    "[ʜᴀʜᴀʜᴀᴀ ɪ ᴀᴍ Queen!!!!](https://telegra.ph/file/4f51ea1bf4024a27838d2.jpg)", )

buttons = [
    [
        InlineKeyboardButton(
                            text="🥺 𝐀𝐝𝐝 𝐌𝐞 𝐁𝐚𝐛𝐲 🥺",
                            url="t.me/ManagementXrobot?startgroup=true"),
                    ],
                   [
                       InlineKeyboardButton(text="😜 𝐅𝐀𝐓𝐇𝐄𝐑 😜", url="t.me/nirbhay_2x"),
                       InlineKeyboardButton(text="🙎 𝐅𝐄𝐃 🙎", url="t.me/LD_Federation"),
                     ],
                    [                  
                       InlineKeyboardButton(
                             text="🤘 𝐎𝐖𝐍𝐄𝐑 🤘",
                             url=f"https://t.me/Nirbhay_2x"),
                       InlineKeyboardButton(
                             text="🔰 𝐍𝐄𝐓𝐖𝐎𝐑𝐊 🔰",
                             url=f"https://t.me/yaari_apni_apni"),
                        ],
                       [
                           InlineKeyboardButton(text="💖 𝐋𝐎𝐕𝐄 💖", url="t.me/nirbha_y"
         ),
    ],
]

HELP_STRINGS = """
✪ 𝐇𝐞𝐲 𝐭𝐡𝐞𝐫𝐞, 𝐈"𝐦 ֆǟʀӄǟʀ 𝐌𝐚𝐝𝐞 𝐛𝐲 [ֆǟʀӄǟʀ](https://t.me/nirbhay_2x) !
✪ 𝐈"𝐦 𝐔𝐬𝐞𝐥𝐞𝐬𝐬 𝐰𝐢𝐭𝐡𝐨𝐮𝐭 𝐭𝐡𝐞𝐬𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐈𝐟 𝐲𝐨𝐮 𝐖𝐚𝐧𝐧𝐚 𝐌𝐚𝐤𝐞 𝐦𝐞 𝐅𝐮𝐧𝐜𝐭𝐢𝐨𝐧𝐥, 𝐭𝐡𝐞𝐧 𝐌𝐚𝐤𝐞 𝐦𝐞 𝐀𝐝𝐦𝐢𝐧 𝐢𝐧 𝐲𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐑𝐮𝐧 𝐭𝐡𝐞𝐬𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:
────────────────────────
✪ - /start: *𝐒𝐭𝐚𝐫𝐭𝐬 𝐦𝐞! 𝐘𝐨𝐮"𝐯𝐞 𝐏𝐫𝐨𝐛𝐚𝐛𝐥𝐲 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐔𝐬𝐞𝐝 𝐭𝐡𝐢𝐬.*
✪ - /help: *𝐒𝐞𝐧𝐝𝐬 𝐭𝐡𝐢𝐬 𝐌𝐞𝐬𝐬𝐚𝐠𝐞; 𝐈"𝐥𝐥 𝐭𝐞𝐥𝐥 𝐲𝐨𝐮 𝐌𝐨𝐫𝐞 𝐚𝐛𝐨𝐮𝐭 𝐌𝐲𝐬𝐞𝐥𝐟!*
✪ - /donate: *𝐆𝐢𝐯𝐞𝐬 𝐲𝐨𝐮 𝐢𝐧𝐟𝐨 𝐨𝐧 𝐇𝐨𝐰 𝐭𝐨 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐦𝐞 𝐚𝐧𝐝 𝐌𝐲 𝐂𝐫𝐞𝐚𝐭𝐨𝐫.*
────────────────────────
✪ 𝐈𝐟 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐫𝐞𝐩𝐨𝐫𝐭 𝐁𝐮𝐠𝐬 𝐨𝐫 𝐡𝐚𝐯𝐞 𝐚𝐧𝐲 𝐪𝐮𝐞𝐬𝐭𝐢𝐨𝐧𝐬 𝐨𝐧 𝐡𝐨𝐰 𝐭𝐨 𝐮𝐬𝐞 𝐦𝐞 𝐭𝐡𝐞𝐧 𝐟𝐞𝐞𝐥 𝐟𝐫𝐞𝐞 𝐭𝐨 𝐫𝐞𝐚𝐜𝐡 𝐨𝐮𝐭: @WCFnetwork 𝐎𝐫 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐨 𝐦𝐲 [𝐎𝐖𝐍𝐄𝐑](http://t.me/OpSangram)
✪ 𝐀𝐥𝐥 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐜𝐚𝐧 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐰𝐢𝐭𝐡 𝐭𝐡𝐞 𝐅𝐨𝐥𝐥𝐨𝐰𝐢𝐧𝐠: [(/),(!),(?),(.),(~)](https://telegra.ph/file/7ae68204eacb4fb716e21.jpg)
✪ 𝐋𝐢𝐬𝐭 𝐨𝐟 𝐀𝐥𝐥 𝐌𝐨𝐝𝐮𝐥𝐞𝐬:
────────────────────────
""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "📝 𝐀𝐥𝐥 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐜𝐚𝐧 𝐄𝐢𝐭𝐡𝐞𝐫 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐰𝐢𝐭𝐡 / 𝐨𝐫 !.",
)

HELP_MSG = "𝐂𝐥𝐢𝐜𝐤 𝐭𝐡𝐞 𝐁𝐮𝐭𝐭𝐨𝐧 𝐁𝐞𝐥𝐨𝐰 𝐭𝐨 𝐆𝐞𝐭 𝐡𝐞𝐥𝐩 𝐌𝐚𝐧𝐮 𝐢𝐧 𝐲𝐨𝐮𝐫 𝐏𝐌."
DONATE_STRING = """𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐨 𝐌𝐲 𝐏𝐫𝐞𝐭𝐭𝐲 [𝐎𝐖𝐍𝐄𝐑](t.me/OpSangram)"""
HELP_IMG= "https://telegra.ph/file/362b0e068701bf0b06c10.jpg"
GROUPSTART_IMG= "https://telegra.ph/file/35e730dea457c85cc367b.mp4"

PM_IMG = ( "https://telegra.ph/file/0a6117b91c716a0c9cf99.jpg",
           "https://telegra.ph/file/362b0e068701bf0b06c10.jpg",
           "https://telegra.ph/file/4f51ea1bf4024a27838d2.jpg",
           "https://telegra.ph/file/2cdc3619dc9966bb8b0c2.jpg",
           "https://telegra.ph/file/7ae68204eacb4fb716e21.jpg", )


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("RocksAlexaRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)



def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅Back", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_text(
                random.choice(PMSTART_CHAT),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
            first_name = update.effective_user.first_name
            update.effective_message.reply_photo(
               random.choice(PM_IMG),PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        first_name = update.effective_user.first_name
        update.effective_message.reply_video(
            GROUPSTART_IMG, caption= "*𝐇𝐞𝐲 {},*\n*𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐐𝐮𝐞𝐞𝐧 𝐢𝐬 𝐇𝐞𝐫𝐞*\n*𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐋𝐞𝐯𝐞𝐥 𝐓𝐢𝐦𝐞* : {} ".format(
             first_name,uptime
            ),
            parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
                [
                  [
                  InlineKeyboardButton(text="😜 𝐅𝐀𝐓𝐇𝐄𝐑 😜 ", url=f"t.me/OpSangram"),
                  InlineKeyboardButton(text="😎 𝐔𝐩𝐝𝐚𝐭𝐞  ", url=f"t.me/WCFnetwork"),
                  ]
                ]
            ),
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors



def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "*𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 * © [𝐒𝐚𝐧𝐠𝐫𝐚𝐦](t.me/OpSangram) *𝐚𝐧𝐝* [𝐖𝐂𝐅 𝐍𝐞𝐭𝐰𝐨𝐫𝐤](t.me/WCFnetwork)\n*𝐇𝐞𝐫𝐞 𝐢𝐬 𝐭𝐡𝐞 𝐡𝐞𝐥𝐩 𝐟𝐨𝐫 𝐭𝐡𝐞 {} 𝐌𝐨𝐝𝐮𝐥𝐞𝐬 :*\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="⬅ Back", callback_data="help_back"),
                      InlineKeyboardButton(text="⬅ Home", callback_data="alexa_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass



def alexa_data_callback(update, context):
    query = update.callback_query
    if query.data == "alexa_":
        query.message.edit_text(
            text="""CallBackQueriesData Here""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="alexa_back")
                 ]
                ]
            ),
        )
    elif query.data == "alexa_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )




def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"*𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐦𝐞 𝐢𝐧 𝐩𝐦 𝐭𝐨 𝐠𝐞𝐭 𝐡𝐞𝐥𝐩 𝐨𝐟* {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝐇𝐞𝐥𝐩",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo(
            HELP_IMG, HELP_MSG,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝐇𝐞𝐥𝐩",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "𝐇𝐞𝐫𝐞 𝐢𝐬 𝐭𝐡𝐞 𝐡𝐞𝐥𝐩 𝐟𝐨𝐫 𝐭𝐡𝐞 *{}* 𝐌𝐨𝐝𝐮𝐥𝐞𝐬 :\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "*ᴛʜᴇsᴇ ᴀʀᴇ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:*" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "*sᴇᴇᴍs ʟɪᴋᴇ ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ᴜsᴇʀ sᴘᴇᴄɪғɪᴄ sᴇᴛᴛɪɴɢs ᴀᴠᴀɪʟᴀʙʟᴇ* :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="ᴡʜɪᴄʜ ᴍᴏᴅᴜʟᴇ ᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ ᴄʜᴇᴄᴋ {}'s sᴇᴛᴛɪɴɢs ғᴏʀ?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "*sᴇᴇᴍs ʟɪᴋᴇ ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ᴄʜᴀᴛ sᴇᴛᴛɪɴɢs ᴀᴠᴀɪʟᴀʙʟᴇ* :'(\n*sᴇɴᴅ ᴛʜɪs* "
                "*ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ ɪɴ ᴛᴏ ғɪɴᴅ ɪᴛs ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs!*",
                parse_mode=ParseMode.MARKDOWN,
            )



def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* ʜᴀs ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ sᴇᴛᴛɪɴɢs ғᴏʀ ᴛʜᴇ *{}* ᴍᴏᴅᴜʟᴇs:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "*ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ ǫᴜɪᴛᴇ ᴀ ғᴇᴡ sᴇᴛᴛɪɴɢs ғᴏʀ* {} - *ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ*"
                "*ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇsᴛᴇᴅ ɪɴ.*".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "*ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ ǫᴜɪᴛᴇ ᴀ ғᴇᴡ sᴇᴛᴛɪɴɢs ғᴏʀ* {} - *ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ*"
                "*ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇsᴛᴇᴅ ɪɴ.*".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="*ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ ǫᴜɪᴛᴇ ᴀ ғᴇᴡ sᴇᴛᴛɪɴɢs ғᴏʀ* {} - *ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴘɪᴄᴋ ᴡʜᴀᴛ*"
                "*ʏᴏᴜ'ʀᴇ ɪɴᴛᴇʀᴇsᴛᴇᴅ ɪɴ.*".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))



def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪs ᴄʜᴀᴛ's sᴇᴛᴛɪɴɢs, ᴀs ᴡᴇʟʟ ᴀs ʏᴏᴜʀs."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "*ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs.*"

    else:
        send_settings(chat.id, user.id, True)



def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 2042185317 and DONATION_LINK:
            update.effective_message.reply_text(
                "*ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴅᴏɴᴀᴛᴇ ᴛᴏ ᴛʜᴇ ᴘᴇʀsᴏɴ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴜɴɴɪɴɢ ᴍᴇ*"
                "[ʜᴇʀᴇ]({})".format(DONATION_LINK),
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "*ɪ'ᴠᴇ ᴘᴍ'ᴇᴅ ʏᴏᴜ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪɴɢ ᴛᴏ ᴍʏ ᴄʀᴇᴀᴛᴏʀ!*"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "*ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ғɪʀsᴛ ᴛᴏ ɢᴇᴛ ᴅᴏɴᴀᴛɪᴏɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.*"
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop




def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@WorldChattingFriendsWCF",
                "https://telegra.ph/file/362b0e068701bf0b06c10.jpg",
                caption="「 Queen 」 ɪs ᴀʟɪᴠᴇ ✌️!\n\nᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ᴀɴᴅ @WCFnetwork 🤏",
            )
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)


    start_handler = DisableAbleCommandHandler("start", start)

    help_handler = DisableAbleCommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    data_callback_handler = CallbackQueryHandler(alexa_data_callback, pattern=r"alexa_")
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(data_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Rocks Alexa is now alive and functioning")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    main()
