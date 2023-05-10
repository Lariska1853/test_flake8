from aiogram.filters import Text
from aiogram import Router
from aiogram.types import CallbackQuery

router: Router = Router()


@router.callback_query(Text(text="del"))
async def del_message(callback: CallbackQuery):
    if not callback.message:
        raise ValueError
    await callback.message.delete()
