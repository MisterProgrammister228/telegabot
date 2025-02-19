import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import urllib3
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import random
import os
import re
import telegramcalendar  # Правильный импорт

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Замените на ваш токен!
botTimeWeb = telebot.TeleBot('7717938491:AAFnmme6-KvrQqy7cvwovYq3hGLgLuE9Ua0') # Замените YOUR_BOT_TOKEN на ваш токен
logging.basicConfig(level=logging.DEBUG)

selected_group = None
selected_date = None
group_list = [
    '11б221', '11б231', '11б242', '11бд232', '11веб241', '11зб211', '11зб221', '11зб231', '11зб241', '11зем232', '11зем233', '11зем242', '11зпд211', '11зпд221', '11зпд222', '11зпд231', '11зпд241', '11зт211', '11зт221', '11исип232', '11оиб222', '11оиб232', '11оиб242', '11пд224', '11пд225', '11пд235', '11пд236', '11пд246', '11пд247', '11пд248', '11сса221', '11сса231', '11сса242', '11т232', '11тд242', '11эк221', '11ю243', '9б241', '9бд221', '9бд222', '9бд231', '9бд241', '9бд242', '9зем231', '9зем241', '9зио221', '9исип211', '9исип221', '9исип222', '9исип231', '9исип241', '9исип242', '9оиб211', '9оиб221', '9оиб231', '9оиб241', '9пд211', '9пд212', '9пд213', '9пд221', '9пд222', '9пд223', '9пд231', '9пд232', '9пд233', '9пд234', '9пд241', '9пд242', '9пд243', '9пд244', '9пд245', '9псо221', '9псо231', '9сд231', '9сд241', '9сса241', '9т221', '9т231', '9тд241', '9тор211', '9тор221', '9ф221', '9ф231', '9ф241', '9ю241', '9ю242', 'бд бжд юноши', 'псо бжд юноши'
]
super_admins = [2092122666] # Ваш ID администратора
group_admins = {}  # {group: [user_id]}
homeworks = {} # {group: [{date: '', subject: '', text: '', photo_links: []}]}
DATA_FILE = "bot_data.json"

def load_data():
    global group_admins, homeworks
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            group_admins = data.get('group_admins', {})
            homeworks = data.get('homeworks', {})
            logging.debug(f"Data loaded: group_admins: {group_admins}  homeworks: {homeworks}")


def save_data():
    data = {'group_admins': group_admins, 'homeworks': homeworks}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
       json.dump(data, f, ensure_ascii=False, indent=4)
       logging.debug(f"Data saved: group_admins: {group_admins}  homeworks: {homeworks}")
load_data()

def download_chromedriver():
    try:
        driver_path = ChromeDriverManager().install()
        logging.debug(f"Downloaded ChromeDriver to: {driver_path}")
        return driver_path
    except Exception as e:
        logging.error(f"Error downloading ChromeDriver: {e}")
        return None


