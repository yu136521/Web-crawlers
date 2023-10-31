"""
Before that, enter these commands in the terminal:
pip install asyncio
pip install easygui
pip install aiofiles
pip install aiohttp
pip install requests
---------------------------------------------------------------------------------
The code is divided into three outlines (mainly using crawler technology)
1. Download Bilibili videos: Mainly use asynchronous crawlers, FFmpeg, asynchronous operations, etc
2. Download various rankings of NetEase Cloud Music: Mainly use asynchronous crawlers, network request analysis, programming in the face of objects, etc
3. User use: including error handling, better graphical UI, etc
---------------------------------------------------------------------------------
Steps to download the video of Bilibili
1. Get the main URL
2. Parse to obtain vedio_url and audio_url
3. Download video and audio asynchronously
4. Merge video and audio
---------------------------------------------------------------------------------
Steps to download NetEase Cloud Music
1. Get the main URL
2. Parse to get hyperlinks and merge interfaces
3. Make use of asynchronous operations for downloads
---------------------------------------------------------------------------------
Original: yu136521, Chinese name: 小瑀 Github:yu136521
"""
import asyncio
import json
import os
import re
from os import system

import aiofiles
import aiohttp
import easygui
import requests


class Climb_station_b:
    # Download Video Function (Asynchronous)
    @staticmethod
    async def aio_download_mp4(m_url, v_url, path_video):
        print("正在下载视频")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": m_url
        }
        # Define asynchronous sessions
        async with aiohttp.ClientSession() as session:
            # Asynchronous requests
            async with session.get(v_url, headers=headers) as resp:
                # Asynchronous downloads
                async with aiofiles.open(f"{path_video}/1.mp4", mode='wb') as f:
                    await f.write(await resp.content.read())
        print("视频下载完毕")

    # Download audio (asynchronous)
    @staticmethod
    async def aio_download_mp3(m_url, a_url, path_mp3):
        print("正在下载音频")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": m_url
        }
        # Same as the previous function
        async with aiohttp.ClientSession() as session:
            async with session.get(a_url, headers=headers) as resp:
                async with aiofiles.open(f"{path_mp3}/2.mp3", mode='wb') as f:
                    await f.write(await resp.content.read())
        print("音频下载完毕")

    # Audio and video merging functions
    @staticmethod
    def audio_and_video_merging(gen_path, audio_path, videopath, title):
        title = re.sub("[|]", " ", title)
        # The terminal is passed into the merge function
        system(
            f'ffmpeg -i {videopath} -i {audio_path} -c:v libx264 -c:v copy -c:a aac -c:a copy "{gen_path}/{title}.mp4"')

        # Delete temporary files
        os.remove(videopath)
        os.remove(audio_path)

    # Function Entrance
    @staticmethod
    async def main(main_url, main_path):
        try:
            # Path legal character optimization
            main_path = re.sub(r'[<>|"?*]', '', main_path)
            main_path = main_path.replace("\\", "/")
            # Request header
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            # Request URL
            resp = requests.get(main_url, headers=headers)
            # Regular expression parsing playinfo
            html_data = re.findall('<script>window.__playinfo__=(.*?)</script>', resp.text)[0]
            # JSONIZE the source code
            json_data = json.loads(html_data)
            # title
            title = re.findall('<h1 title="(?P<title>.*?)"', resp.text)[0]
            # Scrape data from dictionaries
            audio_info = json_data['data']['dash']['audio'][0]['backupUrl'][0]
            video_info = json_data['data']['dash']['video'][0]['base_url']
            # Passing references
            tasks = [
                asyncio.create_task(Climb_station_b.aio_download_mp4(main_url, video_info, main_path)),
                asyncio.create_task(Climb_station_b.aio_download_mp3(main_url, audio_info, main_path))
            ]
            await asyncio.wait(tasks)
            Climb_station_b.audio_and_video_merging(main_path, f"{main_path}/1.mp4", f"{main_path}/2.mp3", title)
        # Error handling
        except FileNotFoundError:
            easygui.msgbox(msg="没有找到目标文件，请核对路径后重试", title="提示(点击ok关闭对话框)")
        except requests.exceptions.MissingSchema:
            easygui.msgbox("请检查网址是否正确")
        except aiohttp.client_exceptions.ServerDisconnectedError:
            easygui.msgbox(msg='由于服务器积极拒绝请求，请求被迫断开，若有下载不全请重试', title='提示')


