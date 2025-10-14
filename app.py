from flask import Flask, request, redirect, url_for, session, render_template_string
import json, os, re, time, datetime

# ---------- CONFIG ----------
APP_SECRET = os.environ.get("KG_SECRET", "kelajakgram_dev_secret_key")
app = Flask(__name__)
app.secret_key = APP_SECRET

# Fayl nomlari
USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"
NEWS_FILE = "news.json"
SUPPORT_FILE = "support.json"
CHANNELS_FILE = "channels.json"
GROUPS_FILE = "groups.json"

# Creator
CREATOR_EMAIL = "toshpolatovm71@gmail.com"
CREATOR_PASSWORD = "muhammadali-specialkey-09"
CREATOR_NAME = "Muhammadali Toshpoʻlatov"
CREATOR_PRIMARY = "muhammadali"
CREATOR_USERNAMES = ["kelajakgramuz","theowner","chatuz","creator","uzbekistan","kelajak","owner","theking","muhammadali"]

# System accounts
SYSTEM_ACCOUNTS = {
    "ai": {"name":"Support Kelajak", "usernames":["support","openai","chatgpt","kelajakgramai","superbot"], "role":"support"},
    "global": {"name":"Global Chat", "usernames":["globalchat","global_chat","globaluz","kelajakgramchat","chatuz","uzbekistanchat"], "role":"chat"},
    "news": {"name":"KelajakGram News", "usernames":["kelajakgram","kelajak","uzgram","kelajakgramnews"], "role":"news"}
}

USERNAME_RE = re.compile(r'^[a-z_]+$')  # username faqat a-z va _ bo'lishi mumkin

