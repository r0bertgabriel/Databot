#%%
import telebot
from telebot import types
import schedule
import time
import threading
import csv
import os
import uuid
#%%
chave_api = "7381913977:AAEJe-u-DLY_1YRqB_zqw95mIQg3M84uhq8"
bot = telebot.TeleBot(chave_api)

# Dicionário para armazenar o estado do usuário
user_states = {}

# Constantes para os estados do usuário
AUTHENTICATING = "authenticating"
REGISTERING = "registering"
REGISTERED = "registered"
ADMIN_AUTHENTICATED = "admin_authenticated"

# Função para verificar mensagens
def verificar(mensagem):
    return True

# Função para adicionar informações da empresa no CSV
def add_company_info(chat_id, company_name, email, cnpj, cidade, bairro, categoria):
    file_exists = os.path.isfile('registros.csv')
    with open('registros.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['ID', 'Chat ID', 'Nome da Empresa', 'Email', 'CNPJ', 'Cidade', 'Bairro', 'Categoria'])
        writer.writerow([str(uuid.uuid4()), chat_id, company_name, email, cnpj, cidade, bairro, categoria])

# Função para validar CPF/CNPJ
def validar_cpf_cnpj(cpf_cnpj):
    cpf_cnpj = cpf_cnpj.replace('.', '').replace('-', '').replace('/', '').strip()
    return len(cpf_cnpj) == 11 or len(cpf_cnpj) == 14

# Função para mostrar o menu de opções
def show_options_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    botao1 = types.KeyboardButton('/imagem1')
    botao2 = types.KeyboardButton('/imagem2')
    botao3 = types.KeyboardButton('/imagem3')
    botao4 = types.KeyboardButton('/ajuda')
    markup.add(botao1, botao2, botao3, botao4)
    bot.send_message(chat_id, "Escolha uma das opções abaixo:", reply_markup=markup)

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

# Função para iniciar a interação com o bot
@bot.message_handler(commands=['start'])
def start(mensagem):
    chat_id = mensagem.chat.id
    bot.send_message(chat_id, "Olá! Bem-vindo ao bot. Use /registro para iniciar o registro da sua empresa.")

# Função para iniciar o registro
@bot.message_handler(commands=['registro'])
def registro(mensagem):
    chat_id = mensagem.chat.id
    user_states[chat_id] = {'state': AUTHENTICATING, 'step': 'choose_admin'}
    markup = types.ReplyKeyboardMarkup(row_width=1)
    botao1 = types.KeyboardButton('Admin 1')
    botao2 = types.KeyboardButton('Admin 2')
    botao3 = types.KeyboardButton('Admin 3')
    markup.add(botao1, botao2, botao3)
    bot.send_message(chat_id, "Escolha um administrador para continuar:", reply_markup=markup)

# Função para lidar com a autenticação do administrador
@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get('state') == AUTHENTICATING)
def handle_authentication(mensagem):
    chat_id = mensagem.chat.id
    state_info = user_states[chat_id]

    if state_info['step'] == 'choose_admin':
        admin_choice = mensagem.text.strip().lower()
        if admin_choice in ['admin 1', 'admin 2', 'admin 3']:
            state_info['admin_choice'] = admin_choice
            state_info['step'] = 'enter_password'
            bot.send_message(chat_id, "Por favor, insira a senha do administrador:")
        else:
            bot.send_message(chat_id, "Escolha inválida. Por favor, escolha um administrador válido:")
    elif state_info['step'] == 'enter_password':
        password = mensagem.text.strip()
        valid_passwords = {'admin 1': '123', 'admin 2': '321', 'admin 3': '000'}
        if password == valid_passwords.get(state_info['admin_choice']):
            state_info['state'] = ADMIN_AUTHENTICATED
            show_admin_options(chat_id)
        else:
            bot.send_message(chat_id, "Senha inválida. Por favor, insira a senha correta:")

# Função para mostrar opções do administrador
def show_admin_options(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    botao1 = types.KeyboardButton('/novo_registro')
    botao2 = types.KeyboardButton('/editar_registro')
    botao3 = types.KeyboardButton('/relacionar_registro')
    markup.add(botao1, botao2, botao3)
    bot.send_message(chat_id, "Escolha uma das opções abaixo:", reply_markup=markup)

# Função para iniciar o novo registro
@bot.message_handler(commands=['novo_registro'])
def novo_registro(mensagem):
    chat_id = mensagem.chat.id
    user_states[chat_id] = {'state': REGISTERING, 'step': 'company_name'}
    bot.send_message(chat_id, "Por favor, envie o nome da sua empresa:")

# Função para lidar com mensagens durante o registro
@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get('state') == REGISTERING)
def handle_registration(mensagem):
    chat_id = mensagem.chat.id
    state_info = user_states[chat_id]

    if state_info['step'] == 'company_name':
        state_info['company_name'] = mensagem.text.strip().lower()
        state_info['step'] = 'email'
        bot.send_message(chat_id, "Agora, por favor, envie o e-mail da sua empresa:")
    elif state_info['step'] == 'email':
        state_info['email'] = mensagem.text.strip().lower()
        state_info['step'] = 'cnpj'
        bot.send_message(chat_id, "Por favor, envie o CNPJ da sua empresa:")
    elif state_info['step'] == 'cnpj':
        cnpj = mensagem.text.strip()
        if validar_cpf_cnpj(cnpj):
            state_info['cnpj'] = cnpj
            state_info['step'] = 'cidade'
            bot.send_message(chat_id, "Por favor, envie a cidade da sua empresa:")
        else:
            bot.send_message(chat_id, "CNPJ inválido. Por favor, envie um CNPJ válido:")
    elif state_info['step'] == 'cidade':
        state_info['cidade'] = mensagem.text.strip().lower()
        state_info['step'] = 'bairro'
        bot.send_message(chat_id, "Por favor, envie o bairro da sua empresa:")
    elif state_info['step'] == 'bairro':
        state_info['bairro'] = mensagem.text.strip().lower()
        state_info['step'] = 'categoria'
        bot.send_message(chat_id, "Por favor, envie a categoria da sua empresa:")
    elif state_info['step'] == 'categoria':
        state_info['categoria'] = mensagem.text.strip().lower()

        # Salva os dados no CSV
        add_company_info(chat_id, state_info['company_name'], state_info['email'], state_info['cnpj'], state_info['cidade'], state_info['bairro'], state_info['categoria'])
        
        bot.send_message(chat_id, f"Obrigado! As informações da sua empresa foram registradas:\nEmpresa: {state_info['company_name']}\nEmail: {state_info['email']}\nCNPJ: {state_info['cnpj']}\nCidade: {state_info['cidade']}\nBairro: {state_info['bairro']}\nCategoria: {state_info['categoria']}")
        user_states[chat_id] = {'state': REGISTERED}

        # Mostra o menu de opções após o registro
        show_options_menu(chat_id)

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