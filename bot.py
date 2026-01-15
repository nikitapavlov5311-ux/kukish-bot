```python
import json
import random
import asyncio
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== КОНСТАНТЫ И КЛАССЫ ====================

class KukishCryptoMiningBot:
    def __init__(self):
        # Основные данные
        self.ADMIN_USERNAME = "@nktplv"
        self.user_data = {}
        self.active_bosses = {}
        self.promo_codes = {}
        self.admin_states = {}
        self.gift_states = {}
        self.crafting_states = {}

        # Криптовалюты
        self.cryptocurrencies = {
            "lakacoin": {"name": "LakaCoin", "price": 300, "wear_factor": 0.3, "energy_factor": 1.0, "degradation_factor": 1.0, "emoji": "🪙"},
            "kefir": {"name": "Kefir", "price": 400, "wear_factor": 0.4, "energy_factor": 1.5, "degradation_factor": 1.2, "emoji": "🥛"},
            "jopadollar": {"name": "JopaDollar", "price": 600, "wear_factor": 0.6, "energy_factor": 2.0, "degradation_factor": 1.5, "emoji": "🍑"},
            "referal": {"name": "Referal Rebirth", "price": 1000, "wear_factor": 1.0, "energy_factor": 4.0, "degradation_factor": 2.0, "emoji": "🔥"}
        }

        # Видеокарты (базовые)
        self.gpu_templates = [
            {"id": 1, "name": "RX 550", "price": 6000, "income": 0.00001, "hours_per_1percent": 120,
             "power_per_hour": 75, "base_break_chance": 0.015, "emoji": "💎", "repair_cost_coef": 0.25},
            {"id": 2, "name": "RX 580", "price": 8000, "income": 0.00003, "hours_per_1percent": 110,
             "power_per_hour": 150, "base_break_chance": 0.012, "emoji": "💎", "repair_cost_coef": 0.25},
            {"id": 3, "name": "GTX 1050", "price": 20000, "income": 0.00008, "hours_per_1percent": 100,
             "power_per_hour": 300, "base_break_chance": 0.01, "emoji": "🖥️", "repair_cost_coef": 0.25},
            {"id": 4, "name": "GTX 1660 Super", "price": 30000, "income": 0.0001, "hours_per_1percent": 90,
             "power_per_hour": 400, "base_break_chance": 0.008, "emoji": "🖥️", "repair_cost_coef": 0.25},
            {"id": 5, "name": "RTX 3050", "price": 100000, "income": 0.0002, "hours_per_1percent": 80,
             "power_per_hour": 600, "base_break_chance": 0.005, "emoji": "🎮", "repair_cost_coef": 0.25},
            {"id": 6, "name": "RTX 4060", "price": 180000, "income": 0.0007, "hours_per_1percent": 70,
             "power_per_hour": 800, "base_break_chance": 0.004, "emoji": "🎮", "repair_cost_coef": 0.25},
            {"id": 7, "name": "RTX 4070", "price": 200000, "income": 0.001, "hours_per_1percent": 60,
             "power_per_hour": 900, "base_break_chance": 0.003, "emoji": "🎮", "repair_cost_coef": 0.25},
            {"id": 8, "name": "RTX 3080", "price": 300000, "income": 0.004, "hours_per_1percent": 50,
             "power_per_hour": 1000, "base_break_chance": 0.002, "emoji": "🔥", "repair_cost_coef": 0.25},
            {"id": 9, "name": "RTX 5090", "price": 900000, "income": 0.007, "hours_per_1percent": 40,
             "power_per_hour": 1200, "base_break_chance": 0.0015, "emoji": "🔥", "repair_cost_coef": 0.25},
            {"id": 10, "name": "RTX A6000", "price": 2000000, "income": 0.1, "hours_per_1percent": 30,
             "power_per_hour": 1500, "base_break_chance": 0.0008, "emoji": "🚀", "repair_cost_coef": 0.25}
        ]

        # Кейсы
        self.cases = {
            "money_case": {
                "name": "💰 Денежный кейс", "price": 50000, "gift_price": 75000, "emoji": "💰",
                "description": "Содержит от 1,000 до 80,000 монет", "min_reward": 1000, "max_reward": 80000,
                "probabilities": [(1000, 5000, 0.45), (5001, 15000, 0.30), (15001, 30000, 0.15),
                                 (30001, 50000, 0.07), (50001, 80000, 0.03)], "risk": "Высокий"
            },
            "energy_case": {
                "name": "⚡ Энергетический кейс", "price": 15000, "gift_price": 20000, "emoji": "⚡",
                "description": "Содержит от 1% до 50% энергии", "min_reward": 1, "max_reward": 50,
                "energy_price_per_percent": 500, "probabilities": [(1, 10, 0.60), (11, 25, 0.25),
                                 (26, 40, 0.10), (41, 50, 0.05)], "risk": "Высокий"
            },
            "gpu_case": {
                "name": "🎮 Кейс с видеокартой", "price": 100000, "gift_price": 150000, "emoji": "🎮",
                "description": "Может содержать любую видеокарту!", "probabilities": [
                    ("RX 550", 0.50), ("RX 580", 0.25), ("GTX 1050", 0.10), ("GTX 1660 Super", 0.07),
                    ("RTX 3050", 0.04), ("RTX 4060", 0.02), ("RTX 4070", 0.01), ("RTX 3080", 0.005),
                    ("RTX 5090", 0.004), ("RTX A6000", 0.001)
                ], "risk": "Экстремальный", "marketing_text": "🎯 Испытайте удачу!"
            }
        }

        # Боссы
        self.boss_templates = {
            "ice": {"name": "Ледяной Колосс", "emoji": "🧊", "health": 4000, "element": "Лёд"},
            "fire": {"name": "Огненный Титан", "emoji": "🔥", "health": 6000, "element": "Огонь"},
            "wind": {"name": "Ветренный Ураган", "emoji": "🌪️", "health": 3000, "element": "Ветер"}
        }

        # Титулы
        self.titles = {
            "boss_king": {"name": "Император Боссов", "emoji": "👑", "description": "1 место в боссфайте"},
            "sniper": {"name": "Легендарный Снайпер", "emoji": "🎯", "description": "2 место в боссфайте"},
            "outsider": {"name": "Мега-Аутсайдер", "emoji": "🐌", "description": "3 место в боссфайте"},
            "millionaire": {"name": "Миллионер", "emoji": "💰", "description": "Заработал 1,000,000₽"},
            "energizer": {"name": "Энерджайзер", "emoji": "⚡", "description": "30 дней с энергией >80%"},
            "invulnerable": {"name": "Неуязвимый", "emoji": "🛡️", "description": "50 дней без поломок"},
            "lucky": {"name": "Везунчик", "emoji": "🎰", "description": "Выиграл джекпот в кейсе"},
            "newbie": {"name": "Новичок", "emoji": "🌟", "description": "Первая неделя в игре"}
        }

        # Настройки по умолчанию
        self.default_settings = {
            "notifications": {
                "breakdowns": True, "mining_complete": True, "low_energy": True,
                "daily_bonus": True, "case_rewards": True, "gifts": True
            },
            "automation": {
                "auto_buy_energy": True, "auto_mining": False, "auto_conversion": False, "auto_optimizer": False
            },
            "display": {
                "theme": "light", "compact_mode": False, "public_rating": True, "group_notifications": True
            },
            "currency": "Бубли"
        }

        # Лимиты
        self.MAX_SLOTS = 15
        self.BASE_SLOTS = 5
        self.BASE_SLOT_PRICE = 5000
        self.SLOT_PRICE_MULTIPLIER = 2
        self.MAX_CASES_PER_TYPE = 10
        self.MAX_TOTAL_CASES = 30
        self.WEAR_REPAIR_THRESHOLD = 60
        self.WEAR_REPAIR_COOLDOWN = 7 * 24 * 3600
        self.WEAR_REPAIR_COST_MULTIPLIER = 0.8
        self.WEAR_REPAIR_PERFORMANCE_PENALTY = 0.15
        self.WEAR_REPAIR_ENERGY_PENALTY = 0.10

        # Крафтинг
        self.CRAFT_INCOME_BOOST = 0.03  # +3%
        self.CRAFT_ENERGY_PENALTY = 0.05  # +5%
        self.DISASSEMBLE_COST = 10000

        # Боссфайт
        self.BOSS_MAX_SPEND = 50000
        self.BOSS_COOLDOWN = 5  # секунд
        self.BOSS_DURATION = 30 * 60  # 30 минут
        self.BOSS_DAMAGE_FORMULA_DIVIDER = 30

    # ==================== УТИЛИТЫ ====================

    def get_user(self, user_id: int) -> Dict:
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "balance": 10000,
                "energy": 100.0,
                "crypto": {coin: 0.0 for coin in self.cryptocurrencies},
                "gpus": [],
                "broken_gpus": [],
                "slots": self.BASE_SLOTS,
                "used_slots": 0,
                "extra_slots_bought": 0,
                "cases": {case_id: 0 for case_id in self.cases},
                "settings": self.default_settings.copy(),
                "nickname": None,
                "active_title": None,
                "titles": [],
                "participated_events": [],
                "last_wear_repair": None,
                "last_update": datetime.now().isoformat(),
                "username": None
            }
        return self.user_data[user_id]

    def is_admin(self, username: str) -> bool:
        return username == self.ADMIN_USERNAME

    def format_number(self, num: float) -> str:
        return f"{num:,.2f}".replace(",", " ").replace(".", ",")

    # ==================== ВИДЕОКАРТЫ ====================

    def create_gpu_instance(self, gpu_id: int, currency: str = "lakacoin") -> Dict:
        template = next(g for g in self.gpu_templates if g["id"] == gpu_id)
        return {
            "id": gpu_id,
            "name": template["name"],
            "template": template,
            "currency": currency,
            "durability": 100.0,
            "is_broken": False,
            "is_mining": False,
            "mining_currency": None,
            "mining_start": None,
            "total_mined": 0.0,
            "repair_count": 0,
            "is_v2": False,
            "emoji": template["emoji"]
        }

    def calculate_repair_cost(self, gpu: Dict) -> int:
        template = gpu["template"]
        return int(template["price"] * template["repair_cost_coef"])

    def calculate_wear_repair_cost(self, gpu: Dict) -> int:
        template = gpu["template"]
        wear_percent = 100 - gpu["durability"]
        return int(template["price"] * (wear_percent / 100) * self.WEAR_REPAIR_COST_MULTIPLIER)

    def can_repair_wear(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user["last_wear_repair"] is None:
            return True

        last_repair = datetime.fromisoformat(user["last_wear_repair"])
        time_passed = (datetime.now() - last_repair).total_seconds()
        return time_passed >= self.WEAR_REPAIR_COOLDOWN

    # ==================== МАЙНИНГ ====================

    def start_mining(self, user_id: int, gpu_index: int, currency: str) -> bool:
        user = self.get_user(user_id)
        if gpu_index >= len(user["gpus"]):
            return False

        gpu = user["gpus"][gpu_index]
        if gpu["is_broken"] or gpu["is_mining"]:
            return False

        # Проверка энергии
        if user["energy"] <= 0:
            return False

        gpu["is_mining"] = True
        gpu["mining_currency"] = currency
        gpu["mining_start"] = datetime.now().isoformat()
        return True

    def stop_mining(self, user_id: int, gpu_index: int) -> bool:
        user = self.get_user(user_id)
        if gpu_index >= len(user["gpus"]):
            return False

        gpu = user["gpus"][gpu_index]
        if not gpu["is_mining"]:
            return False

        # Расчет намайненных монет
        if gpu["mining_start"]:
            start_time = datetime.fromisoformat(gpu["mining_start"])
            elapsed = (datetime.now() - start_time).total_seconds()

            # Расчет дохода
            base_income = gpu["template"]["income"]
            if gpu["is_v2"]:
                base_income *= (1 + self.CRAFT_INCOME_BOOST)

            # Учет ремонтов
            for _ in range(gpu["repair_count"]):
                base_income *= (1 - self.WEAR_REPAIR_PERFORMANCE_PENALTY)

            mined = base_income * elapsed
            user["crypto"][gpu["currency"]] += mined
            gpu["total_mined"] += mined

            # Расчет износа
            crypto_info = self.cryptocurrencies[gpu["currency"]]
            wear_per_second = (1 / (gpu["template"]["hours_per_1percent"] * 3600)) * crypto_info["degradation_factor"]
            gpu["durability"] = max(0, gpu["durability"] - (wear_per_second * elapsed * 100))

            # Расчет энергии
            power = gpu["template"]["power_per_hour"]
            if gpu["is_v2"]:
                power *= (1 + self.CRAFT_ENERGY_PENALTY)

            energy_used = (power / 3600) * elapsed / 1000  # в процентах
            user["energy"] = max(0, user["energy"] - energy_used)

            # Проверка поломки
            if gpu["durability"] <= 0:
                gpu["is_broken"] = True
            else:
                break_chance = gpu["template"]["base_break_chance"] * crypto_info["wear_factor"] * (elapsed / 3600)
                if random.random() < break_chance:
                    gpu["is_broken"] = True

        gpu["is_mining"] = False
        gpu["mining_start"] = None
        return True

    # ==================== СЛОТЫ ====================

    def calculate_slot_price(self, user_id: int) -> int:
        user = self.get_user(user_id)
        extra_slots = user["extra_slots_bought"]
        return int(self.BASE_SLOT_PRICE * (self.SLOT_PRICE_MULTIPLIER ** extra_slots))

    def can_buy_gpu(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        user["used_slots"] = len(user["gpus"]) + len(user["broken_gpus"])
        return user["used_slots"] < user["slots"]

    # ==================== КЕЙСЫ ====================

    def can_add_case(self, user_id: int, case_type: str) -> tuple:
        user = self.get_user(user_id)
        if user["cases"][case_type] >= self.MAX_CASES_PER_TYPE:
            return False, f"❌ Лимит кейсов достигнут! (макс: {self.MAX_CASES_PER_TYPE})"

        total_cases = sum(user["cases"].values())
        if total_cases >= self.MAX_TOTAL_CASES:
            return False, f"❌ Общий лимит кейсов достигнут! (макс: {self.MAX_TOTAL_CASES})"

        return True, "✅ Можно добавить кейс"

    def open_case(self, case_type: str, user_id: int) -> Dict:
        user = self.get_user(user_id)
        case = self.cases[case_type]
        result = {"type": case_type, "reward": {}}

        if case_type == "money_case":
            rand = random.random()
            cumulative = 0
            for min_r, max_r, prob in case["probabilities"]:
                cumulative += prob
                if rand <= cumulative:
                    reward = random.randint(min_r, max_r)
                    user["balance"] += reward
                    result["reward"] = {"money": reward}
                    break

        elif case_type == "energy_case":
            rand = random.random()
            cumulative = 0
            for min_r, max_r, prob in case["probabilities"]:
                cumulative += prob
                if rand <= cumulative:
                    energy_reward = random.randint(min_r, max_r)
                    new_energy = min(100, user["energy"] + energy_reward)
                    added = new_energy - user["energy"]
                    user["energy"] = new_energy
                    result["reward"] = {"energy": added}
                    break

        elif case_type == "gpu_case":
            rand = random.random()
            cumulative = 0
            for gpu_name, prob in case["probabilities"]:
                cumulative += prob
                if rand <= cumulative:
                    # Находим ID карты по имени
                    gpu_id = next(g["id"] for g in self.gpu_templates if g["name"] == gpu_name)
                    if self.can_buy_gpu(user_id):
                        gpu = self.create_gpu_instance(gpu_id)
                        user["gpus"].append(gpu)
                        result["reward"] = {"gpu": gpu_name, "gpu_id": gpu_id}
                    break

        user["cases"][case_type] -= 1
        return result

    # ==================== БОССФАЙТ ====================

    def start_boss_fight(self, boss_type: str) -> str:
        if boss_type not in self.boss_templates:
            boss_type = random.choice(list(self.boss_templates.keys()))

        boss = self.boss_templates[boss_type].copy()
        boss_id = f"boss_{datetime.now().timestamp()}"

        self.active_bosses[boss_id] = {
            **boss,
            "current_health": boss["health"],
            "max_health": boss["health"],
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(seconds=self.BOSS_DURATION)).isoformat(),
            "participants": {},
            "damage_log": []
        }

        return boss_id

    def attack_boss(self, user_id: int, boss_id: str, currency: str, amount: float) -> Dict:
        if boss_id not in self.active_bosses:
            return {"success": False, "error": "Босс не найден"}

        boss = self.active_bosses[boss_id]
        user = self.get_user(user_id)

        # Проверка времени
        end_time = datetime.fromisoformat(boss["end_time"])
        if datetime.now() >= end_time:
            return {"success": False, "error": "Бой завершён"}

        # Проверка крипты
        if user["crypto"][currency] < amount:
            return {"success": False, "error": "Недостаточно крипты"}

        # Проверка лимита затрат
        user_spent = boss["participants"].get(user_id, {}).get("total_spent", 0)
        crypto_value = amount * self.cryptocurrencies[currency]["price"]

        if user_spent + crypto_value > self.BOSS_MAX_SPEND:
            return {"success": False, "error": f"Лимит затрат {self.BOSS_MAX_SPEND}₽ достигнут"}

        # Расчет урона
        damage = amount * (self.cryptocurrencies[currency]["price"] / self.BOSS_DAMAGE_FORMULA_DIVIDER)

        # Спишем крипту
        user["crypto"][currency] -= amount

        # Обновим данные босса
        boss["current_health"] = max(0, boss["current_health"] - damage)

        if user_id not in boss["participants"]:
            boss["participants"][user_id] = {"total_damage": 0, "total_spent": 0}

        boss["participants"][user_id]["total_damage"] += damage
        boss["participants"][user_id]["total_spent"] += crypto_value
        boss["damage_log"].append({
            "user_id": user_id,
            "damage": damage,
            "currency": currency,
            "amount": amount,
            "time": datetime.now().isoformat()
        })

        # Проверка убийства босса
        if boss["current_health"] <= 0:
            self.finish_boss_fight(boss_id)

        return {
            "success": True,
            "damage": damage,
            "remaining_health": boss["current_health"],
            "total_spent": boss["participants"][user_id]["total_spent"]
        }

    def finish_boss_fight(self, boss_id: str):
        if boss_id not in self.active_bosses:
            return

        boss = self.active_bosses[boss_id]

        # Сортируем участников по урону
        participants = []
        for user_id, data in boss["participants"].items():
            participants.append({
                "user_id": user_id,
                "damage": data["total_damage"],
                "spent": data["total_spent"]
            })

        participants.sort(key=lambda x: x["damage"], reverse=True)

        # Выдаем награды
        rewards = []
        for i, participant in enumerate(participants[:3]):
            user_id = participant["user_id"]
            user = self.get_user(user_id)

            if i == 0:  # 1 место
                user["balance"] += 50000
                user["energy"] = min(100, user["energy"] + 25)
                title = "boss_king"
            elif i == 1:  # 2 место
                user["balance"] += 25000
                user["energy"] = min(100, user["energy"] + 15)
                title = "sniper"
            else:  # 3 место
                user["balance"] += 12000
                user["energy"] = min(100, user["energy"] + 8)
                title = "outsider"

            # Добавляем титул если его нет
            if title not in user["titles"]:
                user["titles"].append(title)

            rewards.append({
                "user_id": user_id,
                "place": i + 1,
                "reward_money": [50000, 25000, 12000][i],
                "reward_energy": [25, 15, 8][i],
                "title": title
            })

        # Награды за участие
        for participant in participants[3:]:
            user_id = participant["user_id"]
            user = self.get_user(user_id)
            user["balance"] += 2000
            user["energy"] = min(100, user["energy"] + 3)

        boss["rewards"] = rewards
        boss["finished"] = True
        boss["finish_time"] = datetime.now().isoformat()

    # ==================== КРАФТИНГ ====================

    def can_craft_gpu(self, user_id: int, gpu_id: int) -> tuple:
        user = self.get_user(user_id)
        count = sum(1 for gpu in user["gpus"] if gpu["id"] == gpu_id and not gpu["is_v2"])
        return count >= 2, count

    def craft_gpu(self, user_id: int, gpu_id: int) -> Dict:
        user = self.get_user(user_id)

        # Находим 2 одинаковые карты
        indices = []
        for i, gpu in enumerate(user["gpus"]):
            if gpu["id"] == gpu_id and not gpu["is_v2"] and not gpu["is_broken"]:
                indices.append(i)
            if len(indices) == 2:
                break

        if len(indices) < 2:
            return {"success": False, "error": "Недостаточно одинаковых карт"}

        # Удаляем 2 карты
        gpu1 = user["gpus"].pop(max(indices))
        gpu2 = user["gpus"].pop(min(indices))

        # Создаем V2 версию
        v2_gpu = self.create_gpu_instance(gpu_id, gpu1["currency"])
        v2_gpu["is_v2"] = True
        v2_gpu["durability"] = min(gpu1["durability"], gpu2["durability"])

        user["gpus"].append(v2_gpu)

        return {
            "success": True,
            "crafted_gpu": v2_gpu,
            "removed_gpus": [gpu1, gpu2]
        }

    def disassemble_gpu(self, user_id: int, gpu_index: int) -> Dict:
        user = self.get_user(user_id)

        if gpu_index >= len(user["gpus"]):
            return {"success": False, "error": "Карта не найдена"}

        gpu = user["gpus"][gpu_index]
        if not gpu["is_v2"]:
            return {"success": False, "error": "Это не V2 карта"}

        # Проверяем стоимость и слоты
        if user["balance"] < self.DISASSEMBLE_COST:
            return {"success": False, "error": f"Недостаточно средств. Нужно {self.DISASSEMBLE_COST}₽"}

        if user["used_slots"] + 1 > user["slots"]:
            return {"success": False, "error": "Недостаточно слотов для разборки"}

        # Снимаем деньги
        user["balance"] -= self.DISASSEMBLE_COST

        # Удаляем V2 карту
        v2_gpu = user["gpus"].pop(gpu_index)

        # Создаем 2 обычные карты
        gpu1 = self.create_gpu_instance(v2_gpu["id"], v2_gpu["currency"])
        gpu2 = self.create_gpu_instance(v2_gpu["id"], v2_gpu["currency"])

        # Восстанавливаем часть прочности
        repair_percent = 20  # Восстанавливаем 20% прочности
        gpu1["durability"] = min(100, v2_gpu["durability"] + repair_percent)
        gpu2["durability"] = min(100, v2_gpu["durability"] + repair_percent)

        user["gpus"].extend([gpu1, gpu2])

        return {
            "success": True,
            "disassembled_gpu": v2_gpu,
            "created_gpus": [gpu1, gpu2],
            "cost": self.DISASSEMBLE_COST
        }

    # ==================== ТЕЛЕГРАМ ХЕНДЛЕРЫ ====================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_data = self.get_user(user.id)
        user_data["username"] = user.username

        keyboard = [
            [InlineKeyboardButton("🛒 Рынок", callback_data="market")],
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
            [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
            [InlineKeyboardButton("🎰 Кейсы", callback_data="cases_menu")],
            [InlineKeyboardButton("⚙️ Параметры", callback_data="settings")],
        ]

        # Проверяем активные боссфайты
        active_boss = next((boss_id for boss_id, boss in self.active_bosses.items()
                          if not boss.get("finished", False)), None)
        if active_boss:
            keyboard.append([InlineKeyboardButton("🎯 Боссфайт", callback_data=f"boss_fight_{active_boss}")])

        # Проверяем админа
        if self.is_admin(user.username):
            keyboard.append([InlineKeyboardButton("👑 Админ-панель", callback_data="admin_panel")])

        keyboard.append([InlineKeyboardButton("ℹ️ Помощь", callback_data="help")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = f"🎮 Добро пожаловать в *Kukish Crypto Mining*!\n\n"
        if user_data["nickname"]:
            title = f"[{self.titles[user_data['active_title']]['emoji']} {self.titles[user_data['active_title']]['name']}] " if user_data["active_title"] else ""
            welcome_text += f"👤 {title}{user_data['nickname']}\n"
        welcome_text += f"💰 Баланс: {self.format_number(user_data['balance'])}₽\n"
        welcome_text += f"⚡ Энергия: {user_data['energy']:.1f}%\n"
        welcome_text += f"📦 Слоты: {user_data['used_slots']}/{user_data['slots']}\n\n"
        welcome_text += "Выберите действие:"

        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "market":
            await self.show_market(query)
        elif data == "inventory":
            await self.show_inventory(query)
        elif data == "balance":
            await self.show_balance(query)
        elif data == "cases_menu":
            await self.show_cases_menu(query)
        elif data == "settings":
            await self.show_settings(query)
        elif data == "admin_panel":
            await self.show_admin_panel(query)
        elif data == "help":
            await self.show_help(query)
        elif data.startswith("boss_fight_"):
            boss_id = data.replace("boss_fight_", "")
            await self.show_boss_fight(query, boss_id)
        elif data == "main_menu":
            await self.start_command(update, context)
        # ... остальные хендлеры будут добавлены

    async def show_market(self, query):
        user = query.from_user
        user_data = self.get_user(user.id)

        text = "🛒 *Рынок*\n\n"
        text += f"💰 Баланс: {self.format_number(user_data['balance'])}₽\n"
        text += f"📦 Свободных слотов: {user_data['slots'] - user_data['used_slots']}/{user_data['slots']}\n\n"
        text += "Выберите раздел:"

        keyboard = [
            [InlineKeyboardButton("🖥️ Видеокарты", callback_data="market_gpus")],
            [InlineKeyboardButton("⚡ Купить энергию", callback_data="buy_energy")],
            [InlineKeyboardButton("🎁 Подарить видеокарту", callback_data="gift_gpu")],
            [InlineKeyboardButton("📦 Купить слоты", callback_data="buy_slots")],
            [InlineKeyboardButton("🎰 Кейсы", callback_data="cases_menu")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_inventory(self, query):
        user = query.from_user
        user_data = self.get_user(user.id)

        # Обновляем использованные слоты
        user_data["used_slots"] = len(user_data["gpus"]) + len(user_data["broken_gpus"])

        text = "🎒 *Ваш инвентарь*\n\n"
        text += f"💰 Баланс: {self.format_number(user_data['balance'])}₽\n"
        text += f"⚡ Энергия: {user_data['energy']:.1f}%\n"
        text += f"📦 Слоты: {user_data['used_slots']}/{user_data['slots']}\n\n"

        # Проверяем карты для крафта
        craftable_gpus = {}
        for gpu in user_data["gpus"]:
            if not gpu["is_broken"] and not gpu["is_v2"]:
                gpu_id = gpu["id"]
                craftable_gpus[gpu_id] = craftable_gpus.get(gpu_id, 0) + 1

        craftable_count = sum(1 for count in craftable_gpus.values() if count >= 2)

        if craftable_count > 0:
            text += f"⚙️ Доступно крафтов: {craftable_count}\n\n"

        keyboard = [
            [InlineKeyboardButton("🖥️ Мои видеокарты", callback_data="my_gpus")],
            [InlineKeyboardButton("🔧 Сломанные карты", callback_data="broken_gpus")],
        ]

        if craftable_count > 0:
            keyboard.insert(0, [InlineKeyboardButton("⚙️ Крафтинг", callback_data="crafting_menu")])

        # Проверяем возможность ремонта износа
        worn_gpus = [g for g in user_data["gpus"] if g["durability"] < self.WEAR_REPAIR_THRESHOLD and not g["is_broken"]]
        if worn_gpus and self.can_repair_wear(user.id):
            keyboard.insert(0, [InlineKeyboardButton("🔩 Ремонт износа", callback_data="wear_repair_menu")])

        keyboard.extend([
            [InlineKeyboardButton("🎰 Мои кейсы", callback_data="my_cases")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_balance(self, query):
        user = query.from_user
        user_data = self.get_user(user.id)

        text = "💰 *Ваш баланс*\n\n"
        text += f"💵 Деньги: {self.format_number(user_data['balance'])}₽\n"
        text += f"⚡ Энергия: {user_data['energy']:.1f}%\n\n"

        text += "💎 *Криптовалюты:*\n"
        total_crypto_value = 0
        for coin, amount in user_data["crypto"].items():
            if amount > 0:
                coin_info = self.cryptocurrencies[coin]
                value = amount * coin_info["price"]
                total_crypto_value += value
                text += f"{coin_info['emoji']} {coin_info['name']}: {amount:.6f} ≈ {self.format_number(value)}₽\n"

        if total_crypto_value > 0:
            text += f"\n📊 Общая стоимость крипты: {self.format_number(total_crypto_value)}₽\n"

        text += f"\n💎 Итого активов: {self.format_number(user_data['balance'] + total_crypto_value)}₽"

        keyboard = [
            [InlineKeyboardButton("💱 Обменять крипту", callback_data="exchange_crypto")],
            [InlineKeyboardButton("💰 Пополнить баланс", callback_data="deposit")],
            [InlineKeyboardButton("🔙 Назад", callback_data="inventory")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_cases_menu(self, query):
        user = query.from_user
        user_data = self.get_user(user.id)

        text = "🎰 *Кейсы*\n\n"
        text += f"💰 Ваш баланс: {self.format_number(user_data['balance'])}₽\n\n"

        for case_id, case in self.cases.items():
            owned = user_data["cases"][case_id]
            text += f"{case['emoji']} *{case['name']}*\n"
            text += f"   Цена: {self.format_number(case['price'])}₽\n"
            text += f"   В инвентаре: {owned}/{self.MAX_CASES_PER_TYPE}\n"
            text += f"   {case['description']}\n\n"

        keyboard = []
        for case_id, case in self.cases.items():
            keyboard.append([InlineKeyboardButton(
                f"{case['emoji']} {case['name']} - {self.format_number(case['price'])}₽",
                callback_data=f"buy_case_{case_id}"
            )])

        keyboard.extend([
            [InlineKeyboardButton("🎁 Подарить кейс", callback_data="gift_case_menu")],
            [InlineKeyboardButton("🎒 Мои кейсы", callback_data="my_cases")],
            [InlineKeyboardButton("🔙 Назад", callback_data="market")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_settings(self, query):
        user = query.from_user
        user_data = self.get_user(user.id)

        text = "⚙️ *Параметры*\n\n"

        # Показываем активный титул
        if user_data["active_title"]:
            title_info = self.titles[user_data["active_title"]]
            text += f"🏆 Активный титул: [{title_info['emoji']} {title_info['name']}]\n"

        text += f"👤 Никнейм: {user_data['nickname'] or 'Не установлен'}\n"
        text += f"💰 Валюта: {user_data['settings']['currency']}\n"
        text += f"🎨 Тема: {user_data['settings']['display']['theme']}\n\n"

        keyboard = [
            [InlineKeyboardButton("📊 Профиль и статистика", callback_data="profile_stats")],
            [InlineKeyboardButton("🏆 Мои титулы", callback_data="my_titles")],
            [InlineKeyboardButton("👤 Изменить никнейм", callback_data="change_nickname")],
            [InlineKeyboardButton("🔔 Уведомления", callback_data="notifications_settings")],
            [InlineKeyboardButton("🤖 Автоматизация", callback_data="automation_settings")],
            [InlineKeyboardButton("🎨 Интерфейс", callback_data="interface_settings")],
            [InlineKeyboardButton("📈 Аналитика", callback_data="analytics_settings")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_admin_panel(self, query):
        user = query.from_user

        if not self.is_admin(user.username):
            await query.answer("❌ У вас нет прав администратора!")
            return

        text = "👑 *Админ-панель*\n\n"
        text += f"👤 Игроков онлайн: {len(self.user_data)}\n"
        text += f"🎯 Активных боссов: {len([b for b in self.active_bosses.values() if not b.get('finished', False)])}\n\n"

        keyboard = [
            [InlineKeyboardButton("👥 Балансы игроков", callback_data="admin_balances")],
            [InlineKeyboardButton("💰 Задать баланс", callback_data="admin_set_balance")],
            [InlineKeyboardButton("🎒 Инвентари игроков", callback_data="admin_inventories")],
            [InlineKeyboardButton("⚙️ Настройки игры", callback_data="admin_game_settings")],
            [InlineKeyboardButton("🎫 Промокоды", callback_data="admin_promo_codes")],
            [InlineKeyboardButton("🎮 Управление боссфайтами", callback_data="admin_boss_management")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_boss_fight(self, query, boss_id: str):
        if boss_id not in self.active_bosses:
            await query.answer("❌ Боссфайт завершён или не найден!")
            return

        boss = self.active_bosses[boss_id]
        user = query.from_user
        user_data = self.get_user(user.id)

        # Проверяем время
        end_time = datetime.fromisoformat(boss["end_time"])
        if datetime.now() >= end_time:
            await query.answer("❌ Боссфайт завершён!")
            return

        remaining_time = end_time - datetime.now()
        minutes = int(remaining_time.total_seconds() // 60)
        seconds = int(remaining_time.total_seconds() % 60)

        text = f"🎯 *Боссфайт: {boss['name']} {boss['emoji']}*\n\n"
        text += f"❤️ Здоровье: {boss['current_health']}/{boss['max_health']} HP\n"
        text += f"⏰ Осталось: {minutes:02d}:{seconds:02d}\n\n"

        # Топ участников
        participants = list(boss["participants"].items())
        participants.sort(key=lambda x: x[1]["total_damage"], reverse=True)

        text += "🏆 *Топ участников:*\n"
        for i, (user_id, data) in enumerate(participants[:3]):
            damage = data["total_damage"]
            spent = data["total_spent"]
            text += f"{['🥇','🥈','🥉'][i]} {damage:.0f} урона ({spent:.0f}₽)\n"

        user_damage = boss["participants"].get(user.id, {}).get("total_damage", 0)
        user_spent = boss["participants"].get(user.id, {}).get("total_spent", 0)
        text += f"\n🎯 Ваш урон: {user_damage:.0f}\n"
        text += f"💸 Ваши затраты: {user_spent:.0f}₽ / {self.BOSS_MAX_SPEND}₽\n"

        keyboard = []
        for currency_id, currency_info in self.cryptocurrencies.items():
            amount = user_data["crypto"][currency_id]
            if amount > 0:
                damage_per_unit = currency_info["price"] / self.BOSS_DAMAGE_FORMULA_DIVIDER
                keyboard.append([InlineKeyboardButton(
                    f"{currency_info['emoji']} {currency_info['name']} ({amount:.2f}) - {damage_per_unit:.1f} урона/ед.",
                    callback_data=f"boss_attack_{boss_id}_{currency_id}"
                )])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_help(self, query):
        text = "❓ *Помощь по игре Kukish Crypto Mining*\n\n"
        text += "🎮 *Основные разделы:*\n"
        text += "• 🛒 *Рынок* - покупка оборудования и ресурсов\n"
        text += "• 🎒 *Инвентарь* - управление вашим имуществом\n"
        text += "• 💰 *Баланс* - информация о финансах и крипте\n"
        text += "• 🎰 *Кейсы* - азартные покупки с наградами\n"
        text += "• ⚙️ *Параметры* - настройки игры и профиля\n\n"

        text += "⚔️ *Боссфайты:*\n"
        text += "• Запускаются администратором\n"
        text += "• Тратьте крипту для атаки босса\n"
        text += "• Топ-3 получают награды и титулы\n"
        text += "• Лимит затрат: 50,000₽ на игрока\n\n"

        text += "⚙️ *Крафтинг:*\n"
        text += "• 2 одинаковые карты → 1 улучшенная V2\n"
        text += "• V2: +3% дохода, +5% энергии\n"
        text += "• Разборка V2 стоит 10,000₽\n\n"

        text += "📞 *Поддержка:* @nktplv"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

    # ==================== СОХРАНЕНИЕ И ЗАГРУЗКА ====================

    def save_data(self):
        data = {
            "user_data": self.user_data,
            "active_bosses": self.active_bosses,
            "promo_codes": self.promo_codes,
            "last_save": datetime.now().isoformat()
        }
        with open("kukish_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open("kukish_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_data = {int(k): v for k, v in data["user_data"].items()}
                self.active_bosses = data.get("active_bosses", {})
                self.promo_codes = data.get("promo_codes", {})
        except FileNotFoundError:
            pass

    # ==================== ЗАПУСК БОТА ====================

    def setup_handlers(self, application: Application):
        # Команды
        application.add_handler(CommandHandler("start", self.start_command))

        # Обработчики кнопок
        application.add_handler(CallbackQueryHandler(self.button_handler))

        # Сохранение данных каждые 5 минут
        async def auto_save(context: ContextTypes.DEFAULT_TYPE):
            self.save_data()

        job_queue = application.job_queue
        if job_queue:
            job_queue.run_repeating(auto_save, interval=300, first=10)

# ==================== ЗАПУСК ====================

async def main():
    bot = KukishCryptoMiningBot()
    bot.load_data()

    # Замените 'YOUR_BOT_TOKEN' на реальный токен
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

    bot.setup_handlers(application)

    # Запуск бота
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("Бот Kukish Crypto Mining запущен!")

    # Бесконечный цикл
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```
