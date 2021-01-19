import logging
import io
import urllib.parse
from pylatex import Document, Command,Math,Alignat,Package
from pylatex.utils import  NoEscape
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)


#The bot token
TOKEN = "Put Your Token Here"
doc = Document('basic',font_size ="Large")
doc.packages.add(Package("geometry",options=['a5paper',"centering"]))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


#The conversation handler needs to return integres
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
# the list inside list in the keyboard means we seprate the keyboard in row column form
reply_keyboard = [
    ['Math', 'Text'],
    ['Done'],
]
#the mark up attribuite we will set in our reply_text method
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,resize_keyboard = True)



def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Hi, this bot works as latex compiler.!\n\n How to use the bot?\n Just pick what will type and then send your text or math(in latex form).",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Type {text.lower()}: ')

    return TYPING_REPLY


def text_math_compiler(user_data):
    global doc
    equations = list()

    if (user_data['choice'] == "Math"):
        equations.append(user_data['Math'])
        for eq in equations:
            with doc.create(Alignat(numbering = True, escape = False)) as math_eq:
                math_eq.append(eq)
                equations.remove(eq)

    elif(user_data['choice'] == "Text"):
        doc.append(user_data['Text'])





def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    #this method job is to take a dic has choice and the choice value and add it to the doc
    text_math_compiler(user_data)
    del user_data['choice']
    update.message.reply_text(
        "what will you type now?",
        reply_markup=markup,
    )

    return CHOOSING



def done(update: Update, context: CallbackContext) -> int:
    global doc
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"Your file is uploading.."
    )
    user_data.clear()

    f = io.BytesIO()
    f.write(doc.dumps().encode())
    latex = f.getvalue()
    url_unicode = urllib.parse.quote(latex)
    url = "http://www.latexonline.cc/compile?text="+url_unicode


    try:

        context.bot.send_document(chat_id=update.effective_chat.id,document = url)
    except:

        update.message.reply_text(
            f"something wrong has happend!, make sure you have entered everything correctly!\n\n "
        )


    #Clear the document
    doc = Document('basic',font_size ="Large")
    doc.packages.add(Package("geometry",options=['a5paper',"centering"]))
    update.message.reply_text(
        f"Done, click /start to relunch the bot"
    )

    return ConversationHandler.END





def main() -> None:

    #The latex Document

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Math|Text)$'), regular_choice
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
