from websockets.legacy.client import connect
from aiogram import Router
from aiogram.filters import Command, CommandObject
from keyboards.del_kb import del_keyboard
from lexicon.lexicon import LEXICON
from aiogram.types import Message
from aiogram import Bot
from services.instrument_supported import instrument_supported
from services.pretty_look import quote_pretty

router: Router = Router()


@router.message(Command(commands="quote"),
                lambda msg: len(msg.text.split()) == 2)
async def view_quote(message: Message, bot: Bot, command: CommandObject):
    await message.delete()
    instrument = command.args or ''

    if not instrument_supported(instrument):
        await message.answer(
            text=LEXICON["instrument_not_supported"],
            reply_markup=del_keyboard()
        )
        return

    url = f"ws://127.0.0.1:8000/ws/orderbox/{instrument}/"

    async with connect(url) as ws:
        quote = await ws.recv()
        quote = quote_pretty(quote, instrument)
        quote_ms = await message.answer(text=quote,
                                        reply_markup=del_keyboard())
        ms_id, ct_id = quote_ms.message_id, quote_ms.chat.id
        ms_text = quote_ms.text

        while True:
            quote = await ws.recv()
            quote = quote_pretty(quote, instrument)
            if quote != ms_text:
                await bot.edit_message_text(
                    text=quote,
                    chat_id=ct_id,
                    message_id=ms_id,
                    reply_markup=del_keyboard(),
                )
                ms_text = quote


@router.message(Command(commands="quote"))
async def instrument_not_supported(message: Message):
    await message.delete()
    await message.answer(text=LEXICON["no_instrument"],
                         reply_markup=del_keyboard())
