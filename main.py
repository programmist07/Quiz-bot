from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import json

user_contact = None
user_answers = []  # To store answers for the user

file_path = "users.json"

questions = [
    {"savol": "O‘zbekiston poytaxti qaysi shahar?", "javoblar": ["Toshkent", "Samarkand", "Buxoro"], "to'g'ri": "Toshkent"},
    {"savol": "2 * 3 = ?", "javoblar": ["5", "6", "7"], "to'g'ri": "6"},
    {"savol": "Dunyo eng uzun daryosi?", "javoblar": ["Nayl", "Amazonka", "Yangtse"], "to'g'ri": "Amazonka"},
    {"savol": "Bir yil necha kun?", "javoblar": ["365", "366", "364"], "to'g'ri": "365"},
    {"savol": "Qaysi musiqa asbobi tarmoqlar bilan chaladi?", "javoblar": ["Gitara", "Pianino", "Truba"], "to'g'ri": "Gitara"},
    {"savol": "Eng baland tog‘", "javoblar": ["Everest", "Kilimanjaro", "Fuji"], "to'g'ri": "Everest"},
    {"savol": "Alisher Navoiy qaysi asarining muallifi?", "javoblar": ["Xamsa", "Firdavsiy", "Nizomiy"], "to'g'ri": "Xamsa"},
    {"savol": "Suvning kimyoviy formulasi?", "javoblar": ["H2O", "CO2", "NaCl"], "to'g'ri": "H2O"},
    {"savol": "O‘zbekistonda qaysi katta ko‘l mavjud?", "javoblar": ["Aral", "Issiqko‘l", "Chad"], "to'g'ri": "Issiqko‘l"},
    {"savol": "Qaysi sport turi eng ko‘p mashhurlikka ega?", "javoblar": ["Futbol", "Tennis", "Basketbol"], "to'g'ri": "Futbol"}
]

async def save_data(user, id, name, username, time, message):
    user_data = {
        "user_id": id,
        "name": name,
        "username": username,
        "time": time,
        "message": message
    }

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(user_data)

    with open(file_path, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [["Test", "Register"]]
    await update.message.reply_text(f"Hello {update.effective_user.first_name}, welcome to the quiz bot!",
                                    reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    phone_button = KeyboardButton("Send phone number", request_contact=True)  # Request contact
    phone_markup = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True)  # Show button for contact
    await update.message.reply_text(
        "Please send your phone number to start the test.", reply_markup=phone_markup
    )


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_contact
    user = update.effective_user
    id = user.id
    name = user.full_name
    username = user.username
    time = datetime.now().strftime("%c")

    # Check if contact is shared
    if not update.message.contact:
        await update.message.reply_text("You have to register first")
        return

    # If the message contains a contact, update user_contact
    user_contact = update.message.contact.phone_number  # Save the contact's phone number
    await update.message.reply_text(f"Phone number saved: {user_contact}")

    # Start the quiz after the contact is saved
    question_index = 0
    question = questions[question_index]
    options = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(option, callback_data=option) for option in question["javoblar"]]
    ])
    await update.message.reply_text(
        f"Savol {question_index + 1}: {question['savol']}",
        reply_markup=options
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    answer = query.data

    # Track the user's answers
    user_answers.append(answer)

    # Find the current question index
    question_index = len(user_answers) - 1
    if question_index < len(questions):
        question = questions[question_index]
        if answer == question["to'g'ri"]:
            # You can handle scoring here
            pass

        # Move to the next question
        if question_index + 1 < len(questions):
            next_question = questions[question_index + 1]
            options = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(option, callback_data=option) for option in next_question["javoblar"]]
            ])
            await query.message.edit_text(
                f"Savol {question_index + 2}: {next_question['savol']}",
                reply_markup=options
            )
        else:
            score = sum([1 for idx, answer in enumerate(user_answers) if answer == questions[idx]["to'g'ri"]])
            await query.message.reply_text(f"Test finished! Your score: {score} out of {len(questions)}")
    await query.answer()


try:
    app = ApplicationBuilder().token("7919964160:AAFI8YNzl7AIQs19rsaE8Qtevuxg3njyjDs").build()
except Exception as e:
    print("Error", e)
else:
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("Register"), register))
    app.add_handler(MessageHandler(filters.Regex("Test"), start_test))
    app.add_handler(MessageHandler(filters.CONTACT, start_test))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.run_polling()
