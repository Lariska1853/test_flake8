from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram import Router
from keyboards.del_kb import del_keyboard
from lexicon.lexicon import LEXICON

router: Router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_cancel_command_state(message: Message):
    await message.delete()
    await message.answer(text=LEXICON["start"], reply_markup=del_keyboard())
