#!/usr/bin/env python3

import logging
import spacy
import sys
import random
import python-telegram-bot

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

# Define states for conversation
ADD_INFO, ASK_EXTRAS, GET_EXTRAS, CHANGE_ORDER, COMPLAINT, SUGGESTION, ORDER = range(7)

# Response variations
greetings_responses = [
    "Hi there! I am Berta, and I will assist you in ordering coffee today.",
    "Hello! Berta here, ready to help you order some coffee! What would you like?",
    "Hey there! Let's get you some delicious coffee. How can I assist you?",
    "Hello there, my name is Berta, and I will help you to order coffee. What would you have me get for you?",
    "Hi, I'm Berta, nice to meet you. What coffee would you like to order?"
]

manager_contact_responses = [
    "If you need to get in touch with the shop's manager, you can contact this number: +27 345 6789.\n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "You can contact the shop's manager via email at manager@thecoffeeshop.co.za . \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "To speak with the manager, please visit us at the coffee shop or call +27 345 6789. \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "The manager is available at this number: +27 345 6789. Feel free to reach out! \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "For manager inquiries, you can email manager@thecoffeeshop.co.za or contact +27 345 6789. \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "The contact details for the shop's manager is as follows:\nemail: manager@thecoffeeshop.co.za\nphone: +27 345 6789 \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat."
]

website_app_responses = [
    "Currently, we do not have a website or app yet. We have started working on a website, so stay tuned for updates! \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "We don't have a website or app just yet, but we're working on it. \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "At the moment, we don't have a website or app. Hopefully soon! \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "Sorry, we don't have a website or app available yet. We'll keep you posted \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.!"
]

shop_hours_response = [
    "We are open Monday to Friday from 7:00 AM to 6:00 PM, and Saturday from 8:00 AM to 4:00 PM. We are closed on Sundays, as well as on Christmas. \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat.",
    "Our operating hours are Monday to Friday, 7:00 AM - 6:00 PM, and Saturday from 8:00 AM - 4:00 PM. We are closed on Sundays, as well as on Christmas. \n\nPlease tell me what you would like to order, or type '\cancel' if you would like to end this chat."
]

order_completion_responses = [
    "I have placed your order. I hope that you have a wonderful day further!",
    "Your order is confirmed! Enjoy your coffee and have a great day!",
    "All set! Your coffee order is placed. Have an awesome day!",
    "The coffee order is at the barista. It will take a few minutes to complete!",
    "Extra delicious coffee in the making! Hope to see you again soon.",
    "ALAKAZAM! Caffeine being blended... Masterpiece being created! Have an AWESOME day!",
    "BOOM SHAKALAKA! I hope your day is as fantastic as your order!"
]

suggestion_responses = [
    "Thank you for your suggestion! Could you please provide more details or elaborate on your idea?",
    "I appreciate your suggestion! Can you please tell me more about it?",
    "Thanks for the suggestion! Could you please share a bit more about what you're thinking?",
    "Thank you for the idea. Hmmmm, I wonder... Could you please elaborate a bit?",
    "Ahhhh, what an interesting idea! Please do explain a bit more in detail!",
    "I appreciate the suggestion, it intrigues me... Could you maybe please share your thoughts?"
]

complaint_responses = [
    "I'm sorry to hear that you're not satisfied. Can you please describe the issue further?",
    "I apologize for any inconvenience. Could you tell me more about the issue?",
    "We're sorry for the trouble. Can you explain the problem so we can assist you better?",
    "I am sorry to hear about this. Please explain a bit more so that I can better understand.",
    "I am so so sorry! Please tell me more about the issue."
]

suggestion_acknowledgment_responses = [
    "Thank you for your suggestion! We really appreciate your feedback.",
    "Thanks for sharing your suggestion! Your input means a lot to us.",
    "We value your suggestion! Thanks for letting us know.",
    "Thank you for the interesting suggestion! We will definitely have a look at it.",
    "Thanks for bringing this suggestion to us, we will bring it under the manager's attention as soon as possible."
]

complaint_acknowledgment_responses = [
    "Thank you for sharing your feedback. We will work to resolve this issue.",
    "We appreciate your feedback. Our team will look into it.",
    "Thanks for letting us know. We're committed to resolving the issue.",
    "Thank you for bringing this under our attention. We will see if we can find a proper solution.",
    "Thank you for your feedback. We will tackle the issue ASAP!",
    "The complaint has been logged and filed. It will be handled within the next 1 to 5 work days."
]

change_order_responses = [
    "What would you like to change? Type 'coffee' to change the coffee type, 'extras' to change extras, or 'size' to change the size.",
    "How would you like to modify your order? Please specify if it's the coffee, extras, or size.",
    "Please tell me what you'd like to change: 'coffee', 'size', or 'extras'?"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(greetings_responses))
    return ORDER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thank you, I hope you have a fabulous day further.\n\nSee you next time!")
    await update.message.reply_text("Please enter /start if you are ready to place another order of delicious coffee.")
    return ConversationHandler.END

