import os
import json
import random
import asyncio
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
)

TOKEN = os.environ.get("BOT_TOKEN", "ВСТАВЬ_ТОКЕН_СЮДА")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # твой Telegram ID

# ═══════════════════════════════════════════
#  БАЗА ВОПРОСОВ
# ═══════════════════════════════════════════
QUESTIONS = {
    "flags": {
        "name": "🚩 Флаги",
        "easy": [
            {"q": "Белый фон с красным кругом. Чей флаг?",
             "a": ["Китай", "Япония", "Корея", "Вьетнам"], "c": 1,
             "fact": "🇯🇵 Япония! Красный круг — восходящее солнце."},
            {"q": "Красно-белый флаг с кленовым листом. Что за страна?",
             "a": ["США", "Австралия", "Канада", "Финляндия"], "c": 2,
             "fact": "🇨🇦 Канада! Кленовый лист — символ страны с 1965 года."},
            {"q": "Три полосы: белая, синяя, красная. Чей флаг?",
             "a": ["Франция", "Нидерланды", "Россия", "Хорватия"], "c": 2,
             "fact": "🇷🇺 Россия! Триколор введён при Петре I в 1696 году."},
            {"q": "Зелёный фон, жёлтый ромб, синий шар. Какая страна?",
             "a": ["Аргентина", "Колумбия", "Бразилия", "Перу"], "c": 2,
             "fact": "🇧🇷 Бразилия! Звёзды на флаге — созвездия бразильского неба."},
        ],
        "medium": [
            {"q": "Флаг с Y-образным зелёным клином и 6 цветами. Какая страна?",
             "a": ["Нигерия", "Кения", "ЮАР", "Зимбабве"], "c": 2,
             "fact": "🇿🇦 ЮАР! Принят в 1994 году после окончания апартеида."},
            {"q": "Единственный нетрапециевидный флаг в мире — два треугольника.",
             "a": ["Бутан", "Непал", "Шри-Ланка", "Монголия"], "c": 1,
             "fact": "🇳🇵 Непал! Форма флага уникальна — два вымпела."},
            {"q": "Красно-зелёный флаг с орнаментом. Восточная Европа.",
             "a": ["Польша", "Беларусь", "Украина", "Латвия"], "c": 1,
             "fact": "🇧🇾 Беларусь! Орнамент — традиционный белорусский узор."},
        ],
        "hard": [
            {"q": "Зелёный фон, красная рамка, белый полумесяц. Островное государство.",
             "a": ["Шри-Ланка", "Мальдивы", "Сейшелы", "Маврикий"], "c": 1,
             "fact": "🇲🇻 Мальдивы! Самая низколежащая страна — средняя высота 1.5 м."},
            {"q": "Флаг с зелёной звездой на жёлтой полосе. Небольшая страна Южной Америки.",
             "a": ["Гайана", "Суринам", "Тринидад", "Белиз"], "c": 1,
             "fact": "🇸🇷 Суринам! Единственная страна ЮА без часового пояса UTC-4."},
        ]
    },
    "capitals": {
        "name": "🏛️ Столицы",
        "easy": [
            {"q": "Столица Франции?",
             "a": ["Лион", "Марсель", "Париж", "Бордо"], "c": 2,
             "fact": "🗼 Париж! Основан в III веке до н.э. как Лютеция."},
            {"q": "Столица Японии?",
             "a": ["Осака", "Токио", "Киото", "Нагоя"], "c": 1,
             "fact": "🏯 Токио! Стал столицей в 1869 году, заменив Киото."},
            {"q": "Столица Австралии?",
             "a": ["Сидней", "Мельбурн", "Брисбен", "Канберра"], "c": 3,
             "fact": "🦘 Канберра! Построена как компромисс между Сиднеем и Мельбурном."},
            {"q": "Столица Египта?",
             "a": ["Александрия", "Каир", "Луксор", "Асуан"], "c": 1,
             "fact": "🕌 Каир! Крупнейший город Африки — более 20 млн жителей."},
        ],
        "medium": [
            {"q": "Самая высокогорная столица в мире находится в:",
             "a": ["Перу", "Колумбия", "Боливия", "Эквадор"], "c": 2,
             "fact": "🏔️ Боливия! Ла-Пас на высоте 3640 м — резиденция правительства."},
            {"q": "Столица Казахстана называется:",
             "a": ["Алматы", "Шымкент", "Астана", "Актау"], "c": 2,
             "fact": "🏙️ Астана! Стала столицей в 1997 году (ранее — Нур-Султан)."},
        ],
        "hard": [
            {"q": "Конституционная столица ЮАР — это:",
             "a": ["Йоханнесбург", "Кейптаун", "Претория", "Дурбан"], "c": 1,
             "fact": "🏛️ Кейптаун! У ЮАР три столицы: Кейптаун, Претория и Блумфонтейн."},
            {"q": "Nuku'alofa — столица какого государства?",
             "a": ["Фиджи", "Самоа", "Тонга", "Вануату"], "c": 2,
             "fact": "🌺 Тонга! Единственная монархия в Тихом океане."},
        ]
    },
    "nature": {
        "name": "🌿 Природа",
        "easy": [
            {"q": "Страна с наибольшим числом вулканов в мире?",
             "a": ["Япония", "Россия", "Индонезия", "Чили"], "c": 2,
             "fact": "🌋 Индонезия! Более 130 активных вулканов."},
            {"q": "Самый длинный речной бассейн — Амазонка — в основном в:",
             "a": ["Аргентине", "Колумбии", "Бразилии", "Перу"], "c": 2,
             "fact": "🌊 Бразилия! Около 60% бассейна Амазонки — в Бразилии."},
            {"q": "Самое глубокое озеро в мире?",
             "a": ["Ладожское", "Байкал", "Онежское", "Каспий"], "c": 1,
             "fact": "🧊 Байкал! Глубина 1642 м, содержит 20% пресной воды мира."},
        ],
        "medium": [
            {"q": "В какой стране находится Эверест?",
             "a": ["Тибет", "Индия", "Непал", "Китай"], "c": 2,
             "fact": "🏔️ Непал! Эверест (8849 м) — на границе Непала и Китая."},
            {"q": "Страна с наибольшим % лесов в Европе?",
             "a": ["Норвегия", "Финляндия", "Швеция", "Россия"], "c": 1,
             "fact": "🌲 Финляндия! 73% территории — леса."},
        ],
        "hard": [
            {"q": "Страна с крупнейшим ледником (кроме Антарктики)?",
             "a": ["Канада", "Россия", "Гренландия", "Норвегия"], "c": 2,
             "fact": "🧊 Гренландия! Ледяной щит покрывает 80% острова."},
        ]
    },
    "culture": {
        "name": "🎭 Культура",
        "easy": [
            {"q": "Статуя Свободы подарена США какой страной?",
             "a": ["Германия", "Великобритания", "Франция", "Испания"], "c": 2,
             "fact": "🗽 Франция! Подарена в 1886 году."},
            {"q": "Страна, подарившая миру рок-н-ролл и джаз?",
             "a": ["Великобритания", "Австралия", "Канада", "США"], "c": 3,
             "fact": "🎸 США! Джаз родился в Новом Орлеане в начале XX века."},
        ],
        "medium": [
            {"q": "Страна с наибольшим числом объектов ЮНЕСКО?",
             "a": ["Греция", "Китай", "Испания", "Италия"], "c": 3,
             "fact": "🏛️ Италия! 58 объектов ЮНЕСКО — больше всех в мире."},
            {"q": "Самый знаменитый карнавал мира проходит в:",
             "a": ["Буэнос-Айрес", "Лима", "Рио-де-Жанейро", "Богота"], "c": 2,
             "fact": "🎪 Рио-де-Жанейро! Ежегодно собирает 5 млн участников."},
        ],
        "hard": [
            {"q": "Первая в мире письменность появилась в:",
             "a": ["Египет", "Китай", "Иран", "Ирак"], "c": 3,
             "fact": "📜 Ирак (Месопотамия)! Шумерская клинопись — около 3200 лет до н.э."},
            {"q": "Бумага и книгопечатание впервые появились в:",
             "a": ["Японии", "Корее", "Вьетнаме", "Китае"], "c": 3,
             "fact": "📚 Китай! Бумага — 105 г. н.э., книгопечатание — IX век."},
        ]
    }
}

