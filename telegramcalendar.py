from datetime import datetime, timedelta
from telebot import types
import calendar
import locale

def create_calendar(year=None, month=None):
    now = datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    
    cal = calendar.monthcalendar(year, month)
    
    # Set locale to Russian to get month name in Russian
    try:
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8') # Попробуйте ru_RU.UTF-8
    except locale.Error:
          try:
               locale.setlocale(locale.LC_ALL, 'ru_RU') # Попробуйте ru_RU
          except locale.Error:
               try:
                  locale.setlocale(locale.LC_ALL, 'ru') # Попробуйте ru
               except locale.Error:
                    print('Не удалось установить русскую локаль.')
    month_name = datetime(year, month, 1).strftime("%B %Y")
    
    markup = types.InlineKeyboardMarkup(row_width=7)
    # First row: Month and year with navigation buttons
    prev_month = (datetime(year, month, 1) - timedelta(days=1)).strftime("%Y-%m")
    next_month = (datetime(year, month, 1) + timedelta(days=32)).strftime("%Y-%m")
    markup.add(
        types.InlineKeyboardButton(text="<", callback_data=_create_callback_data("prev-month", prev_month)),
        types.InlineKeyboardButton(text=month_name.capitalize(), callback_data="ignore"),  # Отображение месяца на русском
        types.InlineKeyboardButton(text=">", callback_data=_create_callback_data("next-month", next_month)),
    )
    
    # Second row: Days of the week
    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    markup.add(*[types.InlineKeyboardButton(text=day, callback_data="ignore") for day in days_of_week])

    # Calendar rows - Days
    for week in cal:
        buttons = []
        for day in week:
            if day == 0:
                buttons.append(types.InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                buttons.append(types.InlineKeyboardButton(
                    text=str(day),
                    callback_data=_create_callback_data("day", year, month, day))
                )
        markup.add(*buttons)

    return markup


def process_calendar_selection(bot, update):
    callback_data = update.data # Исправили обращение
    if callback_data.startswith("calendar-"):
        action, data = callback_data[9:].split(":")
        now = datetime.now()
        if action == "day":
            year, month, day = map(int, data.split("-"))
            return True, datetime(year, month, day).date()
        elif action in ["prev-month", "next-month"]:
            year, month = map(int, data.split("-"))
            markup = create_calendar(year=year, month=month)
            return False, markup
    else:
        return False, None



def _create_callback_data(action, *args):
    return f"calendar-{action}:{'-'.join(map(str, args))}"


def _month_days(year, month):
    day_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        day_count[1] = 29
    return range(1, day_count[month-1] + 1)