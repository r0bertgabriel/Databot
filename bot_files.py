#%%
import telebot
from telebot import types
import schedule
import time
import threading
import os
import pandas as pd
import sqlite3

from dotenv import load_dotenv

load_dotenv()

# Acessar as variáveis ambiente
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')
db_password = os.getenv('DB_PASSWORD')
if api_key is None:
    raise ValueError("API_KEY environment variable not found")


bot = telebot.TeleBot(api_key)
# Dicionário para armazenar o estado do usuário
user_states = {}

# Arte ASCII para a mensagem de boas-vindas
ascii_art = """
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
█░██░██░██░██░██░██░██░██░██░░░░░░░░░░█
█░██░██░██░██░██░██░██░██░██░░░░░░░░░░█
█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░█░░░░█▀▀▀█░█▀▀█░█▀▀▄░▀█▀░█▄░░█░█▀▀█░░
░░█░░░░█░░░█░█▄▄█░█░░█░░█░░█░█░█░█░▄▄░░
░░█▄▄█░█▄▄▄█░█░░█░█▄▄▀░▄█▄░█░░▀█░█▄▄█░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

# Função para iniciar a interação com o bot
@bot.message_handler(commands=['start'])
def start(mensagem):
    chat_id = mensagem.chat.id
    comandos = [
        "/csv - Enviar arquivos CSV",
        "/txt - Enviar arquivos TXT e transformá-los em CSV",
        "/db - Adicionar arquivos CSV ao banco de dados",
        "/sql_table - Listar tabelas no banco de dados",
        "/listar_arquivos_csv - Listar arquivos CSV na pasta 'csv'"
    ]
    resposta = "Olá! Bem-vindo ao bot. Aqui estão os comandos disponíveis:\n" + "\n".join(comandos)
    bot.send_message(chat_id, ascii_art)
    bot.send_message(chat_id, resposta)
    
    # Enviar o vídeo de boas-vindas como animação
    video_path = 'gif.mp4'
    if os.path.exists(video_path):
        with open(video_path, 'rb') as video:
            bot.send_animation(chat_id, video)
    else:
        bot.send_message(chat_id, "O vídeo de boas-vindas não foi encontrado.")

# Função para receber e salvar tabelas CSV enviadas pelo usuário
@bot.message_handler(commands=['csv'])
def receber_tabelas_csv(mensagem):
    chat_id = mensagem.chat.id
    user_states[chat_id] = {'state': 'waiting_for_csv'}
    bot.reply_to(mensagem, "Aguardando o envio dos arquivos CSV...")

@bot.message_handler(commands=['txt'])
def receber_tabelas_txt(mensagem):
    chat_id = mensagem.chat.id
    user_states[chat_id] = {'state': 'waiting_for_txt'}
    bot.reply_to(mensagem, "Aguardando o envio dos arquivos TXT...")

@bot.message_handler(content_types=['document'])
def handle_document(mensagem):
    chat_id = mensagem.chat.id
    state_info = user_states.get(chat_id, {})
    if state_info.get('state') == 'waiting_for_csv':
        salvar_arquivo_csv(mensagem)
    elif state_info.get('state') == 'waiting_for_txt':
        salvar_arquivo_txt(mensagem)
    else:
        bot.reply_to(mensagem, "Não estou esperando o envio de arquivos no momento.")

def salvar_arquivo_csv(mensagem):
    chat_id = mensagem.chat.id
    try:
        if not os.path.exists('csv'):
            os.makedirs('csv')

        document = mensagem.document
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        if document.mime_type == 'text/csv' or document.file_name.endswith('.csv'):
            src = os.path.join('csv', document.file_name)
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(mensagem, f"Arquivo CSV {document.file_name} salvo com sucesso!")
        else:
            bot.reply_to(mensagem, f"Por favor, envie um arquivo CSV. {document.file_name} não é um CSV.")
    except Exception as e:
        bot.reply_to(mensagem, f"Ocorreu um erro ao salvar os arquivos: {e}")

def salvar_arquivo_txt(mensagem):
    chat_id = mensagem.chat.idgit
    try:
        if not os.path.exists('txt'):
            os.makedirs('txt')

        document = mensagem.document
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        if document.mime_type == 'text/plain' or document.file_name.endswith('.txt'):
            src_txt = os.path.join('txt', document.file_name)
            with open(src_txt, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # Transformar TXT em CSV
            if not os.path.exists('csv'):
                os.makedirs('csv')
            src_csv = os.path.join('csv', os.path.splitext(document.file_name)[0] + '.csv')
            with open(src_txt, 'r') as txt_file, open(src_csv, 'w') as csv_file:
                for line in txt_file:
                    csv_file.write(line.replace('\t', ','))
            
            bot.reply_to(mensagem, f"Arquivo TXT {document.file_name} transformado e salvo como CSV com sucesso!")
        else:
            bot.reply_to(mensagem, f"Por favor, envie um arquivo TXT. {document.file_name} não é um TXT.")
    except Exception as e:
        bot.reply_to(mensagem, f"Ocorreu um erro ao salvar os arquivos: {e}")

# Função para listar todos os arquivos CSV na pasta 'csv'
@bot.message_handler(commands=['listar_arquivos_csv'])
def listar_arquivos_csv(mensagem):
    chat_id = mensagem.chat.id
    if not os.path.exists('csv'):
        os.makedirs('csv')
    arquivos_csv = [f for f in os.listdir('csv') if f.endswith('.csv')]
    if arquivos_csv:
        markup = types.InlineKeyboardMarkup()
        for arquivo in arquivos_csv:
            markup.add(types.InlineKeyboardButton(arquivo, callback_data=f"arquivo:{arquivo}"))
        bot.send_message(mensagem.chat.id, "Selecione um arquivo CSV:", reply_markup=markup)
    else:
        bot.send_message(mensagem.chat.id, "Nenhum arquivo CSV encontrado na pasta 'csv'.")

# Função para detectar o delimitador do CSV
def detectar_delimitador(nome_arquivo):
    with open(nome_arquivo, 'r') as file:
        linha = file.readline()
        if ';' in linha:
            return ';'
        elif ',' in linha:
            return ','
        elif '\t' in linha:
            return '\t'
        else:
            return ','  # Padrão para CSV

# Função para adicionar arquivo CSV como tabela no banco de dados
@bot.message_handler(commands=['db'])
def listar_opcoes_db(mensagem):
    chat_id = mensagem.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Adicionar um arquivo", callback_data="db_opcao:um_arquivo"))
    markup.add(types.InlineKeyboardButton("Adicionar todos os arquivos", callback_data="db_opcao:todos_arquivos"))
    bot.send_message(mensagem.chat.id, "Escolha uma opção:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("db_opcao:"))
def callback_opcao_db(call):
    chat_id = call.message.chat.id
    opcao = call.data.split(":")[1]
    if opcao == "um_arquivo":
        listar_arquivos_para_db(call.message)
    elif opcao == "todos_arquivos":
        adicionar_todos_arquivos_db(call.message.chat.id)

def listar_arquivos_para_db(mensagem):
    if not os.path.exists('csv'):
        os.makedirs('csv')
    arquivos_csv = [f for f in os.listdir('csv') if f.endswith('.csv')]
    if arquivos_csv:
        markup = types.InlineKeyboardMarkup()
        for arquivo in arquivos_csv:
            markup.add(types.InlineKeyboardButton(arquivo, callback_data=f"db_arquivo:{arquivo}"))
        bot.send_message(mensagem.chat.id, "Selecione um arquivo CSV para adicionar como tabela no banco de dados:", reply_markup=markup)
    else:
        bot.send_message(mensagem.chat.id, "Nenhum arquivo CSV encontrado na pasta 'csv'.")

def adicionar_todos_arquivos_db(chat_id):
    try:
        if not os.path.exists('tabelas.db'):
            conn = sqlite3.connect('tabelas.db')
            conn.close()

        arquivos_csv = [f for f in os.listdir('csv') if f.endswith('.csv')]
        if arquivos_csv:
            conn = sqlite3.connect('tabelas.db')
            for arquivo in arquivos_csv:
                delimitador = detectar_delimitador(os.path.join('csv', arquivo))
                df = pd.read_csv(os.path.join('csv', arquivo), delimiter=delimitador)
                df.to_sql(name=os.path.splitext(arquivo)[0], con=conn, if_exists='replace', index=False)
            conn.close()
            bot.send_message(chat_id, "Todos os arquivos CSV foram adicionados como tabelas no banco de dados.")
        else:
            bot.send_message(chat_id, "Nenhum arquivo CSV encontrado na pasta 'csv'.")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao adicionar tabelas no banco de dados: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("db_arquivo:"))
def callback_adicionar_tabela_db(call):
    chat_id = call.message.chat.id
    nome_arquivo = call.data.split(":")[1]
    adicionar_tabela_db(call.message.chat.id, nome_arquivo)

def adicionar_tabela_db(chat_id, nome_arquivo):
    try:
        if not os.path.exists('tabelas.db'):
            conn = sqlite3.connect('tabelas.db')
            conn.close()

        delimitador = detectar_delimitador(os.path.join('csv', nome_arquivo))
        df = pd.read_csv(os.path.join('csv', nome_arquivo), delimiter=delimitador)
        conn = sqlite3.connect('tabelas.db')
        df.to_sql(name=os.path.splitext(nome_arquivo)[0], con=conn, if_exists='replace', index=False)
        conn.close()
        bot.send_message(chat_id, f"Arquivo {nome_arquivo} adicionado como tabela no banco de dados.")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao adicionar tabela no banco de dados: {str(e)}")

# Função para listar tabelas no banco de dados
@bot.message_handler(commands=['sql_table'])
def listar_tabelas(mensagem):
    chat_id = mensagem.chat.id
    conn = sqlite3.connect('tabelas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    conn.close()

    if tabelas:
        markup = types.InlineKeyboardMarkup()
        for tabela in tabelas:
            markup.add(types.InlineKeyboardButton(tabela[0], callback_data=f"tabela:{tabela[0]}"))
        bot.send_message(chat_id, "Selecione uma tabela para ver as colunas disponíveis:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Nenhuma tabela encontrada no banco de dados.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("tabela:"))
def listar_colunas(call):
    chat_id = call.message.chat.id
    tabela = call.data.split(":")[1]
    conn = sqlite3.connect('tabelas.db')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tabela});")
    colunas = cursor.fetchall()
    conn.close()

    if colunas:
        colunas_str = "\n".join([coluna[1] for coluna in colunas])
        bot.send_message(chat_id, f"Colunas disponíveis na tabela {tabela}:\n{colunas_str}")
        bot.send_message(chat_id, "Agora você pode digitar sua consulta SQL.")
        user_states[chat_id] = {'state': 'waiting_for_query', 'tabela': tabela}
    else:
        bot.send_message(chat_id, "Nenhuma coluna encontrada na tabela.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_query')
def executar_query_personalizada(mensagem):
    chat_id = mensagem.chat.id
    query = mensagem.text
    try:
        conn = sqlite3.connect('tabelas.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        if not df.empty:
            bot.send_message(chat_id, df.to_string(index=False))
        else:
            bot.send_message(chat_id, "A consulta não retornou resultados.")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao executar a consulta SQL: {str(e)}")
    finally:
        user_states[chat_id] = {}

# Iniciar o agendamento em um thread separado
def agendar_envio_diario():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=agendar_envio_diario).start()

# Iniciar o bot
bot.polling()
# %%