# In the face of the object instance---- grab the NetEase Cloud Music Chart
class Climb_music_biaosheng:
    def __init__(self):
        self.wjj = '飙升榜'
        if not os.path.exists(self.wjj):
            os.mkdir(self.wjj)
        self.murl = 'https://music.163.com/discover/toplist'
        # url='https://music.163.com/#/discover/toplist'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        }

    async def aiodownload(self, url, filename, session, music_name):
        async with session.get(url, headers=self.headers) as resp:
            music_content = await resp.content.read()
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(music_content)
        print(f"{music_name}, 下载完毕")

    async def main(self, url):
        tasks = []
        n = 0
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                infos = re.findall('<li><a href="/song\?id=(\d+)">(.*?)</a></li>', await resp.text())
                for info in infos:
                    n += 1
                    k = f'%d0{len(str(len(infos)))}d' % n
                    music_id = info[0]
                    music_name = info[1]
                    music_name = re.sub('[/:*?"<>|\n]', '', music_name)
                    # Music playback interface
                    music_url = f'http://music.163.com/song/media/outer/url?id={music_id}'
                    filename = f'{self.wjj}\\{k}、{music_name}.mp3'
                    print(filename, len(infos))
                    # Create an empty task list
                    tasks.append(asyncio.create_task(self.aiodownload(music_url, filename, session, music_name)))
                await asyncio.wait(tasks)


class Climb_music_xinge:
    def __init__(self):
        self.wjj = '新歌榜'
        if not os.path.exists(self.wjj):
            os.mkdir(self.wjj)
        self.url = 'https://music.163.com/discover/toplist?id=3779629'
        # url='https://music.163.com/#/discover/toplist?id=3779629'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        }

    async def aio_download(self, url, filename, session, music_name):
        async with session.get(url, headers=self.headers) as resp:
            music_content = await resp.content.read()
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(music_content)
        print(f"{music_name}, 下载完毕")

    async def main(self, url):
        n = 0
        tasks = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                infos = re.findall('<li><a href="/song\?id=(\d+)">(.*?)</a></li>', await resp.text())
                for info in infos:
                    n += 1
                    k = f'%d0{len(str(len(infos)))}d' % n
                    music_id = info[0]
                    music_name = info[1]
                    music_name = re.sub('[/:*?"<>|\n]', '', music_name)
                    # Music playback interface
                    music_url = f'http://music.163.com/song/media/outer/url?id={music_id}'
                    filename = f'{self.wjj}\\{k}、{music_name}.mp3'
                    print(filename, len(infos))
                    tasks.append(asyncio.create_task(self.aio_download(music_url, filename, session, music_name)))
                await asyncio.wait(tasks)


class Climb_music_rege:
    def __init__(self):
        self.wjj = '热歌榜'
        if not os.path.exists(self.wjj):
            os.mkdir(self.wjj)
        self.url = 'https://music.163.com/discover/toplist?id=3778678'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        }

    async def aio_download(self, url, filename, session, music_name):
        async with session.get(url, headers=self.headers) as resp:
            music_content = await resp.content.read()
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(music_content)
        print(f"{music_name}, 下载完毕")

    async def main(self, url):
        n = 0
        tasks = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                infos = re.findall('<li><a href="/song\?id=(\d+)">(.*?)</a></li>', await resp.text())
                for info in infos:
                    n += 1
                    k = f'%0{len(str(len(infos)))}d' % n
                    music_id = info[0]
                    music_name = info[1]
                    music_name = re.sub('[\\/:*?"<>|\n]', '', music_name)
                    # Music playback interface
                    music_url = f'http://music.163.com/song/media/outer/url?id={music_id}'
                    filename = f'{self.wjj}\\{k}、{music_name}.mp3'
                    print(filename, len(infos))
                    tasks.append(asyncio.create_task(self.aio_download(music_url, filename, session, music_name)))
                await asyncio.wait(tasks)


