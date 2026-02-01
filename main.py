import json

class Distributor:
    def __init__(self, user_id, name, personal_volume=0):
        self.user_id = user_id
        self.name = name
        self.personal_volume = personal_volume  # ЛО (Личный объем)
        self.group_volume = 0                   # ГО (Групповой объем)
        self.rank_percent = 0                   # Текущий процент выплат
        self.rank_name = "Start"                # Название ранга
        self.downline = []                      # Структура

    def add_partner(self, partner):
        self.downline.append(partner)

    def calculate_group_volume(self):
        """1. Считаем ГО (снизу вверх)"""
        volume = self.personal_volume
        for partner in self.downline:
            volume += partner.calculate_group_volume()
        self.group_volume = volume
        return volume

    def update_rank(self, marketing_plan):
        """2. Определяем ранг на основе ГО"""
        # Сначала обновляем ранги у нижних (рекурсия)
        for partner in self.downline:
            partner.update_rank(marketing_plan)

        # Теперь у себя. Ищем максимально возможный ранг
        # Сортируем план по объему, чтобы найти высший подходящий
        sorted_plan = sorted(marketing_plan.items(), key=lambda x: x[1]['volume'])
        
        for name, data in sorted_plan:
            required_vol = data['volume']
            if self.group_volume >= required_vol:
                self.rank_name = name
                self.rank_percent = data['percent']

    def calculate_bonus(self):
        """3. Считаем деньги (Разница процентов - Stair Step)"""
        total_bonus = 0
        
        # А. Бонус с личного объема (Cashback)
        personal_bonus = self.personal_volume * self.rank_percent
        total_bonus += personal_bonus
        
        print(f"\n--- {self.name} (Ранг: {self.rank_name}, Ставка: {self.rank_percent*100:.0f}%) ---")
        print(f"Личный бонус: {self.personal_volume} * {self.rank_percent:.2f} = {personal_bonus:.2f}")

        # Б. Бонус с веток (Дифференциальный)
        for partner in self.downline:
            # Наш процент минус процент партнера
            diff_percent = self.rank_percent - partner.rank_percent
            
            # В ступенчатом маркетинге, если партнер догнал - ноль (или минимальный фикс, здесь пока 0)
            if diff_percent < 0: diff_percent = 0
            
            branch_bonus = partner.group_volume * diff_percent
            total_bonus += branch_bonus
            
            if branch_bonus > 0:
                print(f"Бонус с ветки {partner.name}: {partner.group_volume} баллов * {diff_percent*100:.1f}% = {branch_bonus:.2f}")
            else:
                print(f"Ветка {partner.name}: Обгон/Равенство ({partner.rank_percent*100:.0f}% vs {self.rank_percent*100:.0f}%) -> 0.00")

        return total_bonus

# --- НАСТРОЙКИ И ЗАПУСК СИМУЛЯЦИИ ---

if __name__ == "__main__":
    # 1. МАРКЕТИНГ-ПЛАН (Ступенчатый)
    # Имя ранга : {Объем для входа, Процент выплат}
    PLAN = {
        "Start":    {"volume": 0,    "percent": 0.00},
        "Partner":  {"volume": 500,  "percent": 0.05}, # 5% от 500 баллов
        "Manager":  {"volume": 1000, "percent": 0.10}, # 10% от 1000 баллов
        "Leader":   {"volume": 3000, "percent": 0.15}, # 15% от 3000 баллов
        "Top":      {"volume": 10000,"percent": 0.21}  # 21% от 10000 баллов
    }

    # 2. СТРОИМ СТРУКТУРУ
    # Ты (Павел)
    me = Distributor(1, "Павел (Ты)", personal_volume=200)

    # Ветка 1: Сильный лидер (Олег) - сделал сам 1000 баллов
    oleg = Distributor(2, "Олег (Лидер)", personal_volume=1000) 
    
    # Ветка 2: Развивающаяся (Мария + её люди)
    maria = Distributor(3, "Мария", personal_volume=100)
    novichok1 = Distributor(4, "Новичок 1", personal_volume=300)
    novichok2 = Distributor(5, "Новичок 2", personal_volume=300)
    
    # Собираем дерево (кто под кем)
    me.add_partner(oleg)
    me.add_partner(maria)
    
    maria.add_partner(novichok1)
    maria.add_partner(novichok2)

    # 3. ЗАПУСКАЕМ РАСЧЕТ
    print(">>> РАСЧЕТ СТУПЕНЧАТОГО МАРКЕТИНГА v2.0 <<<")
    
    # Шаг А: Считаем обороты (снизу вверх)
    me.calculate_group_volume()
    print(f"Твой Групповой Объем (ГО): {me.group_volume}")
    
    # Шаг Б: Раздаем ранги всем участникам
    me.update_rank(PLAN)
    
    # Шаг В: Считаем деньги
    income = me.calculate_bonus()
    
    print("-" * 30)
    print(f"ИТОГО ТВОЙ ЧЕК: {income:.2f} у.е.")