def get_data_from_site(url, start_date, end_date, group):
    logging.debug(f"get_data_from_site called, URL {url}, start_date: {start_date}, end_date: {end_date}, group {group}")
    chrome_options = Options()
    driver_path = download_chromedriver()
    if driver_path is None:
        return "Не удалось получить драйвер Chrome. Попробуйте позже"

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')  # Устанавливаем случайный User-Agent
    chrome_options.add_argument("--headless=new") #запуск в headless режиме
    chrome_options.add_experimental_option("detach", True) # Добавляем detach

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options) # Убрали detach
        driver.get(url)
        logging.debug(f"Page opened, URL {url}")
        time.sleep(3)

        group_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//select[@id='gruppa']")))
        group_select.send_keys(group)
        logging.debug(f"Group {group} set")
        time.sleep(1)

        calendar_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='calendar']")))
        logging.debug(f"Calendar found.")
        calendar_input.clear()
        calendar_input.send_keys(start_date)
        logging.debug(f"Set calendar start date to {start_date}")
        time.sleep(1)

        calendar_input2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='calendar2']")))
        logging.debug(f"Calendar2 found.")
        calendar_input2.clear()
        calendar_input2.send_keys(end_date)
        logging.debug(f"Set calendar end date to {end_date}")
        time.sleep(1)

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"][contains(@value, "Выбрать")]'))
        )
        submit_button.click()
        logging.debug(f"Clicked submit")

        # Ожидание завершения выполнения JavaScript
        try:
            WebDriverWait(driver, 60).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            logging.debug("JavaScript execution completed.")
        except TimeoutException:
            logging.error("Timeout waiting for JavaScript execution to complete.")
            return "Расписание не было загружено из-за таймаута JavaScript"

        time.sleep(5)
        page_source = driver.page_source
        logging.debug(f"Page source AFTER JS:\n{page_source}")
        soup = BeautifulSoup(page_source, 'html.parser')
        table = soup.find('table', class_='table-3') # более точный поиск таблицы
        if table is None:
            return "Не удалось найти таблицу расписания"
        
        formatted_schedule = ""
        tables = soup.find_all('div', id='content')  # Находим все div с id='content'
        if not tables:
            return "Не удалось найти таблицы расписания"
        
        current_day = None
        for table_div in tables:
            table = table_div.find('table', class_='table-3') # Находим таблицы с классом table-3 внутри div
            if table:
                rows = table.find_all('tr')
                for row in rows:
                   cells = row.find_all('td')
                   if cells: # Проверяем, есть ли ячейки в строке
                        if len(cells) == 1 and cells[0].has_attr('data-label') and cells[0]['data-label'] == 'Дата': # Проверка строки с датой
                            day_info = cells[0].text.strip()
                            if day_info != current_day:
                                if current_day:
                                   formatted_schedule += "\n"
                                formatted_schedule += f"🗓️ *{day_info}*\n\n"
                                current_day = day_info
                        elif len(cells) >= 6:
                            formatted_schedule += f"⏰ {cells[0].text.strip()}\n" \
                                                    f"🧑‍🎓 {cells[1].text.strip()}\n" \
                                                    f"📚 {cells[2].text.strip()}\n" \
                                                    f"👨‍🏫 {cells[3].text.strip()}\n" \
                                                    f"🏢 {cells[4].text.strip()}\n" \
                                                    f"📍 {cells[5].text.strip()}\n\n"

        return formatted_schedule
    except Exception as e:
        import traceback
        logging.error(f"Error during parsing: {e}")
        logging.error(traceback.format_exc())
        return f"Произошла ошибка при получении расписания. {e}"
    finally:
        if driver:
           driver.quit()
           
def get_current_week_dates(week_offset=0):
    today = date.today()
    start_weekday = today.weekday()
    start_date = today + timedelta(days=-start_weekday + (week_offset * 7))
    end_date = start_date + timedelta(days=(5 - start_date.weekday()))
    return start_date.strftime("%d.%m.%Y"), end_date.strftime("%d.%m.%Y")

@botTimeWeb.message_handler(commands=['start', 'resetgroup'])
def start_command(message):
    global selected_group, selected_date
    selected_group = None
    selected_date = None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_group = types.KeyboardButton('Ввести группу')
    markup.add(button_group)
    botTimeWeb.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    #botTimeWeb.register_next_step_handler(message, handle_group_input) # Убрали, команда будет обрабатываться в handle_commands


@botTimeWeb.message_handler(func=lambda message: message.text and message.text.lower() == 'ввести группу')
def handle_group_input(message): # Функция теперь обрабатывает ввод
    botTimeWeb.send_message(message.chat.id, 'Введите название группы:')
    botTimeWeb.register_next_step_handler(message, get_group)


def get_group(message):
    global selected_group
    group = message.text.strip().lower()
    if group in group_list:
        selected_group = group # сохраняем группу
        send_schedule_options(message)
    else:
        botTimeWeb.send_message(message.chat.id, 'Неверная группа. Попробуйте еще раз.')
        botTimeWeb.register_next_step_handler(message, get_group)