LEVELS = {
    "easy":   {"name": "🟢 Лёгкий",  "points": 10, "questions": 5},
    "medium": {"name": "🟡 Средний", "points": 20, "questions": 7},
    "hard":   {"name": "🔴 Сложный", "points": 35, "questions": 10},
}

# ═══════════════════════════════════════════
#  ХРАНИЛИЩЕ ДАННЫХ (JSON файл)
# ═══════════════════════════════════════════
DB_FILE = "data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "leaderboard": {}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(db, user_id):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": "",
            "total_score": 0,
            "games_played": 0,
            "correct": 0,
            "premium": False,
            "joined": datetime.now().isoformat()
        }
    return db["users"][uid]

# ═══════════════════════════════════════════
#  СЕССИИ ИГРЫ (в памяти)
# ═══════════════════════════════════════════
sessions = {}

def new_session(user_id, category, level):
    cat_data = QUESTIONS[category]
    all_q = cat_data.get(level, []) + cat_data.get("easy", [])
    count = LEVELS[level]["questions"]
    questions = random.sample(all_q, min(count, len(all_q)))
    sessions[user_id] = {
        "category": category,
        "level": level,
        "questions": questions,
        "current": 0,
        "score": 0,
        "correct": 0,
        "wrong": 0,
        "answered": False,
    }

