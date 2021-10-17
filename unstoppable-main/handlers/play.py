import os
from os import path
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from callsmusic import callsmusic, queues
from callsmusic.callsmusic import client as USER
from helpers.admins import get_administrators
import requests
import aiohttp
import yt_dlp
from youtube_search import YoutubeSearch
import converter
from downloaders import youtube
from config import DURATION_LIMIT
from helpers.filters import command
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
import aiofiles
import ffmpeg
from PIL import Image, ImageFont, ImageDraw


def transcode(filename):
    ffmpeg.input(filename).output("input.raw", format='s16le', acodec='pcm_s16le', ac=2, ar='48k').overwrite_output().run() 
    os.remove(filename)

# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 18000)
    seconds %= 18000
    minutes = seconds // 300
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"ᴛɪᴛʟᴇ: {title}", (400, 255, 255), font=font)
    draw.text(
        (190, 590), f"ᴅᴜʀᴀᴛɪᴏɴ: {duration}", (400, 255, 255), font=font
    )
   
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")




@Client.on_message(command("play") 
                   & filters.group
                   & ~filters.edited 
                   & ~filters.forwarded
                   & ~filters.via_bot)
async def play(_, message: Message):

    lel = await message.reply("Processing...")
    
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "BG Assistant"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Promote me as admin in your group!</b>")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "♫︎ Woohoo , I have joined Here to Play Songs for [you](tg://settings) on VoiceChat! 🦋")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"✋ Flood Wait Error! 🦋 Userbot is Unable to join the Group.\nMake sure that my Userbot is Not Banned in your Group!⚡️")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"🤦🏻‍♀️ My Music Player Assistant is not Here.\nPlease allow me to invite my Assistant Player by Sending /play or /userbotjoin. 🦋")
        return
    
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 300) > DURATION_LIMIT:
            raise DurationLimitError(
                f"⚡️ Unable to play video more than {DURATION_LIMIT} 😞"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/46c460685ec153d93e3cf.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 300)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ᴄʜᴀɴɴᴇʟ",
                        url="https://t.me/BG_NEWS")
                   
                ]
            ]
        )
        
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")
            
            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 300
                
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=" ϟ ʏᴏᴜᴛᴜʙᴇ ϟ",
                            url=f"{url}"),
                        InlineKeyboardButton(
                            text=" ϟ sᴜᴘᴘᴏʀᴛ ϟ ",
                            url=f"http://t.me/desk_bg")

                    ]
                ]
            )
        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/46c460685ec153d93e3cf.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ʏᴏᴜᴛᴜʙᴇ",
                                url=f"https://youtube.com")

                        ]
                    ]
                )
        if (dur / 300) > DURATION_LIMIT:
             await lel.edit(f"⚡️ Unable to play video more than {DURATION_LIMIT} 😞")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)     
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit("🥱 **Please specify song Name! 😏**")
        await lel.edit("🔎 **🔥Finding The Song! **")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit(" **💕 Making Thumbnail**")
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
                
        except Exception as e:
            await lel.edit(
                "🥺 Song Not Found! Please Recheck Song_Name!"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
                [   
             
                    [
        InlineKeyboardButton(
            text="sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="http://t.me/desk_bg"),
    ],
    
    [
        InlineKeyboardButton(
            text="⧐ ʏᴏᴜᴛᴜʙᴇ ⧏", url=f"{url}"
        ),
        InlineKeyboardButton(text="⧐ ᴅᴏᴡɴʟᴏᴀᴅ ⧏",url=f"{durl}"),
    ],
                    
                 
                ]
            
        
        if (dur / 300) > DURATION_LIMIT:
             await lel.edit(f"⚡️ Unable to play video more than {DURATION_LIMIT} 😞")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(youtube.download(url))
  
    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
        photo="final.png", 
        caption="**♫︎ 𝖲𝗈𝗇𝗀 : {}\n❔𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇 : {} min\n💕 𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝖾𝖽 𝖻𝗒 : {}\n𝖯𝗈𝗌𝗂𝗍𝗂𝗈𝗇 : {}\n\n[@ᴛᴇᴀᴍʙᴀʙʏɢɪʀʟ](http://t.me/desk_bg)".format(
        title, duration, message.from_user.mention(), ροѕιτιοи
        ),
        reply_markup=keyboard)
        os.remove("final.png")
        return await lel.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
        photo="final.png",
        reply_markup=keyboard,
        caption="**♫︎ 𝖲𝗈𝗇𝗀 : {}\n❔𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇 : {} min\n💕 𝖱𝖾𝗊𝗎𝖾𝗌𝗍𝖾𝖽 𝖻𝗒 : {}\n\n[@ᴛᴇᴀᴍʙᴀʙʏɢɪʀʟ](http://t.me/desk_bg)**".format(
        title, duration, message.from_user.mention()
        ), )
        os.remove("final.png")
        return await lel.delete()