def send_schedule_options(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Эта неделя', 'Следующая неделя', 'Посмотреть по датам', 'Сбросить группу')
    markup.add('Домашнее задание')
    botTimeWeb.send_message(message.chat.id, 'Выберите вариант:', reply_markup=markup)
    botTimeWeb.register_next_step_handler(message, process_schedule_option)


def process_schedule_option(message):
    option = message.text
    if option.lower() == 'эта неделя':
        start_date, end_date = get_current_week_dates(0)
        get_schedule_by_week(message, start_date, end_date, message)
    elif option.lower() == 'следующая неделя':
        start_date, end_date = get_current_week_dates(1)
        get_schedule_by_week(message, start_date, end_date, message)
    elif option.lower() == 'посмотреть по датам':
        get_schedule_by_date(message)
    elif option.lower() == 'сбросить группу':
         reset_bot(message)
    elif option.lower() == 'домашнее задание':
         send_homework_options(message)
    else:
        botTimeWeb.send_message(message.chat.id, "Неверный выбор. Пожалуйста, выберите еще раз.")
        send_schedule_options(message)


def get_schedule_by_week(message, start_date, end_date, start_message):
    global selected_group
    if selected_group is None:
        botTimeWeb.send_message(message.chat.id, "Выберите группу сначала.")
        return
    schedule_data = get_data_from_site(
        "https://asiec.ru/ras/?ysclid=lrm05c7g58540524053",
        start_date,
        end_date,
        selected_group,
    )
    if schedule_data and not "Не удалось получить расписание" in schedule_data:
        if schedule_data.strip() : # Проверяем, что строка не пустая
             botTimeWeb.send_message(message.chat.id, schedule_data, parse_mode="Markdown")
        else:
            botTimeWeb.send_message(message.chat.id, "Расписание не найдено.")
    else:
        botTimeWeb.send_message(message.chat.id, "Не удалось получить расписание с сайта. Попробуйте позже.")
    
    send_schedule_options(start_message) # Возвращаем к выбору варианта

def get_schedule_by_date(message):
    calendar_markup = telegramcalendar.create_calendar()
    botTimeWeb.send_message(
        message.chat.id,
        "Пожалуйста, выберите дату:",
        reply_markup=calendar_markup
    )


@botTimeWeb.callback_query_handler(func=lambda call: True)
def process_callback(call):
    global selected_date
    selected, date_obj = telegramcalendar.process_calendar_selection(botTimeWeb, call)
    if selected:
        selected_date = date_obj
        schedule_data = get_data_from_site(
            "https://asiec.ru/ras/?ysclid=lrm05c7g58540524053",
            selected_date.strftime("%d.%m.%Y"),
            selected_date.strftime("%d.%m.%Y"),
            selected_group,
        )
        if schedule_data and not "Не удалось получить расписание" in schedule_data:
           if schedule_data.strip():  # Проверяем, что строка не пустая
               botTimeWeb.send_message(call.message.chat.id, schedule_data, parse_mode="Markdown")  # Убрали parse_mode
               send_schedule_options(call.message) # Вызываем функцию отправки клавиатуры
           else:
               botTimeWeb.send_message(call.message.chat.id, "Расписание не найдено.")
               send_schedule_options(call.message) # Вызываем функцию отправки клавиатуры
        else:
           botTimeWeb.send_message(call.message.chat.id, "Не удалось получить расписание с сайта. Попробуйте позже.")
           send_schedule_options(call.message) # Вызываем функцию отправки клавиатуры
    elif date_obj:
        botTimeWeb.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=date_obj
         )
    


@botTimeWeb.message_handler(func=lambda message: message.text and message.text.lower() == "сбросить")
def reset_bot(message):
     global selected_group
     selected_group = None  # Сбрасываем выбранную группу
     botTimeWeb.send_message(message.chat.id, "Введите название группы:")
     botTimeWeb.clear_step_handler(message.chat.id) # Сбрасываем шаг
     botTimeWeb.register_next_step_handler(message, get_group)

# Функции для домашнего задания
@botTimeWeb.message_handler(commands=['setadmin'])
def set_admin(message):
    if message.from_user.id not in super_admins:
        botTimeWeb.reply_to(message, "У вас нет прав для этой команды.")
        return
    botTimeWeb.send_message(message.chat.id, "Введите ID пользователя, которого хотите назначить админом группы и группу через пробел (пример: 123456789 9оиб241):")
    botTimeWeb.register_next_step_handler(message, process_set_admin)

def process_set_admin(message):
    try:
        user_id, group = message.text.split()
        user_id = int(user_id)
        if group in group_list:
           group_admins.setdefault(group, []).append(user_id)
           botTimeWeb.send_message(message.chat.id, f"Пользователь {user_id} назначен админом группы {group}.")
           save_data() # Сохраняем данные после назначения
        else:
           botTimeWeb.send_message(message.chat.id, "Неверная группа.")
    except ValueError:
       botTimeWeb.send_message(message.chat.id, "Неверный формат. Попробуйте еще раз.")

