from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalhttp import HttpError
from paypalcheckoutsdk.orders import OrdersCaptureRequest

import telebot
import time
import pytz
from datetime import datetime

# PayPal
client_id = "AYYkmeOvofEcCoER09L0Hp4BGbpXMuzedKDWmGWGqBVH9a1ESfWM9azyyY_VzaJ2qLRHDUXqcKj4Yq_q"
client_secret = "EOASjJVj9yWDFnp1cz63H21jn2mNSiJ4H5PZ3TWi3_4iO9IPP4A8GJqVo6VrQ7RElC0x7nLDnsOoE406"
# Creating an environment
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)
request = OrdersCreateRequest()

request.prefer('return=representation')
# Programme
bot = telebot.TeleBot('1367755612:AAG0dTVeXJYEyAEDbDJAnHQdKzA1cJQNl10')
tz = pytz.timezone('UTC')
current_datetime = datetime.now(tz)
lis = []

low1 = {'BTC': 0.02,
        'BCH': 0.5,
        'ETH': 0.3,
        'LTC': 2,
        'XRP': 280,
        'XLM': 1250}

course = {'BTC': 11300,
          'BCH': 236.07,
          'ETH': 450.00,
          'LTC': 51.02,
          'XRP': 0.40,
          'XLM': 0.080}

adress = {'BTC': 'bc1qkhxy58fr9etgetpf2fq8m3uase9xax3h463eq8',
          'BCH': 'qptgykzy4ssjsfw4zyxtlcx2gcwrnkxt3qaqlgqkkg',
          'ETH': '0x904a5EC1BDBa1E25416C7d8C84f814b4E20C387f',
          'LTC': 'LN7dfDEs6S9YXrMTFKLiRbNJ9VZZb3teis',
          'XRP': 'rNmYEtwGwZK4D7kvdfVVu7S15Dj84vSf36',
          'XLM': 'GCRSWSRYBGEZ6HD7WB42TLCTIDZM3ALVWSBXSYUQLS5QIVGOPTZ6IOLA'}


@bot.message_handler(commands=['start'])
def start_chat(message):
    print(message)
    bot.send_message(message.chat.id, 'Hello, {}, lets start!'.format(message.from_user.first_name))
    keyboard_lang = telebot.types.InlineKeyboardMarkup()
    keyboard_lang.row(
        telebot.types.InlineKeyboardButton('ENG', callback_data='lang-ENG'),
        telebot.types.InlineKeyboardButton('ESP', callback_data='lang-ESP')
    )
    bot.send_message(message.chat.id, 'Choose your language:', reply_markup=keyboard_lang)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
    data = query.data
    if data.startswith('lang-'):
        get_ex_lang_callback(query)
    elif data.startswith('menu-'):
        get_ex_menu_callback(query)
    elif data.startswith('sell-') or data.startswith('buy-'):
        get_ex_buy_sell_callback(query)
    elif data.startswith('pp-') or data.startswith('vm-'):
        get_ex_sell2_callback(query)
    elif data.startswith('sys-'):
        get_ex_sys_callback(query)


def get_ex_lang_callback(query):
    bot.answer_callback_query(query.id)
    main_menu(query.message)  # query.data[5:]


@bot.message_handler(content_types=['text'])
def get_ex_menu_callback(message):
    if message.text == 'Sell Crypto':
        buy_sell_crypto(message, 'sell')
    elif message.text == 'Buy Crypto':
        buy_sell_crypto(message, 'buy')
    elif message.text == 'My orders':
        check_order(message)
    elif message.text == 'Referral bonuses':
        bonuses(message)
    elif message.text == 'Contact us':
        help_bot(message)


def get_ex_sys_callback(query):
    bot.answer_callback_query(query.id)
    if query.data[4:] == 'cncl':
        bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
        main_menu(query.message)
    elif query.data[4:9] == 'cnfrm':
        if query.data[10:14] == 'sell':
            lis.append([str(query.message.chat.id) + '_' + str(query.message.message_id), False])
            created_form_sell(query.message, query.data[15:18], query.data[18:])
        else:
            created_form_buy(query.message, query.data[15:18], query.data[18:])
    elif query.data[4:7] == 'chk':
        check_order(query.message)
    elif query.data[4:] == 'with':
        withdraw(query.message)


