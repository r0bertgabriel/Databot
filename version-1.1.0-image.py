#%%
import telebot
from telebot import types
import schedule
import time
import threading
#%%
chave_api = "7381913977:AAEJe-u-DLY_1YRqB_zqw95mIQg3M84uhq8"
bot = telebot.TeleBot(chave_api)

# Função para verificar mensagens
def verificar(mensagem):
    return True

# Função para enviar imagem automaticamente uma vez ao dia
def enviar_imagem_diaria():
    with open('imagem_diaria.jpg', 'rb') as photo:
        bot.send_photo(chat_id, photo, caption="Aqui está sua imagem diária!")

# Função para agendar o envio diário
def agendar_envio_diario():
    schedule.every().day.at("09:00").do(enviar_imagem_diaria)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Função para responder mensagens
@bot.message_handler(func=verificar)
def responder_mensagem(mensagem):
    chat_id = mensagem.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2)
    botao1 = types.KeyboardButton('/imagem1')
    botao2 = types.KeyboardButton('/imagem2')
    botao3 = types.KeyboardButton('/imagem3')
    botao4 = types.KeyboardButton('/ajuda')
    markup.add(botao1, botao2, botao3, botao4)
    bot.send_message(chat_id, "Olá, eu sou um bot de criptografia. Escolha uma das opções abaixo:", reply_markup=markup)

# Função para enviar imagem 1
@bot.message_handler(commands=['imagem1'])
def enviar_imagem1(mensagem):
    with open('imagem1.jpg', 'rb') as photo:
        bot.send_photo(mensagem.chat.id, photo, caption="Aqui está a imagem 1!")

# Função para enviar imagem 2
@bot.message_handler(commands=['imagem2'])
def enviar_imagem2(mensagem):
    with open('imagem2.jpg', 'rb') as photo:
        bot.send_photo(mensagem.chat.id, photo, caption="Aqui está a imagem 2!")

# Função para enviar imagem 3
@bot.message_handler(commands=['imagem3'])
def enviar_imagem3(mensagem):
    with open('imagem3.jpg', 'rb') as photo:
        bot.send_photo(mensagem.chat.id, photo, caption="Aqui está a imagem 3!")

# Função para mostrar ajuda
@bot.message_handler(commands=['ajuda'])
def enviar_ajuda(mensagem):
    texto = """ Escolha uma das opções abaixo(Clique no item):
/imagem1 - Receber Imagem 1
/imagem2 - Receber Imagem 2
/imagem3 - Receber Imagem 3
"""
    bot.send_message(mensagem.chat.id, texto)

# Iniciar o agendamento em um thread separado
threading.Thread(target=agendar_envio_diario).start()

# Iniciar o bot
bot.polling()
# %%