@botTimeWeb.message_handler(commands=['setadmin', 'addhw', 'gethw', 'removehw'], func=lambda message: True)
def handle_commands(message):
    if message.text == '/setadmin':
        set_admin(message)
    elif message.text == '/addhw':
         add_homework(message)
    elif message.text == '/gethw':
        get_homework(message)
    elif message.text == '/removehw':
        remove_homework_command(message)
    botTimeWeb.clear_step_handler(message.chat.id) # Очищаем шаг
    if selected_group is None:
        botTimeWeb.send_message(message.chat.id, "Введите название группы:")
        botTimeWeb.register_next_step_handler(message, get_group) # возвращаем к вводу группы
    else:
        send_schedule_options(message) # Иначе в меню

def send_homework_options(message):
    global selected_group
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if selected_group in group_admins and message.from_user.id in group_admins[selected_group]:
         button_add = types.KeyboardButton('Добавить ДЗ')
         markup.add(button_add)
         button_remove = types.KeyboardButton('Удалить ДЗ') # Добавили кнопку удаления
         markup.add(button_remove)
    button_get = types.KeyboardButton('Получить ДЗ')
    markup.add(button_get)
    markup.add('Назад')
    botTimeWeb.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    botTimeWeb.register_next_step_handler(message, process_homework_option)


def process_homework_option(message):
    if message.text.lower() == 'добавить дз':
        add_homework(message)
    elif message.text.lower() == 'получить дз':
         get_homework(message)
    elif message.text.lower() == 'удалить дз': # Добавили обработку удаления
         remove_homework_command(message)
    elif message.text.lower() == 'назад': # Обработка кнопки "Назад"
         send_schedule_options(message) # Возвращаем к меню расписания
    else:
        botTimeWeb.send_message(message.chat.id, "Неверный выбор, пожалуйста, выберите из предложенного.")
        send_homework_options(message)

@botTimeWeb.message_handler(func=lambda message: message.text and message.text.lower() == 'добавить дз')
def add_homework(message):
    global selected_group
    user_id = message.from_user.id
    if selected_group is None:
        botTimeWeb.reply_to(message, "Выберите группу сначала.")
        return

    if selected_group not in group_admins or user_id not in group_admins[selected_group]:
       botTimeWeb.reply_to(message, "Вы не являетесь админом этой группы.")
       return

    botTimeWeb.send_message(message.chat.id, "Введите дату для задания (пример: 23.01.2025):")
    botTimeWeb.register_next_step_handler(message, process_add_or_edit_homework_date, selected_group)


def process_add_or_edit_homework_date(message, group):
   try:
       date_obj = datetime.strptime(message.text, '%d.%m.%Y').date()
       botTimeWeb.send_message(message.chat.id, "Введите название предмета:")
       botTimeWeb.register_next_step_handler(message, process_add_or_edit_homework_subject, group, date_obj.strftime("%d.%m.%Y"))
   except ValueError:
       botTimeWeb.send_message(message.chat.id, "Неверный формат даты, попробуйте еще раз.")
       botTimeWeb.register_next_step_handler(message, process_add_or_edit_homework_date, group)


def process_add_or_edit_homework_subject(message, group, hw_date):
    subject = message.text
    #Проверяем есть ли такое задание
    existing_hw_index = None
    if group in homeworks:
        for index, hw in enumerate(homeworks[group]):
            if hw['date'] == hw_date and hw['subject'] == subject:
                existing_hw_index = index
                break
    if existing_hw_index is not None:
       botTimeWeb.send_message(message.chat.id, "Найдено существующее ДЗ. Теперь введите новый текст домашнего задания или отправьте ссылку на фото (отправьте /done, чтобы завершить редактирование ДЗ):")
       botTimeWeb.register_next_step_handler(message, process_add_homework_content, group, existing_hw_index)
    else:
        homeworks.setdefault(group, []).append({"date": hw_date, "subject": subject, "text": "", "photo_links": []})
        botTimeWeb.send_message(message.chat.id, "Теперь введите текст домашнего задания или отправьте ссылку на фото (отправьте /done, чтобы завершить добавление ДЗ):")
        botTimeWeb.register_next_step_handler(message, process_add_homework_content, group, len(homeworks[group]) - 1)


