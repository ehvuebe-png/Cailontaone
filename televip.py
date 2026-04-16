import asyncio
import random
import os
import httpx
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from telegram.error import RetryAfter, TelegramError

FloodControl = RetryAfter

OWNER_ID = 6924956412
ADMIN_LIST = {OWNER_ID} 
CAM_LIST = set()
RUNNING_CHATS = {} 
ALL_BOTS = [] 
DELAY_SPAM = 0.3

async def get_tokens():
    url = "https://raw.githubusercontent.com/ehvuebe-png/Cailontaone/main/tk.txt"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                tokens = [t.strip() for t in response.text.splitlines() if t.strip()]
                return tokens
    except:
        pass
    return []

async def get_nhay_web():
    url = "https://raw.githubusercontent.com/ehvuebe-png/Cailontaone/main/nhay.txt"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                return [l.strip() for l in response.text.splitlines() if l.strip()]
    except:
        pass
    return []

def get_ngon_full():
    try:
        with open('ngon.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except: return ""

def write_ngon(content):
    with open('ngon.txt', 'w', encoding='utf-8') as f:
        f.write(content)

async def safe_send(bot, chat_id, text_content):
    """Gửi tin thông minh: Chống delay, chống flood, tự phục hồi"""
    try:
        await bot.send_message(chat_id=chat_id, text=text_content, parse_mode=ParseMode.HTML)
    except FloodControl as e:
        await asyncio.sleep(e.retry_after)
        try:
            await bot.send_message(chat_id=chat_id, text=text_content, parse_mode=ParseMode.HTML)
        except: pass
    except TelegramError:
        pass
    except:
        pass

async def spam_worker(bot, chat_id, text_source, target_tag, is_nhay=False):
    """Mỗi con bot là một chiến thần riêng biệt, bốc câu ngẫu nhiên"""
    while RUNNING_CHATS.get(chat_id):
        if is_nhay:
            line = random.choice(text_source)
            msg = f"{line}{target_tag}"
        else:
            msg = f"{text_source}{target_tag}"
            
        await safe_send(bot, chat_id, msg)
        
        wait_time = random.uniform(DELAY_SPAM, DELAY_SPAM + 0.15)
        await asyncio.sleep(wait_time)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_LIST: return
    RUNNING_CHATS[update.effective_chat.id] = False
    await update.message.reply_text("dừng treo", parse_mode=ParseMode.MARKDOWN)

async def nhay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_user.id not in ADMIN_LIST: return
    RUNNING_CHATS[chat_id] = True
    try:
        target_id = context.args[0]
        lines = get_nhay()
        if not lines: return
        await update.message.reply_text("treo nhây")
        while RUNNING_CHATS.get(chat_id):
            for line in lines:
                if not RUNNING_CHATS.get(chat_id): break
                icons = "=))" * random.randint(3, 7)
                msg = f"<b>{line} {icons}</b><a href='tg://user?id={target_id}'>\u200b</a>"
             
                for bot in ALL_BOTS:
                    asyncio.create_task(bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.HTML))
                
                await asyncio.sleep(0.3) 
    except: pass

async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_user.id not in ADMIN_LIST: return
    
    full_text = get_ngon_full()
    if not full_text: return
    
    RUNNING_CHATS[chat_id] = True
    target_tag = f" <a href='tg://user?id={context.args[0]}'>\u200b</a>" if context.args else ""
    
    await update.message.reply_text("treo ngôn")
    for bot in ALL_BOTS:
        asyncio.create_task(spam_worker(bot, chat_id, full_text, target_tag, is_nhay=False))

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_LIST: return
    menu_text = (
        "•<b> LÃO THIÊN WAR BOT </b>\n\n"
        "• <code>nhay &lt;id&gt;</code> treo nhây\n"
        "• <code>spam &lt;id&gt;</code> treo ngôn\n"
        "• <code>stop</code> dừng bot\n\n"
        "•<b>Đeo rọ cho chó</b>\n"
        "• <code>cam &lt;id&gt;</code> khoá mõm chó\n"
        "• <code>sua &lt;id&gt;</code> mở mõm\n\n"
        "• <b>Lặt vặt</b>\n"
        "• <code>upngon &lt;ngon&gt;</code> thay ngôn treo\n"
        "• <code>delay &lt;số&gt;</code> chỉnh tốc độ treo\n"
        "• <code>add &lt;id&gt;</code> thêm adm\n"
        "• <code>xoa &lt;id&gt;</code> xóa adm\n\n"
        "<b>ADMIN: Lão Thiên</b>"
    )
    await update.message.reply_text(menu_text, parse_mode=ParseMode.HTML)

async def upngon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_LIST: return
    parts = update.message.text.split(None, 1)
    if len(parts) >= 2:
        write_ngon(parts[1])
        await update.message.reply_text(" Đã cập nhật ngôn treo")

async def set_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DELAY_SPAM
    if update.effective_user.id not in ADMIN_LIST: return
    try:
        val = float(context.args[0])
        DELAY_SPAM = val
        await update.message.reply_text(f"để delay {val}s")
    except: pass

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        target = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        ADMIN_LIST.add(target)
        await update.message.reply_text(f" Đã thêm Admin: {target}")
    except: pass

async def xoa_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        target = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        if target == OWNER_ID: return
        ADMIN_LIST.discard(target)
        await update.message.reply_text(f" Đã xóa Admin: {target}")
    except: pass

async def anti_flood_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in CAM_LIST:
        try: await update.message.delete()
        except: pass

async def start_instance(token, is_admin=False):
    req = HTTPXRequest(connect_timeout=15, read_timeout=15, connection_pool_size=1000)
    app = ApplicationBuilder().token(token).request(req).build()
    ALL_BOTS.append(app.bot)
    
    app.add_handler(CommandHandler("stop", stop, block=False))
    
    if is_admin:
        app.add_handler(CommandHandler("menu", menu, block=False))
        app.add_handler(CommandHandler("nhay", nhay_cmd, block=False))
        app.add_handler(CommandHandler("spam", spam_cmd, block=False))
        app.add_handler(CommandHandler("upngon", upngon, block=False))
        app.add_handler(CommandHandler("delay", set_delay, block=False))
        app.add_handler(CommandHandler("add", add_admin, block=False))
        app.add_handler(CommandHandler("xoa", xoa_admin, block=False))
        app.add_handler(CommandHandler("cam", lambda u, c: CAM_LIST.add(int(c.args[0])) if c.args else (CAM_LIST.add(u.message.reply_to_message.from_user.id) if u.message.reply_to_message else None), block=False))
        app.add_handler(CommandHandler("sua", lambda u, c: CAM_LIST.discard(int(c.args[0])) if c.args else (CAM_LIST.discard(u.message.reply_to_message.from_user.id) if u.message.reply_to_message else None), block=False))
    
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, anti_flood_delete, block=False))
    
    try:
        await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
        print(f"[✔] Bot {token[:8]} Online!")
    except: pass

async def main():
    tokens = await get_tokens()
    if not tokens: return
    tasks = [start_instance(tokens[0], is_admin=True)]
    for t in tokens[1:]:
        tasks.append(start_instance(t))
    await asyncio.gather(*tasks)
    while True: await asyncio.sleep(3600)

if __name__ == '__main__':
    try: asyncio.run(main())
    except: pass

