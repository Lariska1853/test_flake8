from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from keyboards.del_kb import del_keyboard
from lexicon.lexicon import LEXICON

router: Router = Router()


@router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text=LEXICON["cancel"], reply_markup=del_keyboard())
    await state.clear()
