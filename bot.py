import os
import re
import asyncio
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import base64
import urllib.parse
import concurrent.futures
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TelegramClient('asura_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
session = requests.Session()
COVER_IMAGE_URL = "https://i.ibb.co/Kzh0WxN7/poster.jpg"

async def download_cover_image():
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: session.get(COVER_IMAGE_URL, stream=True))
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.convert('RGB')
    except:
        return None

def decode_image_url(encoded_url):
    try:
        if 'asurascans.imagemanga.online' in encoded_url:
            encoded_part = encoded_url.split('/')[-2]
            url_decoded = urllib.parse.unquote(encoded_part)
            padding = len(url_decoded) % 4
            if padding:
                url_decoded += '=' * (4 - padding)
            decoded_bytes = base64.b64decode(url_decoded)
            return decoded_bytes.decode('utf-8')
        return encoded_url
    except:
        return None

async def get_chapter_info(chapter_url):
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: session.get(chapter_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': chapter_url
        }))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.select_one('.entry-title').text.split('Chapter')[0].strip()
        chapter_num = re.search(r'chapter-(\d+)', chapter_url).group(1)
        return title, chapter_num
    except:
        return None, None

async def get_chapter_images(chapter_url):
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: session.get(chapter_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': chapter_url
        }))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        for p_tag in soup.select('#readerarea p'):
            img_tag = p_tag.find('img')
            if img_tag:
                src = img_tag.get('src') or img_tag.get('data-src')
                if src and not src.startswith('data:image/svg+xml'):
                    if 'asurascans.imagemanga.online' in src:
                        decoded = decode_image_url(src)
                        if decoded and decoded.startswith('http'):
                            images.append(decoded)
                    elif src.startswith('http'):
                        images.append(src)
        return images
    except:
        return []

async def download_image(img_url, index):
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, lambda: session.get(img_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://asurascanz.com/'
        }, stream=True))
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return index, img.convert('RGB') if img.mode == 'RGBA' else img
    except:
        return index, None

async def create_pdf(title, chapter_num, images, temp_dir):
    output_path = os.path.join(temp_dir, f"[@AnimeZFlix] Chapter {chapter_num}.pdf")
    downloaded_images = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for idx, img_url in enumerate(images):
            futures.append(executor.submit(asyncio.run_coroutine_threadsafe, download_image(img_url, idx), asyncio.get_event_loop()))
            await asyncio.sleep(0.3)
        for future in concurrent.futures.as_completed(futures):
            idx, img = future.result().result()
            if img:
                downloaded_images.append((idx, img))
    if not downloaded_images:
        return None
    downloaded_images.sort(key=lambda x: x[0])
    sorted_images = [img for _, img in downloaded_images]
    try:
        sorted_images[0].save(output_path, "PDF", resolution=300.0, save_all=True, append_images=sorted_images[1:], quality=95)
        return output_path
    except:
        return None

async def send_pdf_with_thumbnail(chat_id, pdf_path, caption, thumb_image):
    try:
        thumb_bytes = BytesIO()
        thumb_image.thumbnail((320, 320))
        thumb_image.save(thumb_bytes, format='JPEG')
        thumb_bytes.seek(0)
        await bot.send_file(
            chat_id,
            pdf_path,
            caption=caption,
            force_document=True,
            thumb=thumb_bytes,
            attributes=[DocumentAttributeFilename(os.path.basename(pdf_path))]
        )
    except:
        pass

async def process_single_chapter(chapter_url, temp_dir, thumb_image):
    title, chapter_num = await get_chapter_info(chapter_url)
    if not title or not chapter_num:
        return None, "❌ Failed to extract chapter details"
    images = await get_chapter_images(chapter_url)
    if not images:
        return None, "❌ No images found"
    pdf_path = await create_pdf(title, chapter_num, images, temp_dir)
    if not pdf_path:
        return None, "❌ Failed to create PDF"
    caption = f"📚 {title} – Chapter {chapter_num}\n\nShared via @AnimeZFlix"
    return pdf_path, caption

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("""
🎭 *Asura Scans PDF Bot* 🎭

Send:
- A single chapter URL
- Or: `URL start_chapter end_chapter`

Examples:
`https://asurascanz.com/solo-leveling-chapter-1/`
`https://asurascanz.com/solo-leveling-chapter-1/ 1 10`
""", parse_mode='markdown')

@bot.on(events.NewMessage(pattern=r'(https?://asurascanz\.com/.*chapter-\d+/)(?:\s+(\d+)\s+(\d+))?'))
async def handle_chapter(event):
    try:
        temp_dir = "temp_pdfs_" + str(int(time.time()))
        os.makedirs(temp_dir, exist_ok=True)
        match = event.pattern_match
        base_url = match.group(1).strip()
        start_chapter = match.group(2)
        end_chapter = match.group(3)
        msg = await event.reply("⏳ Downloading thumbnail...")
        thumbnail = await download_cover_image()
        if not thumbnail:
            await msg.edit("❌ Failed to download thumbnail")
            return
        await msg.edit("✅ Thumbnail ready! Processing...")
        if start_chapter and end_chapter:
            for chapter_num in range(int(start_chapter), int(end_chapter) + 1):
                chapter_url = re.sub(r'chapter-\d+', f'chapter-{chapter_num}', base_url)
                pdf_path, caption = await process_single_chapter(chapter_url, temp_dir, thumbnail)
                if pdf_path:
                    await send_pdf_with_thumbnail(event.chat_id, pdf_path, caption, thumbnail)
                    os.remove(pdf_path)
                    await asyncio.sleep(1.5)
                else:
                    await event.reply(caption)
            await msg.edit("✅ All chapters processed and sent.")
        else:
            pdf_path, caption = await process_single_chapter(base_url, temp_dir, thumbnail)
            if pdf_path:
                await msg.edit("✅ PDF ready! Uploading...")
                await send_pdf_with_thumbnail(event.chat_id, pdf_path, caption, thumbnail)
                os.remove(pdf_path)
                await msg.delete()
            else:
                await msg.edit(caption)
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)
    except Exception as e:
        await event.reply(f"❌ Error: {e}")
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

print("Bot is running...")
bot.run_until_disconnected()
