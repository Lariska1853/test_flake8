import json
import requests
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import tokens_db
from keyboards.del_kb import del_keyboard
from lexicon.lexicon import LEXICON
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram import Bot

router: Router = Router()


class FSMLogin(StatesGroup):
    fill_username = State()
    fill_password = State()


@router.message(Command(commands="login"), StateFilter(default_state))
async def process_login_command(message: Message, state: FSMContext):
    await message.delete()
    msg = await message.answer(text=LEXICON["fill_username"])
    form_msg_id, chat_id = msg.message_id, msg.chat.id
    await state.update_data(form_msg_id=form_msg_id, chat_id=chat_id)
    await state.set_state(FSMLogin.fill_username)


@router.message(StateFilter(FSMLogin.fill_username))
async def process_username_sent(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(username=message.text)
    await message.delete()
    text = LEXICON["fill_password"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(text=text, chat_id=chat_id,
                                message_id=form_msg_id)
    await state.set_state(FSMLogin.fill_password)


@router.message(StateFilter(FSMLogin.fill_password))
async def process_password_sent(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(password=message.text)
    await message.delete()
    state_data = await state.get_data()
    await state.clear()
    r = requests.post(
        "http://127.0.0.1:8000/token/login/",
        data={"username": state_data["username"],
              "password": state_data["password"]},
    )
    response_json = json.loads(r.text)
    form_msg_id = state_data["form_msg_id"]
    chat_id = state_data["chat_id"]
    if "auth_token" not in response_json:
        await bot.edit_message_text(
            text=LEXICON["wrong_credentials"],
            chat_id=chat_id,
            message_id=form_msg_id,
            reply_markup=del_keyboard(),
        )
        return
    token = response_json["auth_token"]
    if not message.from_user:
        raise ValueError
    tokens_db[message.from_user.id] = token
    text = LEXICON["logged_in"]
    await bot.edit_message_text(
        text=text, chat_id=chat_id, message_id=form_msg_id,
        reply_markup=del_keyboard()
    )
    await state.set_state(default_state)
