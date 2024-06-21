import app.keyboards as kb
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from app.usernames import user_id_to_name
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.repositories import UserRepository
from dotenv import load_dotenv
from aiogram.filters.callback_data import CallbackData

load_dotenv()
router = Router()

@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    await UserRepository.add_user(user_id=message.from_user.id, username=message.from_user.username)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if await UserRepository.check_start_time(user_id=message.from_user.id, breakfast=False):
        await bot.send_message(chat_id=message.chat.id, text="Ты уже начал работу!", reply_markup=kb.main_keyboard_2)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if await UserRepository.check_user_info(user_id=message.from_user.id):
        await bot.send_message(chat_id=message.chat.id, text="Контроль времени работы приемной комиссии ИКНТ", reply_markup=kb.main_keyboard)
    else: await bot.send_message(chat_id=message.chat.id, text="Сегодняшнюю смену ты уже закрыл, приходи завтра!", reply_markup=kb.new_session)


# ----------------------------- Тестовый юзер --------------------------------- #
    # await UserRepository.add_user(user_id=123, username="Sanya")

    # await UserRepository.add_start_time(user_id=123, breakfast=False)

    # await UserRepository.add_start_time(user_id=123, breakfast=True)
    # await UserRepository.add_end_time(user_id=123, breakfast=True)
    # await UserRepository.add_start_time(user_id=123, breakfast=True)
    # await UserRepository.add_end_time(user_id=123, breakfast=True)

    # await UserRepository.add_end_time(user_id=123, breakfast=False)




@router.callback_query(lambda call: call.data == "start_working")
async def start_working(callback: CallbackQuery):
    await callback.message.answer(text="Ты начал работу!", reply_markup=kb.main_keyboard_2)
    await UserRepository.add_start_time(user_id=callback.from_user.id, breakfast=False)
    await callback.message.delete()


@router.callback_query(lambda call: call.data == "go_to_break" or call.data == "back_from_break")
async def breakfast(callback: CallbackQuery):
    new_keyboard = []
    if callback.data == "go_to_break":
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернулся с перерыва", callback_data="back_from_break")]
        ])
        await UserRepository.add_start_time(user_id=callback.from_user.id, breakfast=True)

    elif callback.data == "back_from_break":
        new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Я закончил работу", callback_data="end_working")],
            [InlineKeyboardButton(text="Ушел на перерыв", callback_data="go_to_break")]
        ])
        await UserRepository.add_end_time(user_id=callback.from_user.id, breakfast=True)

    await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    await callback.answer()

@router.callback_query(lambda call: call.data == "end_working")
async def end_working(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text="Вы уверены что хотите закрыть смену?", reply_markup=kb.success_keyboard)

@router.callback_query(lambda call: call.data == "success")
async def end_working_success(callback: CallbackQuery):
    await callback.message.answer(text="Ты закончил работу! До завтра!", reply_markup=kb.new_session)
    await UserRepository.add_end_time(user_id=callback.from_user.id, breakfast=False)
    await callback.message.delete()

@router.callback_query(lambda call: call.data == "fail")
async def start_working(callback: CallbackQuery):
    await callback.message.answer(text="Ты продолжил работу!", reply_markup=kb.main_keyboard_2)
    await callback.message.delete()

@router.callback_query(lambda call: call.data == "calendar")
async def calendar(callback: CallbackQuery):
    calendar_keyboard = await SimpleCalendar().start_calendar()
    await callback.message.answer(text="Выбери дату:", reply_markup=calendar_keyboard)

@router.callback_query(lambda call: call.data == "new_session")
async def new_session(callback: CallbackQuery):
    if await UserRepository.check_user_info(user_id=callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer(text="Контроль времени работы приемной комиссии ИКНТ", reply_markup=kb.main_keyboard)
    else: await callback.message.answer(text="Сегодняшнюю смену ты уже закрыл, приходи завтра!", reply_markup=kb.new_session)


# for admins

@router.message(Command("info"))
async def work_info(message: Message, bot: Bot):
    calendar_keyboard = await SimpleCalendar().start_calendar()
    await message.answer(text="Выбери дату:", reply_markup=calendar_keyboard)
from datetime import datetime, timedelta

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, bot: Bot):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        date_text = date.strftime("%d/%m/%Y")
        await callback_query.message.edit_text(parse_mode="HTML", text=f"Выбрана дата: <b>{date_text}</b>")
        data = await UserRepository.get_user_info_by_date(date)
        data.sort(key=lambda x: x.user_id)

        current_user_id = None
        response_message = ""

        for item in data:
            if item.user_id != current_user_id:
                if current_user_id is not None:
                    response_message += "\n➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖ ➖\n"
                current_user_id = item.user_id
                user_name = user_id_to_name.get(item.user_id, "Unknown")
                response_message += f'Секретарь <b>{user_name}</b>:\n'

                if item.timestamp_in is None:
                    start_time = "NULL"
                else:
                    main_time_in = item.timestamp_in
                    start_time = item.timestamp_in.strftime("%H:%M")

                if item.timestamp_out is None:
                    end_time = "NULL"
                    total_str_time = "NULL"
                else:
                    main_time_out = item.timestamp_out
                    end_time = item.timestamp_out.strftime("%H:%M")

                    # Рассчет затраченного времени
                    total_time = main_time_out - main_time_in
                    total_hours = total_time.days * 24 + total_time.seconds // 3600
                    total_minutes = (total_time.seconds // 60) % 60
                    total_str_time = f"{total_hours:02} часов {total_minutes:02} минут"

                response_message += f'Начал работу: <b>{start_time}</b>, закончил <b>{end_time}</b>\n'
                response_message += f"<i>Отработано <b>{total_str_time}</b></i>\n\n"
            else:
                if item.timestamp_in is None:
                    start_time = "NULL"
                else:
                    start_time = item.timestamp_in.strftime("%H:%M")

                if item.timestamp_out is None:
                    end_time = "NULL"
                else:
                    end_time = item.timestamp_out.strftime("%H:%M")
                response_message += f'Перерыв: <b>{start_time}</b> - <b>{end_time}</b>\n'



        if response_message:
            await bot.send_message(parse_mode="HTML", chat_id=callback_query.from_user.id, text=response_message, reply_markup=kb.keyboard_allow)
        else:
            calendar_keyboard = await SimpleCalendar().start_calendar()
            await bot.send_message(parse_mode="HTML", chat_id=callback_query.from_user.id, text="Данных нет", reply_markup=calendar_keyboard)