def get_ex_buy_sell_callback(query):
    bot.answer_callback_query(query.id)
    if query.data.startswith('sell-'):
        buy_sell_crypto_2(query.message, query.data[5:], 'sell')
    elif query.data.startswith('buy-'):
        buy_sell_crypto_2(query.message, query.data[4:], 'buy')


def get_ex_sell2_callback(query):
    bot.answer_callback_query(query.id)
    if query.data[11:] == 'sell':
        buy_sell_crypto_3(query.message, query.data[7:10], query.data[3:6], query.data[11:])
    if query.data[11:] == 'buy':
        buy_sell_crypto_3(query.message, query.data[3:6], query.data[7:10], query.data[11:])


@bot.message_handler(commands=['menu'])
def main_menu(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    keyboard_lang = telebot.types.ReplyKeyboardMarkup(True)
    keyboard_lang.add(telebot.types.KeyboardButton('Sell Crypto'),
                      telebot.types.KeyboardButton('Buy Crypto'))
    keyboard_lang.add(telebot.types.KeyboardButton('My orders'),
                      telebot.types.KeyboardButton('Referral bonuses'))
    keyboard_lang.add(telebot.types.KeyboardButton('Contact us'))
    bot.send_message(message.chat.id, "Main menu:", reply_markup=keyboard_lang)


def withdraw(message):
    bot.send_message(message.chat.id, 'Minimum amount for withdrawal $50')


@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.chat.id, "If you have any issues, please let us know @help_bitcashbox")


@bot.message_handler(commands=['bonus'])
def bonuses(message):
    keyboard_bon = telebot.types.InlineKeyboardMarkup()
    keyboard_bon.row(telebot.types.InlineKeyboardButton('Withdraw', callback_data='sys-with'))
    bot.send_message(message.chat.id, 'You have 0 referrals\n'
                                      'You earned from referrals: $0\n'
                                      'Every time your referral makes successful exchange, you get up to 30%\n'
                                      'Your referral link: *потом дадим* t.me////////', reply_markup=keyboard_bon)


def buy_sell_crypto(message, buy_sell):
    keyboard_s_cr = telebot.types.InlineKeyboardMarkup()
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Ethereum(ETH)', callback_data=buy_sell + '-ETH'))
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Litecoin(LTC)', callback_data=buy_sell + '-LTC'))
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Bitcoin(BTC)', callback_data=buy_sell + '-BTC'))
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Bitcoin Cash(BCH)', callback_data=buy_sell + '-BCH'))
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Ripple(XRP)', callback_data=buy_sell + '-XRP'))
    keyboard_s_cr.row(telebot.types.InlineKeyboardButton('Stellar(XLM)', callback_data=buy_sell + '-XLM'))
    bot.send_message(message.chat.id, "Choose the currency you want to {}:".format(buy_sell),
                     reply_markup=keyboard_s_cr)


def created_form_sell(message, currency, amount):
    order_id = str(message.chat.id) + '_' + str(message.message_id)
    lis.append(order_id)
    keyboard_o_s = telebot.types.InlineKeyboardMarkup()
    keyboard_o_s.row(telebot.types.InlineKeyboardButton('Check orders statuses', callback_data='sys-chk'))
    bot.send_message(message.chat.id,
                     "To complete your order, transfer \n{0} {1}\nto the exchanger address:\n"
                     "{3}\n"
                     "\n"
                     "In the memo field enter your order ID\n"
                     "Your order ID is {2}\n"
                     "Your order would be proceeded automatically up to 15 minutes due to a high demand.\n"
                     "Created = {4}.{5}.{6} at {7}:{8} (Current UTC)".format(amount, currency, order_id,
                                                                             adress[currency],
                                                                             current_datetime.month,
                                                                             current_datetime.day,
                                                                             current_datetime.year,
                                                                             current_datetime.hour,
                                                                             current_datetime.minute),
                     reply_markup=keyboard_o_s)