# ---------- JSON helpers ----------
def load_json(path, default):
    if not os.path.exists(path):
        with open(path,"w",encoding="utf-8") as f:
            json.dump(default,f,ensure_ascii=False,indent=2)
        return default
    with open(path,"r",encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(path, data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# ---------- Data stores ----------
users = load_json(USERS_FILE,{})
messages = load_json(MESSAGES_FILE,[])
news = load_json(NEWS_FILE,[])
support_items = load_json(SUPPORT_FILE,[])
channels = load_json(CHANNELS_FILE,{})
groups = load_json(GROUPS_FILE,{})

def save_users(): save_json(USERS_FILE, users)
def save_messages(): save_json(MESSAGES_FILE, messages)
def save_news(): save_json(NEWS_FILE, news)
def save_support(): save_json(SUPPORT_FILE, support_items)
def save_channels(): save_json(CHANNELS_FILE, channels)
def save_groups(): save_json(GROUPS_FILE, groups)

# ---------- Ensure creator ----------
def ensure_creator():
    if CREATOR_EMAIL not in users:
        users[CREATOR_EMAIL] = {
            "name": CREATOR_NAME,
            "email": CREATOR_EMAIL,
            "password": CREATOR_PASSWORD,
            "usernames": CREATOR_USERNAMES+[CREATOR_PRIMARY],
            "role": "creator",
            "online": False,
            "joined": datetime.datetime.now().isoformat()
        }
        save_users()
ensure_creator()

# ---------- Helpers ----------
def current_user():
    em = session.get("user_email")
    if not em: return None
    return users.get(em)

def mark_online(email):
    if email in users:
        users[email]['online']=True
        users[email]['last_seen']=time.time()
        save_users()
def mark_offline(email):
    if email in users:
        users[email]['online']=False
        users[email]['last_seen']=time.time()
        save_users()

def next_id():
    return int(time.time()*1000)

def find_by_username(uname):
    u = uname.lstrip("@").lower()
    # Users
    for email, info in users.items():
        if u in [x.lower() for x in info.get("usernames", [])]:
            return ("user", email, info)
    # System accounts
    for key, info in SYSTEM_ACCOUNTS.items():
        if u in [x.lower() for x in info["usernames"]]:
            return ("system", key, info)
    # Channels
    if u in channels:
        return ("channel", u, channels[u])
    # Groups
    if u in groups:
        return ("group", u, groups[u])
    return (None, None, None)

def is_username_taken(username):
    uname = username.lower()
    for uinfo in users.values():
        if uname in [x.lower() for x in uinfo.get("usernames",[])]:
            return True
    for info in SYSTEM_ACCOUNTS.values():
        if uname in [x.lower() for x in info["usernames"]]:
            return True
    if uname in channels or uname in groups:
        return True
    return False

# ---------- BASE STYLE ----------
BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body{font-family:Inter, Arial, sans-serif;background:#f6f8fb;margin:0;padding:12px;color:#111}
 .wrap{max-width:900px;margin:0 auto}
 h1{font-size:28px}
 h2{font-size:20px}
 .card{background:#fff;padding:14px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06);margin:12px 0}
 .btn{display:inline-block;padding:10px 14px;border-radius:10px;background:#0b84ff;color:#fff;text-decoration:none;margin:6px 6px;font-size:16px}
 label{display:block;font-weight:600;margin-top:8px}
 input[type=text], input[type=password], input[type=email], textarea{width:100%;padding:12px;font-size:16px;border-radius:8px;border:1px solid #ddd}
 .small{font-size:14px;color:#666}
 .msg{padding:10px;border-radius:10px;margin-bottom:8px;background:#fff;border:1px solid #eef}
 .online{color:green;font-weight:700}
 .offline{color:#666}
 .danger{color:#b00020;font-weight:700}
 .muted{color:#666}
</style>
"""

# ---------- HOME ----------
@app.route("/")
def home():
    user = current_user()
    user_html = ""
    if user:
        user_html = f"<div class='small'>Siz: <b>{user['name']}</b> • @{user['usernames'][0]} • <span class='online'>online</span></div>"
    content = BASE_STYLE + f"""
    <div class='wrap'>
      <h1>🌐 KelajakGram</h1>
      {user_html}
      <div class='card'>
        <form action='/search' method='get'>
          <input name='q' placeholder='Foydalanuvchi, kanal yoki guruh username kiriting' />
          <div style='margin-top:8px'><button class='btn' type='submit'>🔍 Qidirish</button></div>
        </form>
      </div>
      <div class='card'>
        <a class='btn' href='/global'>🌍 Global Chat (@globalchat)</a>
        <a class='btn' href='/support'>💬 Support Kelajak (@support)</a>
        <a class='btn' href='/news'>📰 KelajakGram News (@kelajakgram)</a>
        { "<a class='btn' href='/create_channel'>➕ Kanal yaratish</a>" if user and user.get("role")=="creator" else "" }
        { "<a class='btn' href='/create_group'>➕ Guruh yaratish</a>" if user and user.get("role")=="creator" else "" }
        <a class='btn' href='/register'>➕ Ro'yxatdan o'tish</a>
        { "<a class='btn' href='/settings'>⚙️ Sozlamalar</a>" if user else "" }
        { "<a class='btn' href='/logout'>🔒 Chiqish</a>" if user else "" }
      </div>
    </div>
    """
    return render_template_string(content)

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        username_raw = request.form.get("username","").strip().lower()
        password = request.form.get("password","").strip()
        username = username_raw.lstrip("@")
        if not name or not email or not username or not password:
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Iltimos barcha maydonlarni to'ldiring.</div>")
        if not USERNAME_RE.match(username):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username qabul qilinmaydi!</div>")
        if is_username_taken(username):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username allaqachon band!</div>")
        users[email] = {"name":name,"email":email,"password":password,"usernames":[username],"role":"user","online":True,"joined":datetime.datetime.now().isoformat()}
        save_users()
        session["user_email"]=email
        mark_online(email)
        return redirect(url_for("home"))
    return render_template_string(BASE_STYLE+"""
    <div class='wrap'>
      <div class='card'>
        <h2>➕ Ro'yxatdan o'tish</h2>
        <form method='post'>
          <label>Ism</label><input name='name' required>
          <label>Email</label><input name='email' type='email' required>
          <label>Username</label><input name='username' required>
          <label>Parol</label><input name='password' type='password' required>
          <div style='margin-top:10px'><button class='btn' type='submit'>Ro'yxatdan o'tish</button></div>
        </form>
      </div>
    </div>
    """)

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","").strip()
        user = users.get(email)
        if not user:
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Foydalanuvchi topilmadi.</div>")
        if user.get("password")==password or (email==CREATOR_EMAIL and password==CREATOR_PASSWORD):
            session["user_email"]=email
            mark_online(email)
            return redirect(url_for("home"))
        return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Parol noto'g'ri.</div>")
    return render_template_string(BASE_STYLE+"""
    <div class='wrap'>
      <div class='card'>
        <h2>Kirish</h2>
        <form method='post'>
          <label>Email</label><input name='email' type='email' required>
          <label>Parol</label><input name='password' type='password' required>
          <div style='margin-top:10px'><button class='btn' type='submit'>Kirish</button></div>
        </form>
      </div>
    </div>
    """)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    em = session.get("user_email")
    if em: mark_offline(em)
    session.clear()
    return redirect(url_for("home"))

# ---------- CREATE CHANNEL ----------
@app.route("/create_channel", methods=["GET","POST"])
def create_channel():
    user = current_user()
    if not user or user.get("role")!="creator":
        return redirect(url_for("home"))
    if request.method=="POST":
        name = request.form.get("name","").strip()
        uname = request.form.get("username","").strip().lower().lstrip("@")
        if not name or not uname:
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Barcha maydonlarni to'ldiring!</div>")
        if not USERNAME_RE.match(uname):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username qabul qilinmaydi!</div>")
        if is_username_taken(uname):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username allaqachon band!</div>")
        channels[uname] = {"name":name,"username":uname,"creator":user['email'],"joined":datetime.datetime.now().isoformat()}
        save_channels()
        return redirect(url_for("home"))
    return render_template_string(BASE_STYLE+"""
    <div class='wrap'>
      <div class='card'>
        <h2>➕ Kanal yaratish</h2>
        <form method='post'>
          <label>Kanal nomi</label><input name='name' required>
          <label>Username</label><input name='username' required>
          <div style='margin-top:10px'><button class='btn' type='submit'>Yaratish</button></div>
        </form>
      </div>
    </div>
    """)

# ---------- CREATE GROUP ----------
@app.route("/create_group", methods=["GET","POST"])
def create_group():
    user = current_user()
    if not user or user.get("role")!="creator":
        return redirect(url_for("home"))
    if request.method=="POST":
        name = request.form.get("name","").strip()
        uname = request.form.get("username","").strip().lower().lstrip("@")
        if not name or not uname:
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Barcha maydonlarni to'ldiring!</div>")
        if not USERNAME_RE.match(uname):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username qabul qilinmaydi!</div>")
        if is_username_taken(uname):
            return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Bunday username allaqachon band!</div>")
        groups[uname] = {"name":name,"username":uname,"creator":user['email'],"joined":datetime.datetime.now().isoformat()}
        save_groups()
        return redirect(url_for("home"))
    return render_template_string(BASE_STYLE+"""
    <div class='wrap'>
      <div class='card'>
        <h2>➕ Guruh yaratish</h2>
        <form method='post'>
          <label>Guruh nomi</label><input name='name' required>
          <label>Username</label><input name='username' required>
          <div style='margin-top:10px'><button class='btn' type='submit'>Yaratish</button></div>
        </form>
      </div>
    </div>
    """)
# ---------- GLOBAL CHAT ----------
@app.route("/global", methods=["GET","POST"])
def global_chat():
    user = current_user()
    if not user: return redirect(url_for("login"))
    global messages
    if request.method=="POST":
        text = request.form.get("text","").strip()
        if text:
            messages.append({
                "id": next_id(),
                "from": user['email'],
                "to": "global",
                "text": text,
                "time": datetime.datetime.now().isoformat()
            })
            save_messages()
        return redirect(url_for("global_chat"))
    chat_html=""
    for msg in [m for m in messages if m['to']=="global"]:
        sender = users.get(msg['from'],{"name":"System"})
        chat_html += f"<div class='msg'><b>{sender['name']}</b>: {msg['text']} <span class='small'>{msg['time'].split('T')[1][:8]}</span></div>"
    return render_template_string(BASE_STYLE+f"""
    <div class='wrap'>
      <h2>🌍 Global Chat</h2>
      <form method='post'>
        <textarea name='text' placeholder='Xabar yozing...' required></textarea>
        <div style='margin-top:6px'><button class='btn' type='submit'>Yuborish</button></div>
      </form>
      <div style='margin-top:12px'>{chat_html}</div>
      <a class='btn' href='/'>⬅️ Orqaga</a>
    </div>
    """)

# ---------- SUPPORT ----------
@app.route("/support", methods=["GET","POST"])
def support():
    user = current_user()
    if not user: return redirect(url_for("login"))
    global support_items
    if request.method=="POST":
        text = request.form.get("text","").strip()
        if text:
            support_items.append({
                "id": next_id(),
                "from": user['email'],
                "text": text,
                "time": datetime.datetime.now().isoformat()
            })
            save_support()
        return redirect(url_for("support"))
    support_html=""
    for s in support_items:
        sender = users.get(s['from'],{"name":"System"})
        support_html += f"<div class='msg'><b>{sender['name']}</b>: {s['text']} <span class='small'>{s['time'].split('T')[1][:8]}</span></div>"
    return render_template_string(BASE_STYLE+f"""
    <div class='wrap'>
      <h2>💬 Support Kelajak</h2>
      <form method='post'>
        <textarea name='text' placeholder='Savol yoki muammo yozing...' required></textarea>
        <div style='margin-top:6px'><button class='btn' type='submit'>Yuborish</button></div>
      </form>
      <div style='margin-top:12px'>{support_html}</div>
      <a class='btn' href='/'>⬅️ Orqaga</a>
    </div>
    """)

# ---------- NEWS ----------
@app.route("/news", methods=["GET","POST"])
def news_feed():
    user = current_user()
    if not user: return redirect(url_for("login"))
    global news
    if request.method=="POST" and user.get("role")=="creator":
        text = request.form.get("text","").strip()
        if text:
            news.append({
                "id": next_id(),
                "from": user['email'],
                "text": text,
                "time": datetime.datetime.now().isoformat()
            })
            save_news()
        return redirect(url_for("news_feed"))
    news_html=""
    for n in reversed(news):
        sender = users.get(n['from'],{"name":"System"})
        news_html += f"<div class='msg'><b>{sender['name']}</b>: {n['text']} <span class='small'>{n['time'].split('T')[1][:8]}</span></div>"
    post_form=""
    if user.get("role")=="creator":
        post_form="""
        <form method='post'>
            <textarea name='text' placeholder='Yangilik yozing...' required></textarea>
            <div style='margin-top:6px'><button class='btn' type='submit'>Yuborish</button></div>
        </form>
        """
    return render_template_string(BASE_STYLE+f"""
    <div class='wrap'>
      <h2>📰 KelajakGram News</h2>
      {post_form}
      <div style='margin-top:12px'>{news_html}</div>
      <a class='btn' href='/'>⬅️ Orqaga</a>
    </div>
    """)

# ---------- PROFILE ----------
@app.route("/profile/<uname>")
def profile(uname):
    typ,key,info = find_by_username(uname)
    if not info: return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Topilmadi!</div>")
    online_status = "<span class='online'>online</span>" if info.get("online", False) else "<span class='offline'>offline</span>"
    usernames = " ".join([f"@{u}" for u in info.get("usernames",[])])
    return render_template_string(BASE_STYLE+f"""
    <div class='wrap'>
      <h2>Profil: {info.get('name')}</h2>
      <div class='card'>
        <b>Username:</b> {usernames}<br>
        <b>Status:</b> {online_status}<br>
        <b>Rol:</b> {info.get('role','user')}<br>
        <b>Qo‘shilgan vaqti:</b> {info.get('joined')}
      </div>
      <a class='btn' href='/'>⬅️ Orqaga</a>
    </div>
    """)

# ---------- SEARCH ----------
@app.route("/search")
def search():
    q = request.args.get("q","").strip().lower()
    if not q:
        return redirect(url_for("home"))
    typ,key,info = find_by_username(q)
    if not info:
        return render_template_string(BASE_STYLE+"<div class='wrap card danger'>Hech nima topilmadi!</div>")
    return redirect(url_for("profile", uname=q))
    # ---------- SETTINGS ----------
@app.route("/settings", methods=["GET","POST"])
def settings():
    user = current_user()
    if not user: return redirect(url_for("login"))

    if request.method=="POST":
        name = request.form.get("name","").strip()
        username = request.form.get("username","").strip().lower().lstrip("@")
        old_password = request.form.get("old_password","").strip()
        new_password = request.form.get("new_password","").strip()
        errors = []

        # Username tekshirish
        if username != user['usernames'][0]:
            if not USERNAME_RE.match(username):
                errors.append("Username faqat kichik harf va '_' belgilaridan iborat bo‘lishi kerak.")
            # Band bo‘lganlarni tekshirish (foydalanuvchilar, system, kanallar, guruhlar)
            for u in users.values():
                if username in [un.lower() for un in u.get("usernames",[])] and u['email']!=user['email']:
                    errors.append("Bunday username band qilingan!")
            for info in SYSTEM_ACCOUNTS.values():
                if username in [un.lower() for un in info["usernames"]]:
                    errors.append("Bunday username system tomonidan band qilingan!")
            if username in channels or username in groups:
                errors.append("Bunday username kanal yoki guruh tomonidan band qilingan!")

        # Parolni o‘zgartirish
        if new_password:
            if old_password != user['password']:
                errors.append("Eski parol noto‘g‘ri!")

        if errors:
            error_html = "<br>".join(errors)
            return render_template_string(BASE_STYLE+f"<div class='wrap card danger'>{error_html}</div>")

        # Ma'lumotlarni yangilash
        user['name']=name
        user['usernames']=[username]
        if new_password: user['password']=new_password
        save_users()
        return redirect(url_for("settings"))

    return render_template_string(BASE_STYLE+f"""
    <div class='wrap'>
      <h2>⚙️ Sozlamalar</h2>
      <form method='post'>
        <label>Ism</label>
        <input name='name' value='{user['name']}' required>
        <label>Username</label>
        <input name='username' value='{user['usernames'][0]}' required>
        <label>Eski Parol (faqat o‘zgartirmoqchi bo‘lsangiz)</label>
        <input name='old_password' type='password'>
        <label>Yangi Parol</label>
        <input name='new_password' type='password'>
        <div style='margin-top:10px'>
          <button class='btn' type='submit'>Saqlash</button>
        </div>
      </form>
      <a class='btn' href='/'>⬅️ Orqaga</a>
    </div>
    """)
# ---------- RUN ----------
if __name__=="__main__":
    app.run(debug=True)
