import pandas as pd
import requests,os,json
from telebot import TeleBot, types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import custom_filters
from dotenv import load_dotenv
import time
import sqlite3
from calories import calories_possible

import models_testing.edaman_food as by_name
import models_testing.logmeal as by_photo
import recommend
from pathlib import Path
from pathlib import Path

load_dotenv()

# for menu buttons
TOKEN = os.getenv('TOKEN')
url="https://api.telegram.org/bot"+TOKEN+"/setMyCommands?commands="
cmd=[{
    "command":"start",
    "description":"to start registration of further actions"
},
{
    "command":"recommend",
    "description":"to see recommended dishes"
},
{
    "command":"calories",
    "description":"to find out calories you can consume for the day"
},
{
    "command":"cancel",
    "description":"to cancel last command"
}]
cmd=json.dumps(cmd)
url=url+str(cmd)
response=requests.get(url)
print(response)

state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, parse_mode=None, state_storage=state_storage)


class MyStates(StatesGroup):
    sex = State()
    height = State()
    age = State()
    weight_current = State()
    weight_desired = State()
    intensity = State()
    deficiency = State()
    survey = State()
    survey_in_process = State()
    calories = State()
    get_recommendation = State()
    enter_calories_manually =  State()
    find_calories_by_name = State()
    find_calories_by_photo = State()
    calories_decision = State()

def init_db(user_id) -> bool:
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM info WHERE id == {user_id}')
    records = cursor.fetchall()

    connection.commit()
    connection.close()

    return len(records) == 0

