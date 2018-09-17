import gevent.monkey
gevent.monkey.patch_all()  # noqa

import logging
logging.basicConfig(level=logging.INFO)  # noqa

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import MessageEntity

from models import get_session, URLShare
from config import config


AUTHORS_FILTER = Filters.user(username="@jiajunhuang")


def report_error(func):
    def wrapper(bot, update, *args, **kwargs):
        try:
            return func(bot, update, *args, **kwargs)
        except Exception as e:
            logging.exception("failed to handle message from telegram")
            bot.send_message(chat_id=update.message.chat_id, text="出错啦：" + str(e))
    return wrapper


def save_url(url):
    with get_session() as s:
        url_share = URLShare(url=url)
        s.add(url_share)
        s.flush()
        return url_share.id


def save_comment(comment):
    with get_session() as s:
        share = s.query(URLShare).order_by(URLShare.id.desc()).first()
        if share:
            share.comment = comment
            s.add(share)
            return comment + ": https://share.jiajunhuang.com?jump=" + share.url

        return "not found"


def update_comment(share_id, comment):
    with get_session() as s:
        share = s.query(URLShare).filter(URLShare.id == share_id).first()
        if share:
            share.comment = comment
            s.add(share)
            return "mapped with url: " + share.url

        return "not found"


@report_error
def comment_handler(bot, update, args):
    if len(args) == 0:
        text = "Usage: /comment <your comments>"
        bot.send_message(chat_id=update.message.chat_id, text=text)
    else:
        text = save_comment(" ".join(args))
        bot.send_message(chat_id="@jiajunhuangcom", text=text)  # send to channel


@report_error
def update_comment_handler(bot, update, args):
    if len(args) == 0:
        text = "Usage: /update <id> <new comments>"
    else:
        text = update_comment(int(args[0]), "".join(args[1:]))

    bot.send_message(chat_id=update.message.chat_id, text=text)


@report_error
def url_share_handler(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="save with id: {}".format(save_url(update.message.text)))


if __name__ == "__main__":
    updater = Updater(token=config.TGBOTTOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CommandHandler(
            'comment', comment_handler, pass_args=True, filters=AUTHORS_FILTER,
        )
    )
    dispatcher.add_handler(
        CommandHandler(
            'update', update_comment_handler, pass_args=True, filters=AUTHORS_FILTER,
        ),
    )
    dispatcher.add_handler(MessageHandler(
        Filters.text & (
            Filters.entity(MessageEntity.URL) | Filters.entity(MessageEntity.TEXT_LINK)
        ) & AUTHORS_FILTER,
        url_share_handler,
    ))
    updater.start_polling()
