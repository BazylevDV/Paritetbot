import logging
from aiogram import Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboards as kb
from app.email_utils import send_email
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramAPIError
import asyncio
from app.file_paths import FILE_PATHS, MIME_TYPES  # Импортируем переменные
import re  # Импортируем re для регулярных выражений
import os  # Импортируем os для работы с переменными окружения

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailRequest(StatesGroup):
    email = State()


def setup_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        main_menu = kb.get_main_menu()  # Используем функцию для получения клавиатуры
        await message.answer('Здравствуйте!', reply_markup=main_menu)
        await message.answer('Внизу выберите нужный пункт в меню. ✨')  # Добавляем сообщение

    @dp.message(F.text == "Каталог оборудования🗂️")
    async def catalog_handler(message: types.Message, state: FSMContext):
        await state.set_state(EmailRequest.email)
        await state.update_data(file_type="catalog")
        await message.answer("Введите адрес электронной почты вашей организации, чтобы получить каталог на оборудование📫 :")

    @dp.message(F.text == "Склад на сегодня💒")
    async def warehouse_handler(message: types.Message, state: FSMContext):
        await state.set_state(EmailRequest.email)
        await state.update_data(file_type="warehouse")
        await message.answer("Введите адрес электронной почты вашей организации, чтобы получить информацию о складе и ценах📫 :")

    @dp.message(F.text == "Успей купить по акции-1☎️")
    async def promo_handler_1(message: types.Message, state: FSMContext):
        await state.set_state(EmailRequest.email)
        await state.update_data(file_type="promo1")
        await message.answer("Введите адрес электронной почты вашей организации, чтобы получить инфу по первой промо-акции📫 :")

    @dp.message(F.text == "Успей купить по акции-2☎️")
    async def promo_handler_2(message: types.Message, state: FSMContext):
        await state.set_state(EmailRequest.email)
        await state.update_data(file_type="promo2")
        await message.answer("Введите Ваш адрес электронной почты, чтобы получить инфу по второй промо-акции📫 :")

    @dp.message(StateFilter(EmailRequest.email))
    async def process_email_request(message: types.Message, state: FSMContext):
        try:
            email = message.text
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):  # Проверка на корректный email
                await message.answer("Неверный формат email. Пожалуйста, попробуйте снова.")
                return
            await state.update_data(email=email)
            await state.set_state(None)  # Сбрасываем состояние
            await send_file(message, state)
            await send_and_clear_state(message, state)
        except Exception as e:
            logger.error(f"Ошибка при обработке email: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    async def send_and_clear_state(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            email = data.get("email")
            file_type = data.get("file_type", "unknown")  # Добавляем file_type

            # Формирование темы письма для пользователя
            subject_user = f"Ответ на Ваш запрос с информацией по {file_type} от компании Паритет."

            # Формирование тела письма для пользователя
            body_user = (
                """
                Филиал группы компаний 'Паритет',
                офис и склад : Челябинск, Постышева 2, 
                тел. (+7-351-274-40-17, 274-40-19, внутренние номера 120, 121, 107).
                """
            )

            # Отправка письма пользователю
            await send_email(email, subject_user, body_user, file_type)  # Передаем file_type
            logger.info(f"Email sent to {email} with subject: {subject_user}")
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")

        await message.answer("Выбрали оборудование? - жмите 'Запросить КП'. Остались вопросы, жмите 'Информация'. Благодарю🤝 !", reply_markup=kb.get_main_menu())
        await state.finish()

    @dp.message(F.text == "Информация📝")
    async def info_handler(message: types.Message):
        info_text = (
            "Представленная информация от бота по номенклатуре и ценам не является офертой, "
            "уточняйте у менеджеров напрямую по телефонам челябинского филиала группы компаний 'Паритет' "
            "по адресу Челябинск ул. Постышева д.2 офис 104, 101 городские номера: +7-351-274-40-17, "
            "351-274-40-19 (внутренние номера 120, 121 либо 107) либо дождитесь КП на указанную Вами почту."
        )
        await message.answer(info_text)

    async def send_file(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            email = data.get("email")
            file_type = data.get("file_type")

            # Получаем путь к файлу и его MIME-тип
            file_path = FILE_PATHS.get(file_type)
            mime_type = MIME_TYPES.get(file_type)

            if not file_path or not mime_type:
                await message.answer("Произошла ошибка при отправке файла. Пожалуйста, попробуйте снова.")
                return

            # Отправка файла пользователю
            file = FSInputFile(file_path)
            await message.answer_document(file)

            await message.answer(f"Файл отправлен на адрес {email}.")
        except TelegramAPIError as e:
            logger.error(f"Ошибка при отправке файла: {e}")
            await message.answer("Произошла ошибка при отправке файла. Пожалуйста, попробуйте снова.")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            await message.answer("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")

    # Добавляем таймер для напоминания пользователю о необходимости ввести данные
    async def remind_user(message: types.Message, state: FSMContext):
        await asyncio.sleep(60 * 5)  # 5 минут
        data = await state.get_data()
        if data.get("email") is None:
            await message.answer("Вы еще не ввели  рабочий адрес электронной почты. Хотите продолжить или завершить сеанс?")
            await message.answer("Выберите действие:", reply_markup=kb.reminder_keyboard())

    @dp.callback_query(F.data == "continue")
    async def continue_session(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.answer("Продолжаем сеанс. Введите адрес  электронной почты:")

    @dp.callback_query(F.data == "finish")
    async def finish_session(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await state.finish()
        await callback_query.message.answer("Сеанс завершен. Спасибо за использование бота!", reply_markup=kb.get_main_menu())

    # Запускаем таймер при переходе в состояние EmailRequest.email
    @dp.message(StateFilter(EmailRequest.email))
    async def start_reminder(message: types.Message, state: FSMContext):
        asyncio.create_task(remind_user(message, state))
        await asyncio.sleep(0)  # Чтобы избежать предупреждения о не ожидаемой корутине

    # Добавленный обработчик для команды /admin
    @dp.message(Command("admin"))
    async def admin_panel(message: types.Message):
        # Проверка на администратора
        if message.from_user.id == int(os.getenv("ADMIN_CHAT_ID")):
            await message.answer("Админ-панель", reply_markup=kb.admin_keyboard())
        else:
            await message.answer("У вас нет доступа к админ-панели.")