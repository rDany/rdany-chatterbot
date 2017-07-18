import time
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from corpus import rdany_corpus
from corpus import rdany_answers


from telegram import telegram


def get_mars_time():
    millis = time.time()
    JDut = (millis / (8.64 * 1.e4)) + 2440587.5
    JDtt = JDut + (37 + 32.184) / 86400
    J2000 = JDtt - 2451545
    MSD = (((J2000 - 4.5) / 1.027491252) + 44796 - 0.00096)
    return MSD

try:
    # Attempts to load Telegram configuration
    from config import Config
except:
    print ("Missing config.py, no Telegram support")

# Sends a message to Telegram
def send_to_telegram(chat_id, answer):
    msg = {
            'chat_id': chat_id,
            'parse_mode': 'Markdown',
            'text': answer,
        }
    r = telegram_conection.send_to_bot('sendMessage', data = msg)

chatterbot = ChatBot(
    "Training Example",
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch'
        },
        {
            'import_path': 'chatterbot.logic.LowConfidenceAdapter',
            'threshold': 0.65,
            'default_response': 'fallback.LOW_CONFDENCE'
        }
    ],)
chatterbot.set_trainer(ListTrainer)

corpus_list = []
for k in rdany_corpus:
    corpus_list.append(k)
    corpus_list.append(rdany_corpus[k])

chatterbot.train(corpus_list)

#print ()
#input_text = None
telegram_conection = telegram("eibriel_icecream_bot", Config.telegram_token, "8979")
while 1:
    #input_text = input("> ")

    telegram_conection.open_session()
    r = telegram_conection.get_update() # Listen for new messages
    if not r:
        continue # If no messages continue loop
    r_json = r.json()
    telegram_conection.close_session()
    for result in r_json["result"]:
        answer = ""
        if not ("message" in result and "text" in result["message"]):
            continue # Sanity check on the message

        chat_id = result["message"]["chat"]["id"] # Get user id
        input_text = result["message"]["text"] # Get input text
        print ()
        print (input_text)
        if input_text == "/start":
            answer = "greetings.START"
        else:
            answer = chatterbot.get_response(input_text)
        print (answer)

        if type(rdany_answers[answer]) == dict:
            if "first_time" in rdany_answers[answer]:
                answer_text = rdany_answers[answer]["first_time"]
            elif "recently" in rdany_answers[answer]:
                answer_text = rdany_answers[answer]["recently"]
            elif "else" in rdany_answers[answer]:
                answer_text = rdany_answers[answer]["else"]
            elif "action" in rdany_answers[answer]:
                answer_text = rdany_answers[answer]["text"].format(get_mars_time())
        elif type(rdany_answers[answer]) == list:
            answer_text = rdany_answers[answer][0]

        print (answer_text)
        send_to_telegram(chat_id, answer_text)
