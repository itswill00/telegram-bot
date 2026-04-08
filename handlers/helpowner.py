import html
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from utils.config import OWNER_ID

def helpowner_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("TERMINATE", callback_data="helpowner:close")]
    ])

async def helpowner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    if not user or user.id not in OWNER_ID:
        return

    text = (
        "<b>CORE ACCESS</b>\n"
        "Root privilege interface:\n\n"

        "<b>System Operations</b> — <code>$</code>\n"
        "• <code>$core</code>   : Administration portal\n"
        "• <code>$node</code>   : System control utility\n"
        "• <code>$sh</code> / <code>$py</code> : Executor (Shell/Python)\n"
        "• <code>$sync</code>   : Repository synchronization\n"
        "• <code>$reboot</code> : Process replacement\n"
        "• <code>$live</code>   : Toggle watchdog state\n"
        "• <code>$env</code>    : Environment configuration\n"
        "• <code>$dump</code>   : Data archive generation\n"
        "• <code>$load</code>   : Database restoration\n\n"

        "<b>Control Suite</b> — <code>$</code>\n"
        "• <code>$purge</code>  : Global ID banishment\n"
        "• <code>$revive</code> : Restriction reversal\n"
        "• <code>$hush</code>   : Direct communication block\n"
        "• <code>$eject</code>  : Cluster member removal\n"
        "• <code>$grant</code>  : Privilege escalation\n"
        "• <code>$revoke</code> : Privilege revocation\n"
        "• <code>$push</code>   : Global packet broadcast\n"
        "• <code>$node status</code> : Hardware diagnosis\n"
        "• <code>$node logs</code>   : Internal log stream\n\n"

        "<b>External Nodes</b> — <code>.</code>\n"
        "• <code>.wlc</code>      : Entrance protocol config\n"
        "• <code>.autodl</code>   : Automated capture config\n"
        "• <code>.speedtest</code> : Bandwidth verification\n"
    )




    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=helpowner_keyboard()
    )

async def helpowner_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    if q.data != "helpowner:close":
        return

    try:
        await q.message.delete()
    except Exception:
        pass
