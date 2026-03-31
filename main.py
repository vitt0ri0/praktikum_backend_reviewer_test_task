# Комментарии по стилю: Посмотри пожалуйста требования к коду (https://docs.google.com/document/d/1s_FqVkqOASwXK0DkOJZj5RzOm4iWBO5voc_8kenxXbw/edit?tab=t.0) и перед коммитом стоит использовать uv / black / isort одну из утилит для упрощения себе жизни
# - Уточню некоторые несоблюденные пункты: констистентность кавычек, бэкслеши, отступы. 
# - Не хватает docstrings для методов


import datetime as dt


class Record:
    def __init__(self, amount, comment, date=""):
        self.amount = amount
        self.date = (
            dt.datetime.now().date()
            # стоит проверить синтаксис, похоже на ошибку, и можно сделать if date: (обрезать строку), без лишнего else и not
            if not date
            else dt.datetime.strptime(date, "%d.%m.%Y").date()
        )
        self.comment = comment


class Calculator:
    def __init__(self, limit):
        self.limit = limit
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def get_today_stats(self):
        today_stats = 0

        # здесь происходит что-то странное, и похоже обращаемся не к экземпляру класса, а к самому классу Record, нужно проверить и поправить
        for Record in self.records: 
            if Record.date == dt.datetime.now().date():
                today_stats = today_stats + Record.amount
        return today_stats

    def get_week_stats(self):
        week_stats = 0
        today = dt.datetime.now().date()
        for record in self.records:
            if (today - record.date).days < 7 and (today - record.date).days >= 0:
                week_stats += record.amount
        return week_stats


class CaloriesCalculator(Calculator):
    def get_calories_remained(self):  # Получает остаток калорий на сегодня
        x = self.limit - self.get_today_stats()
        if x > 0:
            return (
                # строки взаимодействия с клиентов я бы вынес в константы. В продакшене это обычно на стороне фронтенда. Но если рабоатем с апи, то эти коснтанты часто в БД, и их может менять админ продукта. 
                f"Сегодня можно съесть что-нибудь"
                f" ещё, но с общей калорийностью не более {x} кКал"
            )
        else: # лишний else, так как если условие не выполняется, то функция все равно вернет результат
            return "Хватит есть!"


class CashCalculator(Calculator):
    # Рекомендация: инициалиизровать константы лучше в отдельном классе, т.к. в перспективе их получение 
    # будет либо из БД, либо из API
    # Можно назвать метод get_currency_rate и вызывать его внутри get_today_cash_remained, 
    # тогда не нужно будет передавать эти константы в виде аргументов метода, 
    # а также не нужно будет их объявлять в виде атрибутов класса, 
    # так как они не будут использоваться нигде кроме этого метода
    USD_RATE = float(60)  # Курс доллар США.
    EURO_RATE = float(70)  # Курс Евро.

    def get_today_cash_remained(self, currency, USD_RATE=USD_RATE, EURO_RATE=EURO_RATE):
        currency_type = currency
        cash_remained = self.limit - self.get_today_stats()
        # логику вычисления можно упростить, и сделать if только для currency, а внутри него уже делать вычисления, тогда не нужно будет дублировать код для каждого типа валюты
        if currency == "usd":  # стоит сравнивать currency с константой, которые лучше объявить в начале файла, например, CURRENCY_USD = "usd"
            cash_remained /= USD_RATE
            currency_type = "USD"
        elif currency_type == "eur":
            cash_remained /= EURO_RATE
            currency_type = "Euro"
        elif currency_type == "rub":
            cash_remained == 1.00 # хардкод для рубля? коммента, наверное, не хватает. 
            currency_type = "руб"

        # опять же, можно делать if (...): return (...) без else. 
        if cash_remained > 0:
            return f"На сегодня осталось {round(cash_remained, 2)} {currency_type}"
        elif cash_remained == 0:
            return "Денег нет, держись"
        elif cash_remained < 0:
            return "Денег нет, держись: твой долг - {0:.2f} {1}".format(
                -cash_remained, currency_type
            )

    # избыточный вызов родительского метода, так как он ничего не меняет в дочернем классе. Стоит либо удалить либо переопределить.
    def get_week_stats(self):
        super().get_week_stats()

if __name__ == "__main__":
    # создадим калькулятор денег с дневным лимитом 1000
    cash_calculator = CashCalculator(1000)
            
    # дата в параметрах не указана, 
    # так что по умолчанию к записи должна автоматически добавиться сегодняшняя дата
    cash_calculator.add_record(Record(amount=145, comment="кофе")) 
    # и к этой записи тоже дата должна добавиться автоматически
    cash_calculator.add_record(Record(amount=300, comment="Серёге за обед"))
    # а тут пользователь указал дату, сохраняем её
    cash_calculator.add_record(Record(amount=3000, comment="бар в Танин др", date="08.11.2019"))
                    
    print(cash_calculator.get_today_cash_remained("rub"))