def process_add_homework_content(message, group, hw_index):
    if message.text == '/done':
        botTimeWeb.send_message(message.chat.id, "Домашнее задание успешно добавлено.")
        send_homework_options(message)
        save_data() # Сохраняем ДЗ после добавления
        return
    homeworks[group][hw_index]["text"] = message.text if message.text else '' # Сохраняем текст

    if message.text.startswith('http'):
        homeworks[group][hw_index]['photo_links'].append(message.text)
        botTimeWeb.send_message(message.chat.id, "Ссылка на фото добавлена. Отправьте еще ссылку или /done.")
        botTimeWeb.register_next_step_handler(message, process_add_homework_content, group, hw_index)
    else:
       botTimeWeb.send_message(message.chat.id, "Текст задания добавлен. Теперь вы можете отправлять ссылки на фото или /done.")
       botTimeWeb.register_next_step_handler(message, process_add_homework_content, group, hw_index)
    
@botTimeWeb.message_handler(func=lambda message: message.text and message.text.lower() == 'получить дз')
def get_homework(message):
    global selected_group
    if selected_group is None:
       botTimeWeb.reply_to(message, "Выберите группу сначала.")
       return
    botTimeWeb.send_message(message.chat.id, "Введите дату (пример: 23.01.2025) или введите 'all' для получения всех заданий:",)
    botTimeWeb.register_next_step_handler(message, process_get_homework, selected_group)


def process_get_homework(message, group):
    if message.text.lower() == 'all':
        if group in homeworks:
            for hw in homeworks[group]:
                botTimeWeb.send_message(message.chat.id, f"🗓️ {hw['date']}\n📚 {hw['subject']}\n-----ДЗ-----\n{hw['text']}")
                if hw['photo_links']:
                    for photo_link in hw['photo_links']:
                        botTimeWeb.send_message(message.chat.id, photo_link)
            send_homework_options(message)
        else:
            botTimeWeb.send_message(message.chat.id, "Для этой группы нет домашнего задания")
            send_homework_options(message)
    else:
        try:
            selected_date = datetime.strptime(message.text, '%d.%m.%Y').date().strftime("%d.%m.%Y")
            if group in homeworks:
                for hw in homeworks[group]:
                    if hw['date'] == selected_date:
                        botTimeWeb.send_message(message.chat.id, f"🗓️ {hw['date']}\n📚 {hw['subject']}\n-----ДЗ-----\n{hw['text']}")
                        if hw['photo_links']:
                            for photo_link in hw['photo_links']:
                                botTimeWeb.send_message(message.chat.id, photo_link)
                send_homework_options(message)
            else:
                botTimeWeb.send_message(message.chat.id, "Для этой группы нет домашнего задания")
                send_homework_options(message)

        except ValueError:
            botTimeWeb.send_message(message.chat.id, "Неверный формат даты. Попробуйте еще раз.")
            botTimeWeb.register_next_step_handler(message, process_get_homework, group)

@botTimeWeb.message_handler(commands=['removehw'])
def remove_homework_command(message):
    if message.from_user.id not in super_admins:
        botTimeWeb.reply_to(message, "У вас нет прав для этой команды.")
        return
    botTimeWeb.send_message(message.chat.id, "Введите дату, предмет и группу через пробел для удаления ДЗ (пример: 24.01.2025 Математика 9оиб241):")
    botTimeWeb.register_next_step_handler(message, process_remove_homework)


def process_remove_homework(message):
    try:
        match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+(.+)\s+(\w+)", message.text) # Используем регулярное выражение
        if match:
            hw_date, subject, group = match.groups()
            hw_date = datetime.strptime(hw_date, '%d.%m.%Y').date().strftime("%d.%m.%Y")
            group = group.lower()
            if group in homeworks:
                new_homeworks = [hw for hw in homeworks[group] if not (hw['date'] == hw_date and hw['subject'] == subject)]
                homeworks[group] = new_homeworks
                botTimeWeb.send_message(message.chat.id, f"Домашнее задание для группы {group} на {hw_date} по предмету {subject} удалено.")
                save_data()
            else:
                botTimeWeb.send_message(message.chat.id, f"Домашнее задание для группы {group} на {hw_date} по предмету {subject} не найдено.")
        else:
            botTimeWeb.send_message(message.chat.id, "Неверный формат. Попробуйте еще раз.")
    except ValueError:
        botTimeWeb.send_message(message.chat.id, "Неверный формат даты. Попробуйте еще раз.")

botTimeWeb.polling()
