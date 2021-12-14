import telebot
from yahoo_fin import stock_info as si

with open("token") as f:
    firstline = f.readline().rstrip()
API_TOKEN = firstline

bot = telebot.TeleBot(API_TOKEN)

def get_symbols(message, type):
        char_list ={ 'full': 6, 'price':7}
        try:
            list_symbols = {}
            tickers = (message[char_list[type]:])
            if (len(tickers) > 2):
                list_symbols = message[char_list[type]:].split(',')
        except:
            print('iUJIJUI')
            return None
        else:
            if list_symbols:
                return list_symbols
            else:
                return None

# Handle '/start' 
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """/help to see what I'm capable of.""")

# Handle '/help'
@bot.message_handler(commands=['help'])
def help(message):
    reply = 'You can control me by sending these commands: \n'\
        '/price - Live price of ticker.\n'\
        '/full - More information about ticker.\n'
    bot.send_message(message.chat.id, reply)

# Handle '/full'
@bot.message_handler(commands=['full'])
def get_full_info(message):
    stocks_name = get_symbols(message.text, 'full')
    if stocks_name == None :
        bot.send_message(message.chat.id, "Please define a symbol to retrieve the information requested")
    else:
        for stock in stocks_name:
            reply = ""
            try:
                stock_price = si.get_quote_table(stock.strip())
                stock_price['DayRange'] = stock_price["Day's Range"]
            except AssertionError as e:
                reply +=f"{stock.strip()} symbol do not exist. \n"
            except:
                reply +=f"{stock.strip()} symbol do not have current information. \n"
            else:
                reply +=  f"{stock.strip()} price share is at ${stock_price['Quote Price']:.2f} \n"\
                    f"Day's Range: ${stock_price['DayRange']}\n"\
                    f"Previous Close: ${stock_price['Quote Price']:.2f}\n"\
                    f"Open: ${stock_price['Open']:.2f}\n"\
                    f"52 Week Range: ${stock_price['52 Week Range']}" 
                
            if len(reply) > 0: 
                bot.send_message(message.chat.id, reply)   

# Handle '/price'
@bot.message_handler(commands=['price'])
def get_stock_price(message):
    stocks_name = get_symbols(message.text, 'price')
    reply = ""
    if stocks_name == None :
        bot.send_message(message.chat.id, "Please define a symbol to retrieve the information requested")
    else:
        for stock in stocks_name:
            try:
                stock_price = si.get_live_price(stock.strip())
            except AssertionError as e:
                reply +=f"{stock.strip()} symbol do not exist. \n"
            except:
                reply +=f"{stock.strip()} symbol do not have current information. \n"
            else:
                reply +=  f"{stock.strip()} price share is at ${stock_price:.2f} \n"

        if len(reply) > 0: 
            bot.send_message(message.chat.id, reply)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def message(message):
    bot.send_message(message.chat.id, "Refer to /help to know how to interact with me")


bot.polling()

