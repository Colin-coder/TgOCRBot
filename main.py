import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters
import os
from rapidocr_onnxruntime import RapidOCR
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def do_ocr(img_path):
    engine = RapidOCR()
    result, _ = engine(img_path, use_det=True, use_cls=False, use_rec=True)
    # 打印识别的文字模块个数为
    print("识别的文字模块个数为:", len(result))

    texts = []

    # 打印每个元素的值
    for element in result:
        texts.append(element[1])

    return '\n'.join(texts)

async def download_pic(update: Update):
    photo_file = await update.message.photo[-1].get_file()
    pic_name = f'abc.jpg'
    await photo_file.download_to_drive(pic_name)
    return pic_name

async def get_pic_ocr_texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = await download_pic(update)
    print(name)
    ocr_str = convert_to_telegram_supported_chars(name)
    # await context.bot.send_message(chat_id=context.job.chat_id,
    #                                 text=f"receive image succeed: {ocr_str}",
    #                                 parse_mode="MarkdownV2")
    await update.message.reply_text(f"receive image succeed: {ocr_str}")
    await update.message.reply_text(f"ocr succeed: {do_ocr(name)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("👋 直接发送图片来获取ocr结果",
                                    parse_mode="MarkdownV2")


async def start_boot(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text="🚀 *OCR启动中\.\.\.*",
                                   parse_mode="MarkdownV2")
    time.sleep(1)
    await context.bot.send_message(chat_id=context.job.chat_id, text="🎮 *OCR启动完成\!*",
                                   parse_mode="MarkdownV2")

# 替换特殊字符，适配tg发送消息的格式要求
SPECIAL_CHARS = [
    '\\',
    '_',
    '*',
    '[',
    ']',
    '(',
    ')',
    '~',
    '`',
    '>',
    '<',
    '&',
    '#',
    '+',
    '-',
    '=',
    '|',
    '{',
    '}',
    '.',
    '!'
]
def convert_to_telegram_supported_chars(input_string):
    for char in SPECIAL_CHARS:
        input_string = input_string.replace(char, f'\{char}')
    return input_string


def main() -> None:
    tg_api_token = os.getenv('TG_API_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    tg_api_base_url = os.getenv('TG_API_BASE_URL', 'https://api.telegram.org/bot')
    
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().connect_timeout(30).read_timeout(30).base_url(
        base_url=tg_api_base_url).token(tg_api_token).build()
    job_queue = application.job_queue
    job_queue.run_once(start_boot, chat_id=tg_chat_id, when=2)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(MessageHandler(filters.PHOTO, get_pic_ocr_texts))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
