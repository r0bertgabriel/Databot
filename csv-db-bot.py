#%%
import telebot
from telebot import types
import schedule
import time
import threading
import os
import pandas as pd
import sqlite3

# Chave da API do bot
chave_api = "TOKEN"
bot = telebot.TeleBot(chave_api)

# Dicionário para armazenar o estado do usuário
user_states = {}

# Função para iniciar a interação com o bot
@bot.message_handler(commands=['start'])
def start(mensagem):
    chat_id = mensagem.chat.id
    bot.send_message(chat_id, "Olá! Bem-vindo ao bot. /csv /sql /sql_table /listar_arquivos_csv.")

# Função para receber e salvar tabela CSV enviada pelo usuário
@bot.message_handler(commands=['csv'])
def receber_tabela_csv(mensagem):
    user_states[mensagem.chat.id] = {'state': 'waiting_for_csv'}
    bot.reply_to(mensagem, "Aguardando o envio do arquivo CSV...")

@bot.message_handler(content_types=['document'])
def handle_document(mensagem):
    chat_id = mensagem.chat.id
    state_info = user_states.get(chat_id, {})
    if state_info.get('state') == 'waiting_for_csv':
        try:
            file_info = bot.get_file(mensagem.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            if mensagem.document.mime_type == 'text/csv' or mensagem.document.file_name.endswith('.csv'):
                src = os.path.join('.', mensagem.document.file_name)
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                bot.reply_to(mensagem, "Arquivo CSV salvo com sucesso!")
            else:
                bot.reply_to(mensagem, "Por favor, envie um arquivo CSV.")
        except Exception as e:
            bot.reply_to(mensagem, f"Ocorreu um erro ao salvar o arquivo: {e}")
        finally:
            user_states[chat_id] = {}
    else:
        bot.reply_to(mensagem, "Não estou esperando o envio de um arquivo CSV no momento.")

# Função para listar todos os arquivos CSV no diretório atual
@bot.message_handler(commands=['listar_arquivos_csv'])
def listar_arquivos_csv(mensagem):
    arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    if arquivos_csv:
        markup = types.InlineKeyboardMarkup()
        for arquivo in arquivos_csv:
            markup.add(types.InlineKeyboardButton(arquivo, callback_data=f"arquivo:{arquivo}"))
        bot.send_message(mensagem.chat.id, "Selecione um arquivo CSV:", reply_markup=markup)
    else:
        bot.send_message(mensagem.chat.id, "Nenhum arquivo CSV encontrado no diretório atual.")

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
@bot.message_handler(commands=['sql'])
def listar_arquivos_para_sql(mensagem):
    arquivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    if arquivos_csv:
        markup = types.InlineKeyboardMarkup()
        for arquivo in arquivos_csv:
            markup.add(types.InlineKeyboardButton(arquivo, callback_data=f"sql_arquivo:{arquivo}"))
        bot.send_message(mensagem.chat.id, "Selecione um arquivo CSV para adicionar como tabela no banco de dados:", reply_markup=markup)
    else:
        bot.send_message(mensagem.chat.id, "Nenhum arquivo CSV encontrado no diretório atual.")

def adicionar_tabela_sql(chat_id, nome_arquivo):
    try:
        # Verificar se o banco de dados existe, se não, criar
        if not os.path.exists('tabelas.db'):
            conn = sqlite3.connect('tabelas.db')
            conn.close()

        delimitador = detectar_delimitador(nome_arquivo)
        df = pd.read_csv(nome_arquivo, delimiter=delimitador)
        conn = sqlite3.connect('tabelas.db')
        df.to_sql(name=os.path.splitext(nome_arquivo)[0], con=conn, if_exists='replace', index=False)
        conn.close()
        bot.send_message(chat_id, f"Arquivo {nome_arquivo} adicionado como tabela no banco de dados.")
    except Exception as e:
        bot.send_message(chat_id, f"Erro ao adicionar tabela no banco de dados: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sql_arquivo:"))
def callback_adicionar_tabela_sql(call):
    nome_arquivo = call.data.split(":")[1]
    adicionar_tabela_sql(call.message.chat.id, nome_arquivo)

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
    tabela = call.data.split(":")[1]
    chat_id = call.message.chat.id
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
