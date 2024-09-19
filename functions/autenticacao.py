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
