import telebot
import pandas as pd
import os
import json

BOT_TOKEN = '7632052643:AAGfjD7Jn7a1QouEGLZDAz0IfDmhIEDCxcI'
bot = telebot.TeleBot(BOT_TOKEN)

EXCEL_FILE = r'D:\Download\Отчет по домашним заданиям.xlsx'

TEACHER_IDS_FILE = 'teacher_ids.json'

teacher_ids = {}

def load_teacher_ids():
    global teacher_ids
    if os.path.exists(TEACHER_IDS_FILE):
        with open(TEACHER_IDS_FILE, 'r') as file:
            teacher_ids = json.load(file)

def save_teacher_ids():
    with open(TEACHER_IDS_FILE, 'w') as file:
        json.dump(teacher_ids, file)

def calculate_homework_percentage(file_path):
    df = pd.read_excel(file_path, header=1)
    print("Columns in DataFrame:", df.columns)
    results = {}

    teacher_col = 'Unnamed: 1'
    issued_cols = ['Выдано', 'Выдано.1', 'Выдано.2']
    checked_cols = ['Проверено', 'Проверено.1', 'Проверено.2']

    for index, row in df.iterrows():
        if pd.notna(row[teacher_col]):
            teacher_name = row[teacher_col]
            total_homeworks = sum(row[issued_col] for issued_col in issued_cols if pd.notna(row[issued_col]))
            checked_homeworks = sum(row[checked_col] for checked_col in checked_cols if pd.notna(row[checked_col]))
            print(f"Processing row {index}: {teacher_name}, Total: {total_homeworks}, Checked: {checked_homeworks}")

            if teacher_name not in results:
                results[teacher_name] = {'total': 0, 'checked': 0}
            results[teacher_name]['total'] += total_homeworks
            results[teacher_name]['checked'] += checked_homeworks

    percentages = []
    for teacher, data in results.items():
        total_homeworks = data['total']
        checked_homeworks = data['checked']
        if total_homeworks > 0:
            percentage = (checked_homeworks / total_homeworks) * 100
        else:
            percentage = 0
        percentages.append((teacher, percentage))

    return percentages

def send_notifications():
    results = calculate_homework_percentage(EXCEL_FILE)
    for teacher, percentage in results:
        if percentage < 75:
            teacher_id = teacher_ids.get(teacher)
            if teacher_id:
                message = f"Внимание! Процент проверенных домашних заданий ниже 75%. Текущий процент: {percentage:.2f}%"
                bot.send_message(teacher_id, message)

def send_percentages(chat_id):
    results = calculate_homework_percentage(EXCEL_FILE)
    print("Results from calculate_homework_percentage:", results)
    if results:
        message_text = "Процент проверенных домашних заданий для каждого педагога:\n"
        for teacher, percentage in results:
            message_text += f"{teacher}: {percentage:.2f}%\n"
        bot.send_message(chat_id, message_text)
    else:
        bot.send_message(chat_id, "Нет данных для отображения.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для отслеживания проверенных домашних заданий. Пожалуйста, зарегистрируйтесь, отправив команду /register.")

@bot.message_handler(commands=['register'])
def register(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите ваше ФИО:")
    bot.register_next_step_handler(message, process_name_step)

def process_name_step(message):
    teacher_name = message.text
    teacher_ids[teacher_name] = message.chat.id
    save_teacher_ids()
    bot.send_message(message.chat.id, f"Спасибо, {teacher_name}! Вы зарегистрированы.")

@bot.message_handler(commands=['check'])
def check_homework(message):
    send_notifications()
    bot.reply_to(message, "Проверка процента проверенных домашних заданий завершена.")
@bot.message_handler(commands=['percent'])
def show_percentages(message):
    send_percentages(message.chat.id)

@bot.message_handler(commands=['clear'])
def clear_teacher_ids(message):
    global teacher_ids
    teacher_ids.clear()
    save_teacher_ids()  #
    bot.reply_to(message, "Словарь teacher_ids очищен.")

if __name__ == "__main__":
    load_teacher_ids()
    bot.polling()