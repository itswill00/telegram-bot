from telegram.ext import CommandHandler, PrefixHandler

from handlers.networking import whoisdomain_cmd, ip_cmd, domain_cmd
from handlers.broadcast import broadcast_cmd
from handlers.start import start_cmd
from handlers.tr import tr_cmd, trlist_cmd
from handlers.restart import restart_cmd
from handlers.gsearch import gsearch_cmd
from handlers.stats import stats_cmd
from handlers.help import help_cmd
from handlers.speedtest import speedtest_cmd
from handlers.ping import ping_cmd
from handlers.weather import weather_cmd
from handlers.dl.handlers import dl_cmd, autodl_cmd
from handlers.welcome import wlc_cmd, start_verify_pm
from handlers.ship import ship_cmd
from handlers.reminder import reminder_cmd
from handlers.gemini import ai_cmd
from handlers.groq import groq_query
from handlers.quiz import quiz_cmd
from handlers.premium import premium_cmd
from handlers.waifu import waifu_cmd
from handlers.update import update_cmd
from handlers.groups import groups_cmd
from handlers.music import music_cmd
from handlers.kurs import kurs_cmd
from handlers.net import net_cmd
from handlers.cookies import cookies_cmd
from handlers.donate import donate_cmd
from handlers.quotly import q_cmd
from handlers.kang import kang_cmd
from handlers.setting import setting_cmd
from handlers.dl.instagram_scrape import ig_cmd

from handlers.moderation import (
    moderation_cmd, 
    ban_cmd, 
    unban_cmd, 
    mute_cmd, 
    unmute_cmd,
    kick_cmd,
    addsudo_cmd,
    rmsudo_cmd,
    sudolist_cmd,
)

from handlers.admin_panel import admin_cmd
from handlers.owner_tools import eval_cmd, sh_cmd, ban_cmd, unban_cmd
from handlers.owner_env import env_cmd
from handlers.owner_sys import sys_cmd
from handlers.helpowner import helpowner_cmd
from handlers.owner_backup import direct_backup_cmd
from handlers.owner_restore import restore_cmd
from handlers.owner_hotreload import hotreload_cmd

# Admin commands use '$' prefix with a unique technical naming style
ADMIN_COMMANDS = [
    ("core", admin_cmd, False),
    ("py", eval_cmd, False),
    ("sh", sh_cmd, False),
    ("cfg", env_cmd, False),
    ("node", sys_cmd, False),
    ("dump", direct_backup_cmd, False),
    ("load", restore_cmd, False),
    ("live", hotreload_cmd, False),
    ("root", helpowner_cmd, False),
    ("hush", mute_cmd, False),
    ("speak", unmute_cmd, False),
    ("purge", ban_cmd, False),
    ("revive", unban_cmd, False),
    ("eject", kick_cmd, False),
    ("grant", addsudo_cmd, False),
    ("revoke", rmsudo_cmd, False),
    ("trusted", sudolist_cmd, False),
    ("nodes", groups_cmd, False),
    ("sync", update_cmd, False),
    ("push", broadcast_cmd, False),
    ("meter", stats_cmd, False),
    ("reboot", restart_cmd, False),
]


# Public commands use '.' prefix to avoid collisions
COMMAND_HANDLERS = [
    ("start", start_cmd, True),
    ("settings", setting_cmd, False),
    ("q", q_cmd, False),
    ("ig", ig_cmd, False),
    ("kang", kang_cmd, False),
    ("net", net_cmd, False),
    ("donate", donate_cmd, False),
    ("start", start_verify_pm, False),
    ("kurs", kurs_cmd, False),
    ("music", music_cmd, False),
    ("autodl", autodl_cmd, False),
    ("waifu", waifu_cmd, False),
    ("premium", premium_cmd, False),
    ("quiz", quiz_cmd, False),
    ("ship", ship_cmd, True),
    ("reminder", reminder_cmd, False),
    ("help", help_cmd, True),
    ("menu", help_cmd, True),
    ("ping", ping_cmd, True),
    ("ip", ip_cmd, True),
    ("whoisdomain", whoisdomain_cmd, True),
    ("domain", domain_cmd, True),
    ("tr", tr_cmd, True),
    ("trlist", trlist_cmd, True),
    ("wlc", wlc_cmd, True),
    ("ask", ai_cmd, False),
    ("groq", groq_query, False),
    ("weather", weather_cmd, False),
    ("speedtest", speedtest_cmd, False),
    ("gsearch", gsearch_cmd, False),
    ("dl", dl_cmd, False),
]

def register_commands(app):
    # Register Admin Commands with '$' prefix but new names
    for name, handler, blocking in ADMIN_COMMANDS:
        app.add_handler(
            PrefixHandler("$", name, handler, block=blocking),
            group=-1
        )
    
    # Register Public Commands with '.' prefix to avoid collisions
    for name, handler, blocking in COMMAND_HANDLERS:
        app.add_handler(
            PrefixHandler(".", name, handler, block=blocking),
            group=-1
        )