def created_form_buy(message, currency, amount):
    bot.send_chat_action(message.chat.id, 'typing')
    # -------------------Making Order---------------------------------------------------------------------
    request.request_body(
        {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": amount
                    }
                }
            ]
        }
    )
    try:
        response = client.execute(request)
        print(response.result)
        keyboard_o_s = telebot.types.InlineKeyboardMarkup()
        keyboard_o_s.row(telebot.types.InlineKeyboardButton('Check orders statuses', callback_data='sys-chk'))
        approving_link = [link.href for link in response.result.links if link.rel == 'approve'][0]
        bot.send_message(message.chat.id,
                         "To complete your order, transfer \n{0} {1}\nto the exchanger address:\n"
                         "{3}"
                         "In the memo field enter your order ID\n"
                         "Your order ID is {2}\n"
                         "Your order would be proceeded automatically up "
                         "to 15 minutes due to a high demand.\n"
                         "Created = {4}.{5}.{6} at {7}:{8} (Current UTC)".format(amount, currency, response.result.id,
                                                                                 approving_link,
                                                                                 current_datetime.month,
                                                                                 current_datetime.day,
                                                                                 current_datetime.year,
                                                                                 current_datetime.hour,
                                                                                 current_datetime.minute),
                         reply_markup=keyboard_o_s)
    except IOError as ioe:
        if isinstance(ioe, HttpError):
            pass
    # ----------------------------------------------------------------------------------------


def buy_sell_crypto_2(message, ex_code, buy_sell):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'You {0}: {1}'.format(buy_sell, ex_code))
    keyboard_s2_cr = telebot.types.InlineKeyboardMarkup()
    keyboard_s2_cr.row(telebot.types.InlineKeyboardButton(
        'Paypal USD', callback_data='pp-USD-{0}-{1}'.format(ex_code, buy_sell)))
    keyboard_s2_cr.row(telebot.types.InlineKeyboardButton(
        'Advcash USD', callback_data='ad-USD-{0}-{1}'.format(ex_code, buy_sell)))
    keyboard_s2_cr.row(telebot.types.InlineKeyboardButton(
        'Payeer USD', callback_data='py-USD-{0}-{1}'.format(ex_code, buy_sell)))
    if buy_sell == 'sell':
        bot.send_message(message.chat.id, 'Now, indicate the currency you want to receive:',
                         reply_markup=keyboard_s2_cr)
    elif buy_sell == 'buy':
        bot.send_message(message.chat.id, 'Now, indicate the currency you want to pay with:',
                         reply_markup=keyboard_s2_cr)


def buy_sell_crypto_3(message, ex_code, ex_code2, buy_sell):
    keyboard_cncl = telebot.types.InlineKeyboardMarkup()
    keyboard_cncl.row(telebot.types.InlineKeyboardButton('Cancel', callback_data='sys-cncl'))
    if buy_sell == 'sell':
        price = course[ex_code]
        low = low1[ex_code]
        bot.send_message(message.chat.id, 'You give: {0} \n'
                                          'You get: {1} \n'
                                          'Change rate: 1 {0} = {2} {1} \n'
                                          'Write the amount you want to change from {3} to 999999 {0} '
                                          '(no symbols, only numbers)'.format(ex_code, ex_code2, price,
                                                                              low),
                         reply_markup=keyboard_cncl)
    else:
        price = course[ex_code2]
        low = low1[ex_code2]
        bot.send_message(message.chat.id, 'You give: {0} \n'
                                          'You get: {1} \n'
                                          'Change rate: 1 {1} = {2} {0}\n'
                                          'Write the amount you want to change from {3} to 999999 {1} '
                                          '(no symbols, only numbers)'.format(ex_code, ex_code2, price,
                                                                              low),
                         reply_markup=keyboard_cncl)

    bot.register_next_step_handler(message, sell_crypto_4, ex_code, ex_code2, price, buy_sell, low)


