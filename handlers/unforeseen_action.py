from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from keyboards.del_kb import del_keyboard
from lexicon.lexicon import LEXICON

router: Router = Router()


@router.message()
async def unforeseen_action(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text=LEXICON["unforeseen_action"],
                         reply_markup=del_keyboard())
    await state.clear()