# ═══════════════════════════════════════════
#  КЛАВИАТУРЫ
# ═══════════════════════════════════════════
def main_menu_kb(is_premium=False):
    kb = [
        [InlineKeyboardButton("🎮 Играть", callback_data="play")],
        [InlineKeyboardButton("🏆 Топ игроков", callback_data="leaderboard"),
         InlineKeyboardButton("👤 Мой профиль", callback_data="profile")],
    ]
    if not is_premium:
        kb.append([InlineKeyboardButton("💎 Премиум — убрать рекламу", callback_data="premium")])
    return InlineKeyboardMarkup(kb)

def category_kb():
    kb = []
    for key, cat in QUESTIONS.items():
        kb.append([InlineKeyboardButton(cat["name"], callback_data=f"cat_{key}")])
    kb.append([InlineKeyboardButton("🔙 Назад", callback_data="back_menu")])
    return InlineKeyboardMarkup(kb)

def level_kb(category):
    kb = []
    for key, lv in LEVELS.items():
        kb.append([InlineKeyboardButton(
            f"{lv['name']} — {lv['questions']} вопросов, +{lv['points']} очков",
            callback_data=f"level_{category}_{key}"
        )])
    kb.append([InlineKeyboardButton("🔙 Назад", callback_data="play")])
    return InlineKeyboardMarkup(kb)

def answer_kb(question, q_idx, total):
    letters = ["🅰", "🅱", "🆎", "🆑"]
    kb = []
    row = []
    for i, ans in enumerate(question["a"]):
        row.append(InlineKeyboardButton(
            f"{letters[i]} {ans}",
            callback_data=f"ans_{i}"
        ))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(kb)

# ═══════════════════════════════════════════
//  HANDLERS
# ═══════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    u = get_user(db, user.id)
    u["name"] = user.first_name
    save_db(db)

    text = (
        f"👋 Привет, *{user.first_name}*!\n\n"
        "🌍 *GeoQuiz* — проверь знания географии!\n\n"
        "• 4 категории: флаги, столицы, природа, культура\n"
        "• 3 уровня сложности\n"
        "• 🏆 Таблица лидеров\n"
        "• 💎 Премиум без рекламы\n\n"
        "Нажми *Играть* чтобы начать! 👇"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=main_menu_kb(u["premium"])
    )

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    db = load_db()
    u = get_user(db, user.id)

    # — ГЛАВНОЕ МЕНЮ —
    if data == "back_menu" or data == "menu":
        await query.edit_message_text(
            f"🌍 *GeoQuiz* — главное меню\n\nПривет, *{user.first_name}*! Выбери действие:",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(u["premium"])
        )

    # — ВЫБОР КАТЕГОРИИ —
    elif data == "play":
        await query.edit_message_text(
            "🗂 Выбери *категорию*:",
            parse_mode="Markdown",
            reply_markup=category_kb()
        )

    # — ВЫБОР УРОВНЯ —
    elif data.startswith("cat_"):
        category = data[4:]
        cat_name = QUESTIONS[category]["name"]
        await query.edit_message_text(
            f"Категория: *{cat_name}*\n\nВыбери уровень сложности:",
            parse_mode="Markdown",
            reply_markup=level_kb(category)
        )

    # — СТАРТ ИГРЫ —
    elif data.startswith("level_"):
        _, category, level = data.split("_", 2)
        new_session(user.id, category, level)
        await send_question(query, user.id, db, u)

    # — ОТВЕТ —
    elif data.startswith("ans_"):
        idx = int(data[4:])
        await handle_answer(query, user.id, idx, db, u)

    # — СЛЕДУЮЩИЙ ВОПРОС —
    elif data == "next_q":
        sess = sessions.get(user.id)
        if not sess:
            await query.edit_message_text("Игра не найдена. Начни заново /start")
            return
        sess["current"] += 1
        sess["answered"] = False
        if sess["current"] >= len(sess["questions"]):
            await show_result(query, user.id, db, u)
        else:
            # Показываем рекламу каждые 3 вопроса (только не-премиум)
            if sess["current"] % 3 == 0 and not u["premium"]:
                await show_ad(query, user.id)
            else:
                await send_question(query, user.id, db, u)

    elif data == "after_ad":
        await send_question(query, user.id, db, u)

    # — ЛИДЕРБОРД —
    elif data == "leaderboard":
        await show_leaderboard(query, db)

    # — ПРОФИЛЬ —
    elif data == "profile":
        await show_profile(query, u, user)

    # — ПРЕМИУМ —
    elif data == "premium":
        await show_premium(query)

    elif data == "buy_premium":
        await query.edit_message_text(
            "💎 *Премиум доступ*\n\n"
            "Стоимость: *99 Telegram Stars* ⭐\n\n"
            "Что входит:\n"
            "• ❌ Без рекламы между вопросами\n"
            "• 🏆 Значок Premium в таблице лидеров\n"
            "• 🔓 Все уровни открыты\n\n"
            "Нажми кнопку ниже для оплаты:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐ Купить за 99 Stars", callback_data="pay_stars")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_menu")]
            ])
        )

    elif data == "pay_stars":
        await ctx.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="GeoQuiz Premium",
            description="Без рекламы + значок в топе",
            payload="premium_purchase",
            currency="XTR",
            prices=[LabeledPrice("Premium", 99)],
        )

    # — ИГРАТЬ СНОВА —
    elif data == "play_again":
        sess = sessions.get(user.id)
        if sess:
            new_session(user.id, sess["category"], sess["level"])
            await send_question(query, user.id, db, u)
        else:
            await query.edit_message_text("Выбери категорию:", reply_markup=category_kb())