def sell_crypto_4(message, ex_code, ex_code2, price, buy_sell, low):
    keyboard_cncl = telebot.types.InlineKeyboardMarkup()
    keyboard_cncl.row(telebot.types.InlineKeyboardButton('Cancel', callback_data='sys-cncl'))

    try:
        amount = float(message.text)
        if buy_sell == 'sell':
            if low <= amount <= 999999:
                summ = round(price * amount, 2)
                bot.send_message(message.chat.id, 'You will get: {0} {1}\n'
                                                  'Write down your 16-digits card number as follows:\n'
                                                  '1234 1234 1234 1234\n'
                                                  '\n'
                                                  '*According to our privacy policy all transactions are secured and '
                                                  'encrypted by VISA/MasterCard'.format(summ, ex_code2),
                                 reply_markup=keyboard_cncl)
                bot.register_next_step_handler(message, sell_crypto_5, ex_code, ex_code2, price, amount, buy_sell, summ)
            else:
                bot.send_message(message.chat.id, 'Something is incorrect, try again not')
                buy_sell_crypto_3(message, ex_code, ex_code2, buy_sell)
        else:
            if low <= amount <= 999999:
                summ = amount
                bot.send_message(message.chat.id, 'You will get: {0} {1}\n'
                                                  'WRITE DOWN YOUR {1} ADDRESS: \n'
                                                  'f0598uf958fu958fj9585989f85\n'.format(summ,
                                                                                         ex_code2),
                                 reply_markup=keyboard_cncl)
                bot.register_next_step_handler(message, sell_crypto_5, ex_code, ex_code2, price, amount, buy_sell, summ)
            else:
                bot.send_message(message.chat.id, 'Something is incorrect, try again not')
                buy_sell_crypto_3(message, ex_code, ex_code2, buy_sell)
    except Exception:
        bot.send_message(message.chat.id, 'Something is incorrect, try again')
        main_menu(message)


def sell_crypto_5(message, ex_code, ex_code2, price, amount, buy_sell, summ):
    keyboard_confirm_cncl = telebot.types.InlineKeyboardMarkup()
    keyboard_confirm_cncl.row(telebot.types.InlineKeyboardButton(
        'Confirm', callback_data='sys-cnfrm-sell-' + str(ex_code) + str(amount)),
        telebot.types.InlineKeyboardButton('Cancel', callback_data='sys-cncl'))
    keyboard_confirm_cncl_buy = telebot.types.InlineKeyboardMarkup()
    keyboard_confirm_cncl_buy.row(telebot.types.InlineKeyboardButton(
        'Confirm', callback_data='sys-cnfrm-buy1-' + str(ex_code) + str(summ * price)),
        telebot.types.InlineKeyboardButton('Cancel', callback_data='sys-cncl'))
    try:
        if buy_sell == 'sell':
            check_card = [int(i) for i in message.text.replace(' ', '')]
            if len(check_card) == 16:
                bot.send_message(message.chat.id, 'Now let’s check that we are doing everything’s right.\n'
                                                  'Exchange will be made:\n'
                                                  'You give: {0} {2}\n'
                                                  'You get: {1} {3} on your {4}'.format(amount,
                                                                                        summ,
                                                                                        ex_code,
                                                                                        ex_code2, message.text),
                                 reply_markup=keyboard_confirm_cncl)
            else:
                bot.send_message(message.chat.id, 'Something is incorrect, try again')
                buy_sell_crypto_3(message, ex_code2, ex_code, buy_sell)
        else:
            summ = summ * price
            address = message.text
            bot.send_message(message.chat.id, 'Now let’s check that we are doing everything’s right.\n'
                                              'Exchange will be made:\n'
                                              'You give: {1} {2}\n'
                                              'You get: {0} {3} on your {4}'.format(amount,
                                                                                    summ,
                                                                                    ex_code,
                                                                                    ex_code2, address),
                             reply_markup=keyboard_confirm_cncl_buy)
    except Exception:
        bot.send_message(message.chat.id, 'Something is incorrect, try again')


@bot.message_handler(commands=['check'])
def check_order(message):
    bot.send_message(message.chat.id, 'Write your order ID:')
    bot.register_next_step_handler(message, check_order_2)


def check_order_2(message):
    if message.text in lis:
        bot.send_message(message.chat.id, 'Your order is {}\n'
                                          'Status: Pending'.format(message.text))
    else:
        try:
            order_id = message.text
            request_c = OrdersCaptureRequest(order_id)
            try:
                bot.send_chat_action(message.chat.id, 'typing')
                response = client.execute(request_c)
                order = response.result.id
                bot.send_message(message.chat.id, 'Your order is {}'.format(order))
            except IOError as ioe:
                if isinstance(ioe, HttpError):
                    if ioe.status_code == 422:
                        bot.send_message(message.chat.id, 'Your order is created but not approved')
                    else:
                        bot.send_message(message.chat.id, 'Invalid order ID')
                else:
                    pass

        except Exception:
            bot.send_message(message.chat.id, 'Something is incorrect, try again')


while True:
    try:
        bot.infinity_polling(True)
    except Exception:
        time.sleep(15)
