import telebot
from yahoo_fin import stock_info as si
from datetime import datetime, timedelta
import mplfinance as mplf

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
        '/price {symbol} - Live price of ticker.\n'\
        '/full {symbol} - More information about ticker.\n\n'\
        'Above functions accept 1 or many symbols, use a comma to separate them\n'\
        '/price orcl OR /price amzn,orcl\n\n'\
        'To get a chart use: \n'\
        '/chart {symbol}-{period}\n'\
        'The options available for period are : \n'\
        '1w = 1 week\n'\
        '1m = 1 month\n'\
        '3m = 3 months\n'\
        '6m = 6 months\n'\
        '1y = 1 year\n'
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

@bot.message_handler(commands=['chart'])
def get_stock_chart(message):
    options = message.text[7:].split('-')
    stock = options[0]
    period = options[1]
    timeperiod = {'1w':7,'1m':30,'3m':90,'6m':182, '1y':365}
    reply = ""
    try:
        today = datetime.now()
        start_time = today -timedelta(days=timeperiod[period])
        data = si.get_data(stock, start_time.strftime('%Y-%m-%d'))
        graph_name = f'/tmp/chart-{today.strftime("%Y-%m-%d-%s")}.png'
        mplf.plot(data, type="line", volume=True, style="mike", datetime_format='%d %b %Y',
                    figratio=(20,10), tight_layout=True,
                    title="\n{} {}".format(stock, period),
                    savefig=dict(fname=graph_name, dpi=95))
        photo = open(graph_name, 'rb')
        bot.send_photo(message.chat.id, photo)
    except AssertionError as e:
        reply +=f"{stock.strip()} symbol do not exist. \n"
        bot.send_message(message.chat.id, reply)
    except:
        reply +=f"Please check /help to interact correctly with the bot\n"
        bot.send_message(message.chat.id, reply)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def message(message):
    bot.send_message(message.chat.id, "Refer to /help to know how to interact with me")


bot.polling()