# ═══════════════════════════════════════════
#  ИГРОВЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════
async def send_question(query, user_id, db, u):
    sess = sessions[user_id]
    q = sess["questions"][sess["current"]]
    total = len(sess["questions"])
    num = sess["current"] + 1
    cat_name = QUESTIONS[sess["category"]]["name"]
    lv_name = LEVELS[sess["level"]]["name"]

    progress = "▓" * sess["current"] + "░" * (total - sess["current"])

    text = (
        f"{cat_name} | {lv_name}\n"
        f"[{progress}] {num}/{total}\n"
        f"⭐ Очки: {sess['score']}\n\n"
        f"❓ *{q['q']}*"
    )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=answer_kb(q, sess["current"], total)
    )

async def handle_answer(query, user_id, idx, db, u):
    sess = sessions.get(user_id)
    if not sess or sess["answered"]:
        return
    sess["answered"] = True

    q = sess["questions"][sess["current"]]
    points = LEVELS[sess["level"]]["points"]
    correct = idx == q["c"]
    letters = ["🅰", "🅱", "🆎", "🆑"]

    if correct:
        sess["score"] += points
        sess["correct"] += 1
        result_text = f"✅ *Верно!* +{points} очков\n\n"
    else:
        sess["wrong"] += 1
        result_text = f"❌ *Неверно!*\nПравильный ответ: *{q['a'][q['c']]}*\n\n"

    result_text += f"💡 {q['fact']}"

    total = len(sess["questions"])
    num = sess["current"] + 1
    is_last = num >= total

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Результат 🏁" if is_last else "Следующий ➡️",
            callback_data="next_q"
        )
    ]])

    await query.edit_message_text(
        result_text, parse_mode="Markdown", reply_markup=kb
    )

