#%%
import gnupg
import os

# Configurar o diretório de chaves
gpg = gnupg.GPG(gnupghome='/path/to/your/gpg-keys')

# Importar as chaves públicas e privadas (se já não tiver importado)
with open('/path/to/public_key.asc', 'r') as f:
    gpg.import_keys(f.read())

with open('/path/to/private_key.asc', 'r') as f:
    gpg.import_keys(f.read())

# Verificar as chaves importadas
print(gpg.list_keys())
print(gpg.list_keys(True))  # Para ver as chaves privadas

#%%
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import gnupg

# Configurar o GPG
gpg = gnupg.GPG(gnupghome='/path/to/your/gpg-keys')

# Função para descriptografar mensagens
def decrypt_message(encrypted_message):
    decrypted_data = gpg.decrypt(encrypted_message)
    return str(decrypted_data)

# Função para criptografar mensagens
def encrypt_message(message, recipient):
    encrypted_data = gpg.encrypt(message, recipient)
    return str(encrypted_data)

# Comando de inicialização
def start(update, context):
    update.message.reply_text('Envie uma mensagem criptografada.')

# Função para lidar com mensagens recebidas
def handle_message(update, context):
    encrypted_message = update.message.text
    decrypted_message = decrypt_message(encrypted_message)
    
    # Responder com a mensagem descriptografada
    update.message.reply_text(f'Mensagem descriptografada: {decrypted_message}')
    
    # Criar uma resposta criptografada
    encrypted_reply = encrypt_message('Esta é uma resposta criptografada', 'seu_amigo@example.com')
    update.message.reply_text(f'Mensagem criptografada para envio: {encrypted_reply}')

# Configurar o bot
def main():
    updater = Updater('YOUR_TELEGRAM_BOT_TOKEN', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
