import telebot
import io
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import seaborn as sns

# Substitua 'YOUR_TOKEN' pelo seu token do Telegram
token = 'YOUR_TOKEN'
bot = telebot.TeleBot(token)

# /start - Comando para iniciar o bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Eu sou um bot analista de dados. Para ver o que eu posso fazer, digite /help")

# /help - Comando para mostrar a lista de funcionalidades
@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, '''Eu posso realizar as seguintes funções:
/csv_info - Você faz o upload de um arquivo CSV e eu te dou informações sobre o número de linhas e colunas do DataFrame (shape);
/csv_cut - Você faz o upload de um arquivo CSV, eu removo todas as linhas, exceto a primeira, e devolvo o arquivo editado;
/csv_distr - Você faz o upload de um arquivo CSV e insere o nome da coluna, e eu construo uma distribuição de dados dessa coluna (displot).''')

# /csv_info - Comando para fornecer informações sobre o CSV
@bot.message_handler(commands=['csv_info'])
def handle_csv_info(message):
    bot.send_message(message.chat.id, "Por favor, envie o arquivo CSV")
    bot.register_next_step_handler(message, handle_info)

# Função para processar o arquivo CSV enviado e fornecer informações
def handle_info(message):
    try:
        if message.document.mime_type == 'text/csv':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            df = pd.read_csv(io.StringIO(downloaded_file.decode()))

            # Envia informações sobre o tamanho do DataFrame
            bot.send_message(message.chat.id, "O DataFrame tem {} linhas e {} colunas".format(df.shape[0], df.shape[1]))
            # Envia informações sobre os nomes das colunas e tipos de dados
            bot.send_message(message.chat.id, "Nomes das colunas e tipos de dados:\n\n{}".format(df.dtypes))
        else:
            bot.send_message(message.chat.id, "Somente arquivos CSV são aceitos")
    except Exception as e:
        bot.send_message(message.chat.id, "Erro. Talvez você não tenha enviado o arquivo CSV corretamente. Por favor, tente novamente.")

# /csv_cut - Comando para cortar o CSV, mantendo apenas a primeira linha
@bot.message_handler(commands=['csv_cut'])
def handle_csv_info(message):
    bot.send_message(message.chat.id, "Por favor, envie o arquivo CSV")
    bot.register_next_step_handler(message, handle_docs_photo)

# Função para processar o CSV e retornar um arquivo com apenas a primeira linha
def handle_docs_photo(message):
    try:
        if message.document.mime_type == 'text/csv':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            df = pd.read_csv(io.StringIO(downloaded_file.decode()))
            # Mantém apenas a primeira linha
            df = df.iloc[:1, :]
            # Prepara o arquivo para envio
            processed_file = io.StringIO()
            df.to_csv(processed_file, index=False)
            processed_file.seek(0)
            bot.send_document(message.chat.id, processed_file, visible_file_name='processed_file.csv')
            bot.send_message(message.chat.id, "Arquivo processado enviado!")
        else:
            bot.send_message(message.chat.id, "Somente arquivos CSV são aceitos")
    except Exception as e:
        bot.send_message(message.chat.id, "Erro. Por favor, tente novamente.")

# /csv_distr - Comando para criar gráfico de distribuição com base em uma coluna específica
@bot.message_handler(commands=['csv_distr'])
def handle_csv_distr(message):
    bot.send_message(message.chat.id, "Por favor, envie o arquivo CSV")
    bot.register_next_step_handler(message, handle_distr)

# Função para processar o arquivo CSV e solicitar o nome da coluna para distribuição
def handle_distr(message):
    try:
        if message.document.mime_type == 'text/csv':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            global df
            df = pd.read_csv(io.StringIO(downloaded_file.decode()))
            bot.send_message(message.chat.id, "Digite o nome da coluna para gerar a distribuição:")
            bot.register_next_step_handler(message, handle_distr_column)
        else:
            bot.send_message(message.chat.id, "Somente arquivos CSV são aceitos")
    except Exception as e:
        bot.send_message(message.chat.id, "Erro. Por favor, tente novamente.")

# Função para gerar o gráfico de distribuição da coluna especificada
def handle_distr_column(message):
    try:
        column_name = message.text
        column = df[column_name]
        sns.displot(column)  # Cria o gráfico de distribuição
        plt.xticks(rotation=45)
        plt.savefig("distribution.png")  # Salva o gráfico como imagem
        with open("distribution.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove("distribution.png")
    except KeyError:
        bot.send_message(message.chat.id, "Coluna não encontrada ou tipo de dados incompatível")
        plt.clf()  # Limpa a figura do matplotlib

# Monitoramento contínuo para comandos e interações
bot.polling(none_stop=True)

# Função para lidar com outras mensagens
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "Desculpe, não entendi. Use um dos comandos disponíveis.")

# Inicializa o bot
if __name__ == '__main__':
    bot.polling()