if __name__ == '__main__':
    # Agreement section
    user_choice = easygui.buttonbox(msg="《用户协议》\n本作品请勿用于违法行为", choices=["Yes", "No"], title='By.小瑀')
    if user_choice == "Yes":
        # Create a radio box
        choices = ["下载B站视频", "下载网易云音乐飙升榜", "下载网易云音乐新歌榜", "下载网易云音乐热歌榜"]
        selected_choice = easygui.choicebox(msg="请选择一个选项", choices=choices, title='By.小瑀')
        if selected_choice == "下载B站视频":
            easygui.msgbox(title="提示", msg='下载的视频小概率失败')
            while True:
                url = str(easygui.enterbox(msg="b站视频网址", title="下载B站"))
                path = str(easygui.enterbox(msg="下载视频的路径", title="下载B站"))
                if url is None or path is None:
                    easygui.msgbox(msg="您未正确输入数据，本程序自动退出", title="提示(选择ok键关闭)")
                    exit()
                climb_b = Climb_station_b()
                asyncio.run(climb_b.main(url, path))
                easygui.msgbox(msg="下载完成！", title="下载B站")
                user_choices = easygui.buttonbox("您是否还想继续下载视频", choices=["Yes", "No"])
                if user_choices == "Yes":
                    continue
                else:
                    easygui.msgbox("本程序即将退出(按ok关闭)")
                    break

        elif selected_choice == '下载网易云音乐飙升榜':
            try:
                easygui.msgbox(msg="点击ok下载文件，下载完成后(无报错情况)请在当前文件夹里找'飙升榜'文件夹", title='提示')
                climb_m = Climb_music_biaosheng()
                asyncio.run(climb_m.main('https://music.163.com/discover/toplist'))
                easygui.msgbox("下载完成")
            except aiohttp.client_exceptions.ServerDisconnectedError:
                easygui.msgbox(msg='由于服务器积极拒绝请求，请求被迫断开，若有下载不全请重试', title='提示')
                exit()
            except FileNotFoundError:
                easygui.msgbox(msg='文件路径出现错误，请检查路径', title='提示')
                exit()

        elif selected_choice == "下载网易云音乐新歌榜":
            try:
                easygui.msgbox(msg="点击ok下载文件，下载完成后(无报错情况)请在当前文件夹里找'新歌榜'文件夹",
                               title='提示')
                climb_m = Climb_music_xinge()
                asyncio.run(climb_m.main('https://music.163.com/discover/toplist?id=3779629'))
                easygui.msgbox("下载完成")
            except aiohttp.client_exceptions.ServerDisconnectedError:
                easygui.msgbox(msg='由于服务器积极拒绝请求，请求被迫断开，若有下载不全请重试', title='提示')
                exit()
            except FileNotFoundError:
                easygui.msgbox(msg='文件路径出现错误，请检查路径', title='提示')
                exit()

        elif selected_choice == "下载网易云音乐热歌榜":
            try:
                easygui.msgbox(msg="点击ok下载文件，下载完成后(无报错情况)请在当前文件夹里找'热歌榜'文件夹",
                               title='提示')
                climb_m = Climb_music_rege()
                asyncio.run(climb_m.main('https://music.163.com/discover/toplist?id=3778678'))
                easygui.msgbox("下载完成")
            except aiohttp.client_exceptions.ServerDisconnectedError:
                easygui.msgbox(msg='由于服务器积极拒绝请求，请求被迫断开，若有下载不全请重试', title='提示')
                exit()
            except FileNotFoundError:
                easygui.msgbox(msg='文件路径出现错误，请检查路径', title='提示')
                exit()

        else:
            easygui.msgbox("您已退出本程序，点击ok关闭", title='提示')
            exit()

    else:
        easygui.msgbox(msg='您拒绝本协议，请点击ok退出', title='提示')