async def show_ad(query, user_id):
    text = (
        "📢 *Реклама*\n\n"
        "┌─────────────────────┐\n"
        "│  Место для рекламы  │\n"
        "│   (Telegram Ads)    │\n"
        "└─────────────────────┘\n\n"
        "💎 Хочешь без рекламы? Купи Premium!"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Продолжить игру", callback_data="after_ad")],
        [InlineKeyboardButton("💎 Убрать рекламу", callback_data="premium")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def show_result(query, user_id, db, u):
    sess = sessions[user_id]
    score = sess["score"]
    correct = sess["correct"]
    wrong = sess["wrong"]
    total = len(sess["questions"])
    pct = round((correct / total) * 100)

    # Обновляем статистику
    u["total_score"] += score
    u["games_played"] += 1
    u["correct"] += correct
    save_db(db)

    # Обновляем лидерборд
    db2 = load_db()
    uid = str(user_id)
    if uid not in db2["leaderboard"] or db2["leaderboard"][uid]["score"] < db2["leaderboard"].get(uid, {}).get("score", 0) + score:
        db2["leaderboard"][uid] = {
            "name": u["name"],
            "score": db2.get("leaderboard", {}).get(uid, {}).get("score", 0) + score,
            "premium": u["premium"]
        }
    save_db(db2)

    if pct == 100: emoji, title = "🏆", "Абсолютный эксперт!"
    elif pct >= 80: emoji, title = "🌍", "Отличный результат!"
    elif pct >= 50: emoji, title = "🗺", "Неплохо!"
    else: emoji, title = "✈️", "Пора учить географию!"

    cat_name = QUESTIONS[sess["category"]]["name"]
    lv_name = LEVELS[sess["level"]]["name"]

    text = (
        f"{emoji} *{title}*\n\n"
        f"Категория: {cat_name}\n"
        f"Уровень: {lv_name}\n\n"
        f"🎯 Точность: *{pct}%*\n"
        f"✅ Верных: *{correct}/{total}*\n"
        f"⭐ Очков за игру: *{score}*\n"
        f"📊 Всего очков: *{u['total_score']}*\n\n"
        f"Поделись результатом с друзьями! 👇"
    )

    share_text = (
        f"🌍 GeoQuiz: {cat_name} | {lv_name}\n"
        f"✅ {correct}/{total} — {pct}%\n"
        f"⭐ {score} очков!\n"
        f"Попробуй beat меня! @geoquiz_game_bot"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Играть снова", callback_data="play_again"),
         InlineKeyboardButton("🏆 Топ", callback_data="leaderboard")],
        [InlineKeyboardButton("📤 Поделиться", switch_inline_query=share_text)],
        [InlineKeyboardButton("🏠 Меню", callback_data="back_menu")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def show_leaderboard(query, db):
    lb = db.get("leaderboard", {})
    if not lb:
        text = "🏆 *Таблица лидеров*\n\nПока никто не играл. Будь первым!"
    else:
        sorted_lb = sorted(lb.items(), key=lambda x: x[1].get("score", 0), reverse=True)[:10]
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        lines = ["🏆 *Топ-10 игроков*\n"]
        for i, (uid, data) in enumerate(sorted_lb):
            crown = "💎 " if data.get("premium") else ""
            lines.append(f"{medals[i]} {crown}{data['name']} — *{data['score']}* очков")
        text = "\n".join(lines)

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Меню", callback_data="back_menu")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def show_profile(query, u, user):
    acc = u["correct"]
    games = u["games_played"]
    pct = round((acc / max(games * 5, 1)) * 100) if games > 0 else 0
    premium_badge = "💎 Premium" if u["premium"] else "Обычный"

    text = (
        f"👤 *Профиль: {user.first_name}*\n\n"
        f"🎭 Статус: {premium_badge}\n"
        f"🎮 Игр сыграно: *{games}*\n"
        f"⭐ Всего очков: *{u['total_score']}*\n"
        f"✅ Верных ответов: *{u['correct']}*\n"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Меню", callback_data="back_menu")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def show_premium(query):
    text = (
        "💎 *GeoQuiz Premium*\n\n"
        "Что получишь:\n"
        "• ❌ Без рекламы\n"
        "• 👑 Значок в таблице лидеров\n"
        "• ⚡ Все категории и уровни\n\n"
        "Цена: *99 Telegram Stars* ⭐\n"
        "_(разово, навсегда)_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Купить Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_menu")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

# — Оплата Stars —
async def precheckout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    u = get_user(db, user.id)
    u["premium"] = True
    save_db(db)
    await update.message.reply_text(
        "🎉 *Спасибо за покупку!*\n\n"
        "💎 Premium активирован! Наслаждайся игрой без рекламы.\n\n"
        "Нажми /start чтобы вернуться в меню.",
        parse_mode="Markdown"
    )

# — Статистика для админа —
async def stats_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    db = load_db()
    users = db.get("users", {})
    premium = sum(1 for u in users.values() if u.get("premium"))
    text = (
        f"📊 *Статистика бота*\n\n"
        f"👥 Пользователей: {len(users)}\n"
        f"💎 Premium: {premium}\n"
        f"🎮 Игр сыграно: {sum(u.get('games_played',0) for u in users.values())}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ═══════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    print("✅ GeoQuiz Bot запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
