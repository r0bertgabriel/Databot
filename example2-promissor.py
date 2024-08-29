#%%
import telebot

chave_api = ""
bot = telebot.TeleBot(chave_api)

def verificar(mensagem):
    return True
    

@bot.message_handler(func=verificar)
def responder_mensagem(mensagem):
    bot.reply_to(mensagem, "Olá, eu sou um bot de criptografia. Digite /help para ver os comandos disponíveis.")


texto = """ Escolha uma das opções abaixo(Clique no item):
/opcao1 - Criptografar
/opcao2 - Descriptografar
/opcao3 - Sair
/opcao4 - Criptografar e Descripitografar automaticamente
/opcao5 - Ajuda
"""

bot.polling() # Inicia o bot e fica escutando mensagens
# %%
