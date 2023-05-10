import json
from websocket import create_connection
from aiogram import Router, F
from aiogram.filters import Command, Text
from database.database import tokens_db
from keyboards.del_kb import del_keyboard
from keyboards.make_order_keyboards import yes_no_keyboard
from keyboards.make_order_keyboards import ask_bid_keyboard
from lexicon.lexicon import LEXICON
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from aiogram import Bot

from services.instrument_supported import instrument_supported
from services.pretty_look import order_pretty

router: Router = Router()


class FSMMakeOrder(StatesGroup):
    fill_instrument = State()
    fill_side_of_deal = State()
    fill_price = State()
    fill_amount = State()
    confirm = State()


@router.message(Command(commands="make_order"),
                F.from_user.id.in_(set(tokens_db.keys())))
async def start_make_order_form(message: Message, state: FSMContext):
    await message.delete()
    msg = await message.answer(text=LEXICON["fill_instrument"])
    form_msg_id, chat_id = msg.message_id, msg.chat.id
    await state.update_data(form_msg_id=form_msg_id, chat_id=chat_id)
    await state.set_state(FSMMakeOrder.fill_instrument)


@router.message(Command(commands="make_order"))
async def dont_login(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text=LEXICON["dont_login"],
                         reply_markup=del_keyboard())
    await state.set_state(default_state)


@router.message(instrument_supported,
                StateFilter(FSMMakeOrder.fill_instrument))
async def fill_instrument(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(instrument=message.text)
    await message.delete()
    text = LEXICON["fill_side_of_deal"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=form_msg_id,
        reply_markup=ask_bid_keyboard(),
    )
    await state.set_state(FSMMakeOrder.fill_side_of_deal)


@router.message(StateFilter(FSMMakeOrder.fill_instrument))
async def instrument_not_supported(message: Message,
                                   bot: Bot, state: FSMContext):
    await message.delete()
    text = LEXICON["instrument_not_supported"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(
        text=text, chat_id=chat_id, message_id=form_msg_id,
        reply_markup=del_keyboard()
    )


@router.callback_query(
    StateFilter(FSMMakeOrder.fill_side_of_deal), Text(text=["ask", "bid"])
)
async def fill_side_of_deal(callback: CallbackQuery, state: FSMContext):
    await state.update_data(side_of_deal=callback.data)
    text = LEXICON["fill_price"]
    if not callback.message:
        raise ValueError
    await callback.message.edit_text(text=text)
    await state.set_state(FSMMakeOrder.fill_price)


@router.message(StateFilter(FSMMakeOrder.fill_price), F.text.isdigit())
async def fill_price(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(price=message.text)
    await message.delete()
    text = LEXICON["fill_amount"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(text=text, chat_id=chat_id,
                                message_id=form_msg_id)
    await state.set_state(FSMMakeOrder.fill_amount)


@router.message(StateFilter(FSMMakeOrder.fill_price))
async def if_price_invalid(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    text = LEXICON["invalid_price"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(text=text, chat_id=chat_id,
                                message_id=form_msg_id)
    await state.set_state(FSMMakeOrder.fill_price)


@router.message(StateFilter(FSMMakeOrder.fill_amount), F.text.isdigit())
async def fill_amount(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(amount=message.text)
    await message.delete()
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    del order["form_msg_id"]
    del order["chat_id"]
    text = LEXICON["confirm"] + "\n\n" + order_pretty(order)
    await bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=form_msg_id,
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(FSMMakeOrder.confirm)


@router.message(StateFilter(FSMMakeOrder.fill_amount))
async def if_amount_invalid(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    text = LEXICON["invalid_amount"]
    order = await state.get_data()
    form_msg_id = order["form_msg_id"]
    chat_id = order["chat_id"]
    await bot.edit_message_text(text=text, chat_id=chat_id,
                                message_id=form_msg_id)
    await state.set_state(FSMMakeOrder.fill_amount)


@router.callback_query(StateFilter(FSMMakeOrder.confirm),
                       Text(text=["1", "0"]))
async def sending_an_order(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        raise ValueError
    if int(callback.data):
        token = tokens_db[callback.from_user.id]
        order = await state.get_data()
        del order["form_msg_id"]
        del order["chat_id"]
        instrument = order['instrument']
        ws = create_connection(
            f"ws://127.0.0.1:8000/ws/orderbox/{instrument}/?token={token}"
        )
        ws_message = json.dumps(order)
        ws.send(ws_message)
        if not callback.message:
            raise ValueError
        await callback.message.answer(
            text=LEXICON["order_accepted"], reply_markup=del_keyboard()
        )
        await callback.message.delete()
        return
    if not callback.message:
        raise ValueError
    await callback.message.answer(
        text=LEXICON["order_canceled"], reply_markup=del_keyboard()
    )
    await callback.message.delete()
