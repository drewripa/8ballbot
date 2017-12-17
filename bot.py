import telebot
import cherrypy
import config


from db.SQLighter import SQLighter

WEBHOOK_HOST = config.host
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './crt/webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './crt/webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

#Counter for wrong retries
RETRY_COUNTER = 0

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


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):

    dbconn = SQLighter()

    dbdata = dbconn.select_userdata(message.from_user.id)

    counter = dbdata[0][1]
    yes = dbdata[0][2]
    no = dbdata[0][3]
    mb = dbdata[0][4]

    if len(dbdata) == 0:
        dbconn.user_init(message.from_user.id)
    if message.text[-1] != '?':
        bot.send_message(message.chat.id, str(message.from_user.id))
        bot.send_message(message.chat.id, str(dbdata))
        bot.send_message(message.chat.id, counter)
    else:
        bot.reply_to(message, message.text)


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