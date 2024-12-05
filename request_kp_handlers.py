import logging
from aiogram import Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboards as kb
from app.email_utils import send_email
import asyncio
from app.file_paths import FILE_PATHS, MIME_TYPES  # Импортируем переменные
import re  # Импортируем re для регулярных выражений
from db import create_connection, create_request  # Импортируем функции для работы с базой данных


# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Email(StatesGroup):
    email = State()
    organization = State()
    equipment = State()
    phone = State()
    manager = State()


def setup_request_kp_handlers(dp: Dispatcher):
    @dp.message(F.text == "Запросить КП🖊️")
    async def request_kp_handler(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            await message.answer("Вы уже начали заполнять заявку. Хотите продолжить или начать заново?", reply_markup=kb.restart_keyboard())
        else:
            logger.info("Запрос на КП получен")
            await state.set_state(Email.email)  # Переход в состояние для ввода адреса электронной почты
            await message.answer("Введите адрес электронной почты вашей организации:", reply_markup=kb.back_keyboard())

    @dp.callback_query(F.data == "continue_kp")
    async def continue_kp_handler(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        current_state = await state.get_state()
        if current_state == Email.email:
            await callback_query.message.answer("Продолжаем заполнение. Введите адрес электронной почты вашей организации:")
        elif current_state == Email.organization:
            await callback_query.message.answer("Продолжаем заполнение. Напишите кратко название Вашей организации:")
        elif current_state == Email.equipment:
            await callback_query.message.answer("Продолжаем заполнение. Укажите оборудование, которое Вас заинтересовало:")
        elif current_state == Email.phone:
            await callback_query.message.answer("Продолжаем заполнение. Введите пожалуйста номер вашего рабочего телефона для связи:")
        elif current_state == Email.manager:
            await callback_query.message.answer("Продолжаем заполнение. Выберите менеджера:", reply_markup=kb.manager_keyboard())

    @dp.callback_query(F.data == "restart_kp")
    async def restart_kp_handler(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await state.set_state(Email.email)
        await callback_query.message.answer("Начинаем заполнение заявки заново. Введите адрес электронной почты вашей организации:")

    @dp.message(StateFilter(Email.email))
    async def process_email(message: types.Message, state: FSMContext):
        try:
            email = message.text
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):  # Проверка на корректный email
                await message.answer("Неверный формат email. Пожалуйста, попробуйте снова.")
                return
            await state.update_data(email=email)
            await state.set_state(Email.organization)  # Переход в состояние для ввода названия организации
            await message.answer("Укажите кратко название Вашей организации:👇", reply_markup=kb.back_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при обработке email: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    @dp.message(StateFilter(Email.organization))
    async def process_organization(message: types.Message, state: FSMContext):
        try:
            organization = message.text
            if not organization.strip():  # Проверка на пустоту
                await message.answer("Название организации не может быть пустым. Пожалуйста, попробуйте снова.")
                return
            await state.update_data(organization=organization)
            await state.set_state(Email.equipment)  # Переход в состояние для ввода вида оборудования
            await message.answer("Укажите оборудование, которое Вас заинтересовало, добавьте его краткое описание. Не более 120 знаков:✍️ ", reply_markup=kb.back_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при обработке организации: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.💁‍♂️ ")

    @dp.message(StateFilter(Email.equipment))
    async def process_equipment(message: types.Message, state: FSMContext):
        try:
            equipment = message.text
            if not equipment.strip() or len(equipment) > 120:  # Проверка на пустоту и ограничение на 120 знаков
                await message.answer("Наименование оборудования и описание не могут быть пустыми и должны быть не более 120 знаков. Пожалуйста, попробуйте снова.")
                return
            await state.update_data(equipment=equipment)
            await state.set_state(Email.phone)  # Переход в состояние для ввода номера телефона
            await message.answer("Введите пожалуйста номер вашего рабочего телефона для связи,💁‍♂️ пример: +7(351)3232623", reply_markup=kb.back_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при обработке оборудования: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    @dp.message(StateFilter(Email.phone))
    async def process_phone(message: types.Message, state: FSMContext):
        try:
            phone = message.text
            if not re.match(r'^\+\d+\(\d+\)\d{4,8}$|^\+\d{11,}$', phone):  # Проверка на корректный номер телефона
                await message.answer("Неверный формат телефона. Пожалуйста, попробуйте снова,💁‍♂️ пример: +7(351)3232623.")
                return
            await state.update_data(phone=phone)
            await state.set_state(Email.manager)  # Переход в состояние для выбора менеджера
            await message.answer("Выберите менеджера:", reply_markup=kb.manager_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при обработке телефона: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    @dp.callback_query(F.data.in_(["Дружинина Татьяна", "Ковач Александр"]), StateFilter(Email.manager))
    async def process_manager_choice(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            await callback_query.answer()
            manager = callback_query.data
            await state.update_data(manager=manager)
            await send_and_clear_state(callback_query.message, state)
            await callback_query.message.answer("Ваш запрос получен, менеджер в ближайшее время свяжется с Вами.")
            await callback_query.message.answer("Ознакомьтесь с нашими уникальными предложениями для лабораторной диагностики на @LabDealsBot", reply_markup=kb.subscribe_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора менеджера: {e}")
            await callback_query.message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    @dp.callback_query(F.data == "back")
    async def process_back(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            await callback_query.answer()
            await state.set_state(None)  # Сбрасываем состояние
            await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=kb.get_main_menu())
        except Exception as e:
            logger.error(f"Ошибка при обработке кнопки 'Назад': {e}")
            await callback_query.message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

    async def send_and_clear_state(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            email = data.get("email")
            organization = data.get("organization")
            equipment = data.get("equipment")
            phone = data.get("phone")
            manager = data.get("manager")

            # Формирование темы письма для менеджеров
            subject_manager = "Запрос на получение КП на оборудование от Paritetbot"

            # Формирование тела письма для менеджеров
            body_manager = (
                "Данные пользователя бота Paritetbot, который запросил КП:\n"
                f"Адрес электронной почты: {email}\n"
                f"Название организации: {organization}\n"
                f"Вид оборудования: {equipment}\n"
                f"Номер телефона: {phone}\n"
                f"Менеджер: {manager}\n"
                "\n"
                "С уважением,\n"
                "Команда Paritetbot\n"
                "Контакты: dmbazylev@gmail.com\n"
            )

            # Определение адреса для отправки письма
            if manager == "Дружинина Татьяна":
                recipient = "paritet121.0@gmail.com"
            elif manager == "Ковач Александр":
                recipient = "lab_paritet@mail.ru"
            else:
                recipient = "dmbazylev@ya.ru"

            # Отправка письма на указанный адрес
            await send_email(recipient, subject_manager, body_manager, None)  # Передаем None для file_type
            logger.info(f"Email sent to {recipient} with subject: {subject_manager}")

            # Отправка копии письма на ваш адрес
            await send_email("dmbazylev@ya.ru", subject_manager, body_manager, None)  # Передаем None для file_type
            logger.info(f"Email sent to dmbazylev@ya.ru with subject: {subject_manager}")

            # Сохранение данных в базу данных
            database = "database.db"
            conn = create_connection(database)
            if conn is not None:
                request = (organization, email, phone)
                create_request(conn, request)
            else:
                logger.error("Ошибка! Невозможно создать соединение с базой данных.")

            await state.finish()
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
            await message.answer("Произошла ошибка при отправке письма. Пожалуйста, попробуйте снова.")

    # Добавляем таймер для напоминания пользователю о необходимости ввести данные
    async def remind_user(message: types.Message, state: FSMContext):
        await asyncio.sleep(60 * 1)  # 1 минут
        data = await state.get_data()
        if data.get("email") is None:
            await message.answer("Вы еще не ввели адрес электронной почты. Хотите продолжить или завершить сеанс?")
            await message.answer("Выберите действие:", reply_markup=kb.reminder_keyboard())

    @dp.callback_query(F.data == "continue")
    async def continue_session(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.answer("Продолжаем сеанс. Введите адрес электронной почты вашей организации:")

    @dp.callback_query(F.data == "finish")
    async def finish_session(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await state.finish()
        await callback_query.message.answer("Сеанс завершен. Спасибо за использование бота!", reply_markup=kb.get_main_menu())

    # Запускаем таймер при переходе в состояние Email.email
    @dp.message(StateFilter(Email.email))
    async def start_reminder(message: types.Message, state: FSMContext):
        asyncio.create_task(remind_user(message, state))
        await asyncio.sleep(0)