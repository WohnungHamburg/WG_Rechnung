import logging
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update
from decouple import config

BOT_KEY = config('BOT_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

registry = {}
spent: dict[int, dict[str, list[float]]] = {}
env_list = ['all', 'old', 'food']


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def set_name(update: Update, context: CallbackContext) -> None:
    new_name = ' '.join(context.args)
    chat_id = update.message.chat_id
    registry[chat_id] = new_name
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Hi ' + new_name)


def register_new_spending(update: Update, context: CallbackContext) -> None:
    args = context.args
    spending = args[0]
    env = args[1]
    chat_id = update.effective_chat.id
    if not env in env_list:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Could not find env ' + env + '. Allowed are: ' + ', '.join(env_list))
        return
    if not chat_id in spent:
        spent[chat_id] = {}
    if not env in spent[chat_id]:
        spent[chat_id][env] = []
    spent[chat_id][env].append(spending)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Registered Spending of ' + spending + '€ for ' + env)


def get_spending(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    for chat_id in spent:
        name = registry[chat_id]
        context.bot.send_message(
            chat_id=chat_id, text="Spending for " + name + ':')
        for env in spent[chat_id]:
            context.bot.send_message(
                chat_id, '  spending in ' + env + ": " + ', '.join(spent[chat_id][env]))


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        BOT_KEY, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('name', set_name))
    updater.dispatcher.add_handler(
        CommandHandler('spent', register_new_spending))
    updater.dispatcher.add_handler(CommandHandler('list', get_spending))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
