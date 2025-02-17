import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_all_handlers
from config import TOKEN

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def main():
    """Запуск бота в режиме polling."""
    # Инициализация бота вне блока try-except
    bot = Bot(token=TOKEN)

    try:
        # Инициализация диспетчера
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация всех обработчиков
        register_all_handlers(dp)

        # Запуск polling
        logger.info("Бот запущен в режиме polling")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
    finally:
        # Закрываем сессию бота
        if bot is not None:
            await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())