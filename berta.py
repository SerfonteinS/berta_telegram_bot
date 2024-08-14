#!/usr/bin/env python3

import logging
import spacy
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

nlp = spacy.load("en_core_web_sm")

ADD_INFO, ORDER = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there! I am Berta, and today I will assist you in ordering coffee.")
    return ORDER
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thank you, I hope you have a fabulous day further. \n\nSee you next time!")
    await update.message.reply_text("Please enter \start if you are ready to place another order of delicious coffee.")
    return ConversationHandler.END
    
def extract_intent(doc):
    verb = ""
    dobj = ""
    for token in doc:
        print(f"Token: {token.text}, Dependency: {token.dep_}, Head: {token.head.text}")
        if token.dep_ == "dobj":
            verb = token.head.text
            dobj = token.text
            #break
    print(f"Extracted verb: {verb}, Extracted dobj: {dobj}")
    if verb and dobj:    
        verbList = ["order", "want", "get"]
        dobjList = ["coffee", "caffeine"]
        if verb in verbList and dobj in dobjList:
            intent = verb + dobj.capitalize()
            return intent
    #return None
        
async def intent_ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    doc = nlp(msg)
    
    intent = extract_intent(doc)
    print(f"Extracted intent: {intent}")
    
    if intent == "orderCoffee":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee would you like to order?")
        return ADD_INFO
    elif intent == "wantCoffee":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee do you want?")
        return ADD_INFO
    elif intent == "getCoffee":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee would you like to get?")
        return ADD_INFO
    elif intent == "orderCaffeine":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee would you like to order?")
        return ADD_INFO
    elif intent == "wantCaffeine":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee do you want?")
        return ADD_INFO
    elif intent == "getCaffeine":
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee would you like to get?")
        return ADD_INFO
    else:
        await update.message.reply_text("I do not understand your intent. Would you please rephrase your request?")
        return ORDER
        
def details_to_str(user_data):
    details = list()
    for key, value in user_data.items():
        details.append("{} - {}".format(key, value))
    return "\n".join(details).join(["\n", "\n"])            
        
async def add_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    doc = nlp(msg)
    
    print("Message: ",msg)
    
    for token in doc:
        print(f"Token: {token.text}, Dependency: {token.dep_}")
        if token.dep_ == "dobj":
            dobj = token
            for child in dobj.lefts:
                print(f"Child: {child.text}, Dependency: {child.dep_}")
                if child.dep_ == "amod" or child.dep_ == "compound" or child.dep_ == "det":
                    context.user_data["type"] = child.text + " " + token.text
                    user_data = context.user_data
                    await update.message.reply_text("I have placed your order."
                                              "{}"
                                              "I hope that you have a wonderful day further!".format(details_to_str(user_data)))
                    await update.message.reply_text("Please type /start to make another order!")
                    return ConversationHandler.END
    await update.message.reply_text("I can't extract the needed information. Please try again!")
    return ADD_INFO                        
    
def main():
    application = Application.builder().token("TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=
        {
            ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, intent_ext)],
            ADD_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_info)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)                              

if __name__ == '__main__':
    main()