def extract_intent(doc):
    verb = ""
    dobj = ""
    for token in doc:
        if token.dep_ == "dobj":
            verb = token.head.lemma_
            dobj = token.text.lower()
    
    verb_list = ["order", "want", "get", "have", "take", "buy"]
    dobj_list = ["coffee", "caffeine", "espresso", "latte", "cappuccino", "mocha", "americano", "flat white", "caffe macchiato", "cortado", "iced coffee", "decaf", "iced latte", "black", "doppio", "red eye", "galao", "lungo", "macchiato", "ristretto", "affogato", "cafe au lait", "irish"]
    
    if verb in verb_list and dobj in dobj_list:
        return verb + dobj.capitalize()
    return None

def detect_website_or_app(msg):
    website_app_keywords = ["website", "web", "site", "app", "application", "mobile app", "online"]
    if any(keyword in msg.lower() for keyword in website_app_keywords):
        return True
    return False

def detect_hours_or_days(msg):
    hours_days_keywords = ["hours", "open", "closing", "opening", "operating hours", "days", "when are you open", "open today"]
    if any(keyword in msg.lower() for keyword in hours_days_keywords):
        return True
    return False

def detect_complaint(msg):
    complaint_keywords = ["bad", "dislike", "problem", "not happy", "unhappy", "hate", "wrong", "complain", "issue", "terrible"]
    if any(keyword in msg.lower() for keyword in complaint_keywords):
        return True
    return False

def detect_suggestion(msg):
    suggestion_keywords = ["suggest", "recommend", "should", "could be better", "better if", "I think", "would prefer", "how about"]
    if any(keyword in msg.lower() for keyword in suggestion_keywords):
        return True
    return False

def detect_manager_inquiry(msg):
    manager_keywords = ["manager", "owner", "contact", "speak to", "talk to", "reach", "supervisor"]
    if any(keyword in msg.lower() for keyword in manager_keywords):
        return True
    return False

async def intent_ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    doc = nlp(msg)
    
    if detect_manager_inquiry(msg):
        await update.message.reply_text(random.choice(manager_contact_responses))
        return ORDER
    
    if detect_website_or_app(msg):
        await update.message.reply_text(random.choice(website_app_responses))
        return ORDER
    
    if detect_hours_or_days(msg):
        await update.message.reply_text(random.choice(shop_hours_response))
        return ORDER

    if detect_suggestion(msg):
        await update.message.reply_text(random.choice(suggestion_responses))
        return SUGGESTION

    if detect_complaint(msg):
        await update.message.reply_text(random.choice(complaint_responses))
        return COMPLAINT

    if "change order" in msg or "modify order" in msg:
        await update.message.reply_text(random.choice(change_order_responses))
        return CHANGE_ORDER

    intent = extract_intent(doc)
    if intent:
        context.user_data["product"] = "coffee"
        await update.message.reply_text("I require additional information to place the order. What type of coffee would you like to order? Would you like extras?")
        return ASK_EXTRAS
    else:
        await update.message.reply_text("I do not understand your intent. Would you please rephrase your request?")
        return ORDER

async def ask_extras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    doc = nlp(msg)

    coffee_type = None
    size = None

    for token in doc:
        if token.dep_ == "dobj" or token.dep_ == "pobj":
            coffee_type = token.text
        elif token.dep_ == "amod" or token.dep_ == "compound" or token.dep_ == "det":
            if coffee_type:
                coffee_type = token.text + " " + coffee_type
            else:
                coffee_type = token.text
        elif token.dep_ == "nummod":
            size = token.text

    if coffee_type:
        context.user_data["type"] = coffee_type
        context.user_data["size"] = size if size else "regular"
        
        await update.message.reply_text("Please specify your preferred extras with your coffee, for example milk, sugar, sweetener, soya milk, almond milk, goat milk.)")
        return GET_EXTRAS
    
    await update.message.reply_text("I can't extract the needed information. Please try again!")
    return ASK_EXTRAS

async def get_extras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()
    
    if msg in ["no", "none", "no thanks", "nope", "no thank you"]:
        context.user_data["extras"] = "no extras"
    else:
        context.user_data["extras"] = msg
    
    user_data = context.user_data
    await update.message.reply_text(random.choice(order_completion_responses).format(details_to_str(user_data)))
    await update.message.reply_text("Please type /start to make another order!")
    return ConversationHandler.END

async def handle_complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text(random.choice(complaint_acknowledgment_responses))
    await update.message.reply_text("If you would like to continue with your order, please type /start to begin again.")
    return ConversationHandler.END

async def handle_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text(random.choice(suggestion_acknowledgment_responses))
    await update.message.reply_text("If you would like to continue with your order, please type /start to begin again.")
    return ConversationHandler.END

async def change_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    if "coffee" in msg:
        await update.message.reply_text("What type of coffee would you like to change to?")
        return ASK_EXTRAS
    elif "size" in msg:
        await update.message.reply_text("What size would you like to change your order to?")
        return ASK_EXTRAS
    elif "extras" in msg:
        await update.message.reply_text("What extras would you like to change?")
        return GET_EXTRAS
    else:
        await update.message.reply_text(random.choice(change_order_responses))
        return CHANGE_ORDER

def details_to_str(user_data):
    details = list()
    for key, value in user_data.items():
        details.append("{} - {}".format(key, value))
    return "\n".join(details).join(["\n", "\n"])

def main():
    application = Application.builder().token("TOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, intent_ext)],
            ASK_EXTRAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_extras)],
            GET_EXTRAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extras)],
            CHANGE_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_order)],
            COMPLAINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_complaint)],
            SUGGESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_suggestion)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
