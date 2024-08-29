#%%
import gnupg
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Permitir loops de eventos aninhados
nest_asyncio.apply()

# Configurar o GPG
def configure_gpg():
    gpg = gnupg.GPG()
    gpg.gnupghome = '/home/kali/keys/'
    with open('/home/keys/chave_publica.asc', 'r') as f:
        gpg.import_keys(f.read())
    with open('/home/keys/chave_privada.asc', 'r') as f:
        gpg.import_keys(f.read())
    return gpg

# Função para descriptografar mensagens
def decrypt_message(gpg, encrypted_message):
    decrypted_data = gpg.decrypt(encrypted_message)
    return str(decrypted_data)

# Função para criptografar mensagens
def encrypt_message(gpg, message, recipient):
    encrypted_data = gpg.encrypt(message, recipient)
    return str(encrypted_data)

# Comando de inicialização
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Envie uma mensagem criptografada.')

# Função para lidar com mensagens recebidas
def handle_message(update: Update, context: CallbackContext):
    encrypted_message = update.message.text
    decrypted_message = decrypt_message(gpg, encrypted_message)
    
    # Criar uma resposta criptografada
    encrypted_reply = encrypt_message(gpg, 'Esta é uma resposta criptografada', 'robert@example.com')
    
    # Responder com a mensagem descriptografada e a resposta criptografada
    response = f'Mensagem descriptografada: {decrypted_message}\nMensagem criptografada para envio: {encrypted_reply}'
    update.message.reply_text(response)

# Configurar o bot
def main():
    gpg = configure_gpg()
    application = Application.builder().token("TOKEN-BOT").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
# %%
