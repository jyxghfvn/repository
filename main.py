import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = ' '

MORSE_CODE = {
    'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.', 'Д': '-..',
    'Е': '.', 'Ё': '.', 'Ж': '...-', 'З': '--..', 'И': '..',
    'Й': '.---', 'К': '-.-', 'Л': '.-..', 'М': '--', 'Н': '-.',
    'О': '---', 'П': '.--.', 'Р': '.-.', 'С': '...', 'Т': '-',
    'У': '..-', 'Ф': '..-.', 'Х': '....', 'Ц': '-.-.', 'Ч': '---.',
    'Ш': '----', 'Щ': '--.-', 'Ъ': '--.--', 'Ы': '-.--', 'Ь': '-..-',
    'Э': '..-..', 'Ю': '..--', 'Я': '.-.-'
}

MORSE_CODE_REVERSE = {v: k for k, v in MORSE_CODE.items()}


def caesar_encrypt(text, shift=3):
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('А') if char.upper() >= '\u0410' and char.upper() <= '\u042F' else ord('а')
            offset = ord(char.upper()) - base
            new_char = chr((offset + shift) % 32 + base)
            if char.isupper():
                result += new_char.upper()
            else:
                result += new_char.lower()
        else:
            result += char
    return result


def caesar_decrypt(text, shift=3):
    return caesar_encrypt(text, -shift)

def text_to_morse(text):
    result = []
    for char in text.upper():
        if char == " ":
            result.append(" / ")
        elif char in MORSE_CODE:
            result.append(MORSE_CODE[char])
        else:
            pass
    return " ".join(result)


def morse_to_text(morse_code):
    words = morse_code.split(' / ')
    decoded_words = []
    for word in words:
        letters = word.strip().split()
        decoded_letters = []
        for letter in letters:
            decoded_letters.append(MORSE_CODE_REVERSE.get(letter, '?'))
        decoded_words.append(''.join(decoded_letters))
    return ' '.join(decoded_words)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я могу:\n"
        "/to_morse — перевод русского текста в азбуку Морзе\n"
        "/from_morse — перевод азбуки Морзе в русский\n"
        "/to_caesar — шифр Цезаря (сдвиг на 3)\n"
        "/from_caesar — дешифр шрифта Цезаря\n"
        "/cat — отправить котика!"
    )


async def to_morse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(' ')[2]
    if not text:
        await update.message.reply_text("Пожалуйста, отправьте текст после команды /to_morse")
        return
    morse = text_to_morse(text)
    await update.message.reply_text(morse)


async def from_morse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    morse_code = update.message.text.partition(' ')[2]
    if not morse_code:
        await update.message.reply_text("Пожалуйста, отправьте код Морзе после команды /from_morse")
        return
    text = morse_to_text(morse_code)
    await update.message.reply_text(text)


async def to_caesar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(' ')[2]
    if not text:
        await update.message.reply_text("Пожалуйста, отправьте текст после команды /to_caesar")
        return
    encrypted = caesar_encrypt(text)
    await update.message.reply_text(encrypted)


async def from_caesar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.partition(' ')[2]
    if not text:
        await update.message.reply_text("Пожалуйста, отправьте зашифрованный текст после команды /from_caesar")
        return
    decrypted = caesar_decrypt(text)
    await update.message.reply_text(decrypted)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()


    if all(c in ['.', '-', '/', ' '] for c in message_text):
        decoded_text = morse_to_text(message_text)
        await update.message.reply_text(f"Перевод из Морзе:\n{decoded_text}")

    elif all(c.isalpha() or c.isspace() for c in message_text):
        morse_code = text_to_morse(message_text)
        await update.message.reply_text(f"Азбука Морзе:\n{morse_code}")

    elif any(c.isalpha() for c in message_text):
        decrypted_caesar = caesar_decrypt(message_text)
        await update.message.reply_text(f"Дешифр шрифта Цезаря:\n{decrypted_caesar}")


async def send_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_gif_url = "https://gifer.com/ru/gifs/%D0%BA%D0%BE%D1%82%D1%8B"
    await update.message.bot.send_animation(chat_id=update.effective_chat.id, animation=cat_gif_url)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("to_morse", to_morse))
    app.add_handler(CommandHandler("from_morse", from_morse))
    app.add_handler(CommandHandler("to_caesar", to_caesar))
    app.add_handler(CommandHandler("from_caesar", from_caesar))
    app.add_handler(CommandHandler("cat", send_cat))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен")
    app.run_polling()


if __name__ == '__main__':
    main()