@bot.message_handler(commands=["start",])
def send_welcome(message):
    if init_db(message.from_user.id):
        bot.set_state(message.from_user.id, MyStates.sex, message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("M", "F")
        bot.send_message(
            message.chat.id, 
            "Hiiii! I mean, meoooow..\n" +
            "Hmm, I haven't seen you here.\n" +
            "Tell me about yourself so I can help you.\n" +
            "Let's start slow. Tell me your sex?\n" +
            "Type M if you are a man.\n" +
            "Type F if you are a woman.",
            reply_markup=markup
            )
    else:
        bot.send_message(
            message.chat.id, 
            f"Hiii, {message.from_user.username}! Have a puurrrfect day!", 
            reply_markup=types.ReplyKeyboardRemove()
            )

@bot.message_handler(state=MyStates.sex)
def get_sex(message):
    if message.text not in ["M", "F"]:
        bot.send_message(
            message.chat.id,
            "Choose one of the options: M or F.",
        )
    else:
        bot.send_message(
                message.chat.id,
                "Tell me your height in cm.",
                reply_markup=types.ReplyKeyboardRemove()
            )
        bot.set_state(message.from_user.id, MyStates.height, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["sex"] = message.text

@bot.message_handler(state=MyStates.height, is_digit=True)
def get_height(message):
    bot.send_message(
            message.chat.id,
            "How old are you?"
        )
    bot.set_state(message.from_user.id, MyStates.age, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["height"] = message.text

@bot.message_handler(state=MyStates.height, is_digit=False)
def height_incorrect(message):
    bot.send_message(
            message.chat.id,
            "Round up your height to cm."
        )

@bot.message_handler(state=MyStates.age, is_digit=True)
def get_age(message):
    bot.send_message(
            message.chat.id,
            "Enter your weight in kg."
        )
    bot.set_state(message.from_user.id, MyStates.weight_current, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["age"] = message.text

@bot.message_handler(state=MyStates.age, is_digit=False)
def age_incorrect(message):
    bot.send_message(
            message.chat.id,
            "Please, enter your age as a whole number."
        )

def check_float(message) -> bool:
    try:
        float(message.text)
        return True
    except ValueError:
        bot.send_message(message.chat.id, "Please, enter your weight in kg as a whole number or a decimal.")
        return False

@bot.message_handler(state=MyStates.weight_current)
def get_weight_current(message):
    if not check_float(message):
        return
    bot.send_message(
            message.chat.id,
            "What is your prefered weight?"
        )
    bot.set_state(message.from_user.id, MyStates.weight_desired, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["weight_current"] = message.text

@bot.message_handler(state=MyStates.weight_desired)
def get_weight_desired(message):
    if not check_float(message):
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("A little", "Medium", "Hard")
    bot.send_message(
            message.chat.id,
            "How intense do you usually exercise?",
            reply_markup=markup
        )
    bot.set_state(message.from_user.id, MyStates.intensity, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["weight_desired"] = message.text

@bot.message_handler(state=MyStates.intensity)
def get_intensity(message):
    variants = ["A little", "Medium", "Hard"]
    if message.text not in variants:
        bot.send_message(
            message.chat.id,
            "Please, enter A little, Medium or Hard."
        )
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Save", "Change")
        bot.send_message(
                message.chat.id,
                "Do you want to change your form?",
                reply_markup=markup
            )
        bot.set_state(message.from_user.id, MyStates.deficiency, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if message.text == variants[0]:
                data["intensity"] = str(1.2)
            elif message.text == variants[1]:
                data["intensity"] = str(1.46)
            elif message.text == variants[2]:
                data["intensity"] = str(1.72)

@bot.message_handler(state=MyStates.deficiency)
def get_deficiency(message):
    variants = ["Save", "Change"]
    if message.text not in variants:
        bot.send_message(
            message.chat.id,
            "Please, enter Save or Change."
        )
    else:
        bot.set_state(message.from_user.id, MyStates.deficiency, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if message.text == variants[0]:
                data["deficiency"] = str(10)
            elif message.text == variants[1]:
                data["deficiency"] = str(20)

        bot.send_message(
                message.chat.id,
                "So nice!\n" +
                "Here is your survey, you can change it at any moment, by entering Survey.\n\n" +
                "Sex: {}\n".format(data["sex"]) +
                "Height: {}\n".format(data["height"]) +
                "Age: {}\n".format(data["age"]) +
                "Current weight: {}\n".format(data["weight_current"]) +
                "Prefered weight: {}\n".format(data["weight_desired"]) +
                "Intensity factor: {}\n".format(data["intensity"]) +
                "Deficit: {}%".format(data["deficiency"]),
                reply_markup=types.ReplyKeyboardRemove()
            )
        bot.delete_state(message.from_user.id, message.chat.id)

        connection = sqlite3.connect("db/user.db")
        cursor = connection.cursor()

        cursor.execute(
            f'''
            INSERT INTO info (id, sex, height, age, weight_current, weight_desired, intensity, deficiency)
            VALUES ("{message.from_user.id}", "{data["sex"]}", "{data["height"]}", 
            "{data["age"]}", "{data["weight_current"]}", "{data["weight_desired"]}", 
            "{data["intensity"]}", "{data["deficiency"]}")
            '''
            )

        possible = calories_possible(data["sex"], int(data["height"]), int(data["age"]), 
                                     float(data["weight_current"]), float(data["intensity"]), int(data["deficiency"]))
        eaten = 0

        cursor.execute(
            f'''
            INSERT INTO calories (id, possible, eaten)
            VALUES ("{message.from_user.id}", "{possible}", "{eaten}")
            '''
        )

        connection.commit()
        connection.close()

@bot.message_handler(commands=["cancel"], state="*")
def cancel_state(message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
            message.chat.id,
            "Ok! Dialog is cancelled.",
            reply_markup=types.ReplyKeyboardRemove()
        )

def check_db_by_user(user_id, table):
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM {table} WHERE id_users == {user_id}')
    records = cursor.fetchall()

    connection.commit()
    connection.close()
    return records

@bot.message_handler(commands=["recommend",])
def start_recommendation(message):
    rated_recipes_num = len(check_db_by_user(message.from_user.id, 'rates'))
    if rated_recipes_num < 10:
        bot.set_state(message.from_user.id, MyStates.survey, message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Start a survey")
        if rated_recipes_num == 0:
            bot.send_message(
                message.chat.id, 
                "Please take the survey so that I can find out about your preferences. Then I will recommend you some delicious dishes!",
                reply_markup=markup
                )
        else:
            bot.send_message(
                message.chat.id, 
                "I need at least 10 evaluated dishes to recommend something properly.\n"
                "Now you have {} out of 10.".format(rated_recipes_num),
                reply_markup=markup
                )        
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Give me a recommendation")
        bot.send_message(message.chat.id, "I can recommend you some delicious dishes!",
                        reply_markup=markup)
        recommended = recommend.recommend(check_db_by_user(message.from_user.id, 'rates'))
        for i in recommended:
            print(i)
        print(check_db_by_user(message.from_user.id, 'rates'))
        bot.set_state(message.from_user.id, MyStates.get_recommendation, message.chat.id)

def get_recipe(user_id):
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()
    cursor.execute(f'SELECT id, recipe_name, image_url FROM recipes WHERE NOT EXISTS (SELECT id_recipes FROM rates WHERE id_users == {user_id} AND id_recipes == recipes.id)')
    records = cursor.fetchall()
    connection.commit()
    connection.close()
    return records[0]

def insert_to_db(table, values):
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()
    cursor.execute(f'INSERT INTO {table} VALUES ({values})')
    connection.commit()
    connection.close()

def remove_duplicate_dishes(user_id, rec_list):
    arr1 = pd.DataFrame(data = rec_list, columns = ['recipe_id', 'recipe_name', 'image_url'])
    recommended = check_db_by_user(user_id, 'recommendations')
    arr2 = pd.DataFrame(data = recommended, columns = ['user_id', 'recipe_id'])
    without_dupl = arr1[(~arr1['recipe_id'].isin(arr2['recipe_id']))]
    res = []
    for i in list(without_dupl.values):
        res.append(list(i))   
    return res

@bot.message_handler(state=MyStates.survey)
def start_survey(message):
    if message.text != "Start a survey":
        bot.send_message(
            message.chat.id,
            "Click 'Start a survey' to get started.",
        )
    else:
        res = get_recipe(message.from_user.id)
        rated_recipes_num = len(check_db_by_user(message.from_user.id, 'rates'))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("1","2","3","4","5")
        bot.send_message(message.chat.id, "Rate the dish from 1 to 5, how much you like it\n\n{}/10.\n".format(rated_recipes_num + 1) +
                                        res[1], reply_markup=markup)
        bot.send_photo(message.chat.id, res[2])
        bot.set_state(message.from_user.id, MyStates.survey_in_process, message.chat.id)

@bot.message_handler(state=MyStates.survey_in_process)
def continue_survey(message):
    variants = ['1','2','3','4','5']
    if message.text not in variants:
        bot.send_message(message.chat.id, "Write the number from 1 to 5.")
    else:
        last_recommended = get_recipe(message.from_user.id)[0]
        insert_to_db('rates', f'{message.from_user.id},{last_recommended},{message.text}')
        rated_recipes_num = len(check_db_by_user(message.from_user.id, 'rates'))
        if rated_recipes_num < 10:
            res = get_recipe(message.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("1","2","3","4","5")
            bot.send_message(message.chat.id, "Rate the dish from 1 to 5, how much you like it\n\n{}/10.\n".format(rated_recipes_num + 1) +
                                        res[1],  reply_markup=markup)
            bot.send_photo(message.chat.id, res[2])
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Give me a recommendation")
            bot.send_message(message.chat.id, "Thank you! Now I know what I can advise you :)",
                            reply_markup=markup)
            recommended = recommend.recommend(check_db_by_user(message.from_user.id, 'rates'))
            for i in recommended:
                print(i)
            print(check_db_by_user(message.from_user.id, 'rates'))
            bot.set_state(message.from_user.id, MyStates.get_recommendation, message.chat.id)

@bot.message_handler(state=MyStates.get_recommendation)
def give_recommendation(message):
    variants = ["Give me a recommendation", "Get a recommendation", "Next one"]
    if message.text not in variants:
        bot.send_message(message.chat.id, "Write 'Get a recommendation'.")
    else:
        bot.send_message(message.chat.id, "Wait a sec...")
        recommended = recommend.recommend(check_db_by_user(message.from_user.id, 'rates'))
        recommended_dishes = remove_duplicate_dishes(message.from_user.id, recommended)
        if len(recommended_dishes) == 0:
            bot.send_message(message.chat.id, "Sorry, we don't have any other recommendations for you.", reply_markup=types.ReplyKeyboardRemove())
            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Next one")
            bot.send_message(message.chat.id, "I suppose, you may like this:\n\n" + recommended_dishes[0][1], reply_markup=markup)
            bot.send_photo(message.chat.id, recommended_dishes[0][2])
            insert_to_db('recommendations', f'{message.from_user.id},{recommended_dishes[0][0]}')

@bot.message_handler(commands=["calories"])
def calories_enter(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Enter calories manually", "Find dish by name", "Find dish by photo", "Get left calories")
    bot.set_state(message.from_user.id, MyStates.calories, message.chat.id)
    bot.send_message(
        message.chat.id,
        f"You have 4 options to enter your calories.",
        reply_markup=markup
    )

def update_calories(user_id, eaten: int):
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()

    cursor.execute(
        f'''
        UPDATE calories
        SET eaten = {eaten}
        WHERE id = {user_id}
        '''
        )

    connection.commit()
    connection.close()


def get_calories(user_id):
    connection = sqlite3.connect('db/user.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT possible, eaten FROM calories WHERE id == {user_id}')
    records = cursor.fetchall()
    records = records[0] # we have only one possible outcome

    connection.commit()
    connection.close()
    return records


def tell_calories(chat_id, left_cal):
    if left_cal >= 0:
        bot.send_message(
            chat_id,
            f"Here are the calories that you can consume: {left_cal}."
        )
    else:
        bot.send_message(
            chat_id,
            f"Oh my, you overeat by: {-left_cal} calories!"
        )


@bot.message_handler(state=MyStates.enter_calories_manually)
def calories_manually(message):
    records = get_calories(message.from_user.id)

    new_eaten = int(message.text)
    left_cal = records[0] - (new_eaten + records[1])

    tell_calories(message.chat.id, left_cal)

    update_calories(message.from_user.id, new_eaten + records[1])
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(content_types=['photo'], state=MyStates.find_calories_by_photo)
def calories_by_photo(message):   
    fileID = message.photo[-1].file_id   
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    img_path = 'models_testing/food_img/image.jpg'
    
    with open(img_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    info = by_photo.nutritional_info(Path(img_path))
    name = info['foodName'][0]
    calories = int(info['nutritional_info']['calories'])
    

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Yes", "No")
    bot.send_message(
        message.chat.id,
        f"I guess your food is {name}.\nAnd it contains {calories} calories.\nWould you like me to count them to your eaten calories?",
        reply_markup=markup
    )

    bot.set_state(message.from_user.id, MyStates.calories_decision, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["cal"] = calories

@bot.message_handler(state=MyStates.calories_decision)
def calories_decision(message):
    lower_text = str.lower(message.text)
    variants = ["yes", "no"]
    if lower_text not in variants:
        bot.send_message(
            message.chat.id,
            f"Please, say yes or no, i don't get what you want."
        )
    else: 
        if lower_text == variants[1]:
            bot.send_message(
                message.chat.id,
                f"Ok, won't count them!",
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            bot.send_message(
                message.chat.id,
                f"Added them to my memorry!",
                reply_markup=types.ReplyKeyboardRemove()
            )
            records = get_calories(message.from_user.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                new_eaten = int(data["cal"])
                left_cal = records[0] - (new_eaten + records[1])

                tell_calories(message.chat.id, left_cal)
                update_calories(message.from_user.id, new_eaten + records[1])
        
        bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(content_types=['document'], state=MyStates.find_calories_by_photo)
def calories_by_photo(message):   
    bot.send_message(message.chat.id, "Sorry, I cannot recognize documents, only photos.")


@bot.message_handler(state=MyStates.find_calories_by_name, content_types=['text'])
def calories_by_name(message):
    message.text = str.lower(message.text)
    params = message.text.strip().split(" ")

    if (len(params) == 0 or len(params) > 2):
       bot.send_message(
            message.chat.id,
            f"Excuse me, but I've got {len(params)} words from you: {' '.join(params)}.\n" +
            "I wanted it to look like: 'apple large' or just 'apple'.\n" +
            "Try again!"
        )
    else:
        name = params[0]
        measure = params[1] if len(params) == 2 else ""

        result = by_name.search(name, measure)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Yes", "No")
        bot.send_message(
            message.chat.id,
            f"The {name} has {result['calories']} calories. Would you like me to add them to your eaten ones?",
            reply_markup=markup
        )
        bot.set_state(message.from_user.id, MyStates.calories_decision, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["cal"] = str(result['calories'])


@bot.message_handler(state=MyStates.calories)
def calories_left(message):
    variants = ["Enter calories manually", "Find dish by name", "Find dish by photo", "Get left calories"]
    if message.text not in variants:
        bot.send_message(
            message.chat.id,
            "Please choose one of the variants."
        )
    else:
        if message.text == variants[0]:
            bot.set_state(message.from_user.id, MyStates.enter_calories_manually, message.chat.id)
            bot.send_message(message.chat.id, "Enter calories you have already eaten.", reply_markup=types.ReplyKeyboardRemove())
        elif message.text == variants[1]:
            bot.set_state(message.from_user.id, MyStates.find_calories_by_name, message.chat.id)
            bot.send_message(message.chat.id, "Enter a name of your dish. If you want more precise results, after a name enter the measure: 'small', 'medium', 'large'.",reply_markup=types.ReplyKeyboardRemove())
        elif message.text == variants[2]:
            bot.set_state(message.from_user.id, MyStates.find_calories_by_photo, message.chat.id)
            bot.send_message(message.chat.id, "Send a photo of your dish through the camera or upload it from gallery\n\n" +
                                            "We recommend:\n- Take pictures from an eye-level perspective\n" +
                                            "- Center the food on the picture\n"+
                                            "- Upload squared images", reply_markup=types.ReplyKeyboardRemove())
        elif message.text == variants[3]:
            records = get_calories(message.from_user.id)
            tell_calories(message.from_user.id, records[0] - records[1])

@bot.message_handler(func=lambda message: True)
def send_confusion(message):
    bot.send_message(
            message.chat.id, 
            "Hmm. Sorry, but I don't understand you.\n" +
            "I understand certain commands.\n" +
            "You may see them in my menu.\n" + 
            "If you are new, I recommend you to /start our conversation :3"
            )

       
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.infinity_polling()