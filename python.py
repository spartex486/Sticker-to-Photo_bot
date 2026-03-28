import io # Модуль для создания "виртуальных файлов" в оперативной памяти
import keyboards as main_kb # Твои кнопки
from aiogram.filters import CommandStart  
from aiogram import Router, F, types, Bot 
from PIL import Image # Движок для работы с пикселями (изменение размера, формата)
from states import Form  # Класс с состояниями (waiting_for_photo и т.д.)
from aiogram.fsm.context import FSMContext # Инструмент для управления состояниями юзера
router = Router() 

# --- СТАРТ ---
@router.message(CommandStart()) 
async def first_message(message: types.Message): 
    # Приветствуем и отправляем главное меню из keyboards.py
    await message.answer("Привет! Я бот по изменению формата фотографий/стикеров", reply_markup=main_kb.main_kb) 

# ==========================================
# --- РЕЖИМ 1: ФОТО В СТИКЕР ---
# ==========================================

# 1. Ловим нажатие кнопки "Фото в Стикер"
@router.message(F.text == "Фото в Стикер") 
async def start_photo_mode(message: types.Message, state: FSMContext): 
    # Включаем режим ожидания фото (FSM)
    await state.set_state(Form.waiting_for_photo) 
    await message.answer("Режим «Фото -> Стикер» включен! Присылай ФОТО 🖼") 

# 2. Обработка присланного фото
@router.message(Form.waiting_for_photo, F.photo) 
async def process_photo_to_sticker(message: types.Message, state: FSMContext, bot: Bot): 
    await message.answer("Делаю стикер... ⏳")
    
    # Достаем ID самого качественного фото (последнее в списке)
    photo = message.photo[-1] 
    # Получаем путь к файлу на сервере Telegram
    file_info = await bot.get_file(photo.file_id)
    # Скачиваем байты файла в оперативную память (BytesIO)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    # --- МАГИЯ PILLOW (Создаем правильный стикер) ---
    image = Image.open(downloaded_file) # Открываем скачанные байты как картинку
    
    # Уменьшаем до 480px, чтобы оставить пустые поля (защита от скругления углов)
    image.thumbnail((480, 480))
    
    # Создаем прозрачный квадрат-подложку 512x512 (требование Telegram)
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    
    # Вычисляем центр и "клеим" наше фото на прозрачный квадрат
    x = (512 - image.width) // 2
    y = (512 - image.height) // 2
    canvas.paste(image, (x, y))
    
    # Сохраняем результат в "виртуальный файл" в формате WEBP
    output = io.BytesIO()
    canvas.save(output, format="WEBP")
    output.seek(0) # Перематываем "курсор" в начало файла для чтения ботом
    
    # Отправляем готовый стикер пользователю
    await message.answer_sticker(types.BufferedInputFile(output.read(), filename="sticker.webp"))
    # Выключаем режим ожидания фото (очищаем состояние)
    await state.clear() 
    await message.answer("Готово! Возвращаюсь в главное меню.", reply_markup=main_kb.main_kb)

# ==========================================
# --- РЕЖИМ 2: СТИКЕР В ФОТО ---
# ==========================================

# 1. Ловим нажатие кнопки "Стикер в фото"
@router.message(F.text == "Стикер в фото")
async def start_sticker_mode(message: types.Message, state: FSMContext):
    # Включаем режим ожидания стикера
    await state.set_state(Form.waiting_for_sticker)
    await message.answer("Режим «Стикер -> Фото» включен! Присылай СТИКЕР 🎭")

# 2. Обработка присланного стикера
@router.message(Form.waiting_for_sticker, F.sticker)
async def process_sticker_to_photo(message: types.Message, state: FSMContext, bot: Bot):
    await message.answer("Превращаю в фото... 🪄")
    
    # Получаем и скачиваем стикер аналогично фото
    file_info = await bot.get_file(message.sticker.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    image = Image.open(downloaded_file)
    
    # Если стикер прозрачный (RGBA), переводим в RGB, иначе нельзя сохранить в JPEG
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    output = io.BytesIO()
    image.save(output, format="JPEG") # Конвертируем в обычное фото
    output.seek(0)
    
    # Отправляем результат как обычную фотографию
    await message.answer_photo(types.BufferedInputFile(output.read(), filename="photo.jpg"))
    # Очищаем состояние юзера
    await state.clear() 
    await message.answer("Вот твое фото! Возвращаюсь в главное меню.", reply_markup=main_kb.main_kb)
