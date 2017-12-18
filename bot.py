import telebot
import cherrypy
import config
import random

from db.SQLighter import SQLighter

WEBHOOK_HOST = config.host
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './crt/webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './crt/webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

decisions = [ "It is certain", "It is decidedly so",
                  "Without a doubt", "Yes definitely",
                  "You may rely on it", "As I see it, yes",
                  "Most likely", "Outlook good",
                  "Yes", "Signs point to yes",
                  "Reply hazy try again", "Ask again later",
                  "Better not tell you now", "Cannot predict now",
                  "Concentrate and ask again", "Don\'t count on it",
                  "My reply is no", "My sources say no",
                  "Outlook not so good", "Very doubtful" ]

#If user do not understand hints for several times just repeat them for a few times
def hints(counter, message):
    whydoespythonhavenoswitchcase = {
        0: "Hold on, Tiger. You need to ask a question first.",
        1: "Ok, I've got it. You are persistent. Try again.",
        2: "We can play it all day. Be sure.",
        3: "If you want you could ask me to do this work for you.",
        4: "Last warning. No jokes.",
        5: str(message.text) + ("?\nSee? So simple. Just '?' at the end.\nYou are welcome")
    }
    counter += 1
    return counter, whydoespythonhavenoswitchcase.get(counter-1)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

@bot.message_handler(commands=['stats'])
def stats_message(message):
    dbconn = SQLighter()
    dbdata = dbconn.select_userdata(message.from_user.id)

    if len(dbdata) == 0:
        dbconn.user_init(message.from_user.id)
        dbdata = dbconn.select_userdata(message.from_user.id)

    yes = dbdata[0][2]
    no = dbdata[0][3]
    mb = dbdata[0][4]

    bot.send_message(message.chat.id,
                     "Statistic:\n'Yes' %s times\n'No' %s times\n'Maybe' %s times " % (yes, no, mb))

    dbconn.close()



@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    dbconn = SQLighter()
    dbdata = dbconn.select_userdata(message.from_user.id)

    if len(dbdata) == 0:
        dbconn.user_init(message.from_user.id)
        dbdata = dbconn.select_userdata(message.from_user.id)

    counter = dbdata[0][1]
    yes = dbdata[0][2]
    no = dbdata[0][3]
    mb = dbdata[0][4]

    if message.text[-1] != '?' and counter < 6:
        bot.send_message(message.chat.id, hints(counter, message)[1])
        dbconn.write_userdata(message.from_user.id, hints(counter, message)[0], yes, no, mb)
    else:
        magic = random.randint(0,19)
        bot.send_message(message.chat.id, magic)
        bot.send_message(message.chat.id, decisions[magic])
        if magic < 10:
            yes+=1
        elif magic < 15:
            mb+=1
        else:
            no+=1
        dbconn.write_userdata(message.from_user.id, 0, yes, no, mb)

    dbconn.close()


bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

if __name__ == '__main__':
    bot.polling(none_stop=True)