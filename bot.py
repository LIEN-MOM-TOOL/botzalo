import json
import random
from datetime import datetime
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *
from colorama import Fore, Style, init
import os

# Initialize colorama
init(autoreset=True)

class CustomClient(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.excluded_user_ids = ['207754413506549669']
        self.data_file = 'user_data.json'
        self.message_counts = {}  # Track message counts
        self.load_data()

    def load_data(self):
        """Load user data and message counts from a JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.user_data = data.get('user_data', {})
                self.message_counts = data.get('message_counts', {})
        except FileNotFoundError:
            self.user_data = {}
            self.message_counts = {}
        except json.JSONDecodeError:
            self.user_data = {}
            self.message_counts = {}

    def save_data(self):
        """Save user data and message counts to a JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump({'user_data': self.user_data, 'message_counts': self.message_counts}, f, indent=4)

    def fetchUserInfo(self, userId):
        """Fetch user info and return zaloName or displayName."""
        try:
            user_info = super().fetchUserInfo(userId)
            if 'changed_profiles' in user_info and userId in user_info['changed_profiles']:
                zalo_name = user_info['changed_profiles'][userId].get('zaloName', None)
                if zalo_name:
                    return zalo_name
                else:
                    display_name = user_info['changed_profiles'][userId].get('displayName', userId)
                    return display_name
            else:
                return userId
        except Exception as e:
            print(f"{Fore.RED}Error fetching user info: {e}")
            return userId

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        """Process incoming messages and handle commands."""
        print(f"{Fore.GREEN}Received message:\n"
              "------------------------------\n"
              f"- **Message:** {message}\n"
              f"- **Author ID:** {author_id}\n"
              f"- **Thread ID:** {thread_id}\n"
              f"- **Thread Type:** {thread_type}\n"
              f"- **Message Object:** {message_object}\n"
              f"{Fore.GREEN}------------------------------\n")

        try:
            self.update_message_count(thread_id, author_id)

            self.handle_new_member(message_object, thread_id)  # Chức năng chào mừng thành viên mới

            self.handle_random_girl_video(message_object, thread_id)  # Lệnh video gái xinh

            self.handle_tool(message_object, thread_id)  # Lệnh /tool

            self.handle_member_leave(message_object, thread_id)  # Chức năng thành viên rời nhóm

            self.handle_ban_user(message_object, thread_id)  # Lệnh /cam

            self.handle_user_info(message_object, thread_id)  # Lệnh /thongtin

            self.handle_province(message_object, thread_id)  # Lệnh /23hg

            self.handle_random_girl_image(message_object, thread_id)  # Lệnh /anhgai

            self.handle_menu(message_object, thread_id)  # Lệnh /menu

        except Exception as ex:
            print(f"{Fore.RED}Error processing message: {ex}")

    def handle_new_member(self, message_object, thread_id):
        """Handle the new member joining the group."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if "joined the group" in message_object.content:
                user_id = message_object.author_id
                display_name = self.fetchUserInfo(user_id)
                current_time = datetime.now().strftime("%H:%M/%d/%m/%Y")
                total_members = len(self.fetchGroupInfo(groupId=thread_id).gridInfoMap[thread_id]['memberIds'])

                welcome_message = f"""
🍀Chào mừng @{display_name} đã tham gia nhóm 
🍀Chúc bạn chò chuyện vui vẻ 
🍀by: bot AMIN LIÊN MÕM 🇻🇳
🍀Chúc các thành viên một ngày vui vẻ 
🍀bạn là người thứ {total_members} đã tham gia nhóm
                """
                self.send(Message(text=welcome_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_random_girl_video(self, message_object, thread_id):
        """Xử lý lệnh gửi video gái xinh nhảy ngẫu nhiên."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/gaixinh'):
                GIRL_VIDEOS = [
                    "https://www.tiktok.com/@user1/video/1234567890123456789",
                    "https://www.tiktok.com/@user2/video/9876543210987654321",
                    "https://www.tiktok.com/@user3/video/1928374650918273645"
                ]
                try:
                    tiktok_url = random.choice(GIRL_VIDEOS)
                    download_url = self.get_tiktok_download_url(tiktok_url)
                    if not download_url:
                        self.send(
                            Message(text="Không thể tải video từ TikTok. Vui lòng thử lại sau!"),
                            thread_id=thread_id,
                            thread_type=ThreadType.GROUP
                        )
                        return

                    video_path = self.download_video(download_url)
                    with open(video_path, 'rb') as video_file:
                        self.send(
                            Message(file=video_file),
                            thread_id=thread_id,
                            thread_type=ThreadType.GROUP
                        )
                    os.remove(video_path)

                except Exception as e:
                    self.send(
                        Message(text="Đã xảy ra lỗi khi tải video. Vui lòng thử lại sau!"),
                        thread_id=thread_id,
                        thread_type=ThreadType.GROUP
                    )
                    print(f"{Fore.RED}Error handling random girl video: {e}")

    def handle_tool(self, message_object, thread_id):
        """Handle the /tool command to send tool link and image."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/tool'):
                tool_link = "<link tool>"
                tool_image = "<path_to_image>"
                tool_message = f"""
●Link tool: {tool_link}
●by decode: Liên'n Mõm'm 
●Ảnh tool:
                """
                self.send(Message(text=tool_message), thread_id=thread_id, thread_type=ThreadType.GROUP)
                with open(tool_image, 'rb') as img_file:
                    self.send(Message(file=img_file), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_member_leave(self, message_object, thread_id):
        """Thông báo khi thành viên rời nhóm."""
        if hasattr(message_object, 'content') and "left the group" in message_object.content:
            user_id = message_object.author_id
            display_name = self.fetchUserInfo(user_id)
            current_time = datetime.now().strftime("%H:%M/%d/%m/%Y")
            total_members = len(self.fetchGroupInfo(groupId=thread_id).gridInfoMap[thread_id]['memberIds'])

            leave_message = f"""
🍀Thành viên @{display_name} rời nhóm lúc {current_time}
🍀THÀNH THÀNH VIÊN CON LẠI TRONG NHÓM: {total_members}
            """
            self.send(Message(text=leave_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_ban_user(self, message_object, thread_id):
        """Xử lý lệnh /cam để cấm người dùng trò chuyện."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/cam'):
                user_name = message_object.content.split('@')[1]
                ban_time = 5  # Ban for 5 minutes
                ban_message = f"""
=================================
🍀NGƯỜI DÙNG @{user_name} ĐÃ BỊ CẤM CHO CHUYỆN {ban_time} PHÚT 
=================================
                """
                self.send(Message(text=ban_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_user_info(self, message_object, thread_id):
        """Xử lý lệnh /thongtin để lấy thông tin người dùng."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/thongtin'):
                user_name = message_object.content.split('@')[1]
                user_info_message = f"""
🍀TÊN: {user_name}
🍀SỐ DT: 123456789
🍀NĂM SINH: 2000
                """
                self.send(Message(text=user_info_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_province(self, message_object, thread_id):
        """Xử lý lệnh /23hg để nói về những điều hay của tỉnh đó."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/23hg'):
                province_message = f"""
🍀23 mãi đỉnh 
🍀23 hà giang Chào tất cả mọi người 
🍀❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️
                """
                self.send(Message(text=province_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_random_girl_image(self, message_object, thread_id):
        """Xử lý lệnh /anhgai để gửi ảnh gái xinh."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/anhgai'):
                GIRL_IMAGES = [
                    "<image_url1>",
                    "<image_url2>",
                    "<image_url3>"
                ]
                image_url = random.choice(GIRL_IMAGES)
                self.send(Message(text=image_url), thread_id=thread_id, thread_type=ThreadType.GROUP)

    def handle_menu(self, message_object, thread_id):
        """Xử lý lệnh /Menu để liệt kê tất cả các lệnh của bot."""
        if hasattr(message_object, 'content') and isinstance(message_object.content, str):
            if message_object.content.startswith('/menu'):
                menu_message = """
》》》》LỆNH BOT《《《
==>/tool
==>/thongtin
==>/gaixinh
==>/cam
==>/23hg
                """
                self.send(Message(text=menu_message), thread_id=thread_id, thread_type=ThreadType.GROUP)

# Usage
imei = "920fb18d-e2a3-4dd3-b862-223b2c9282c0-b78b4e2d6c0a362c418b145fe44ed73f"
session_cookies = ({"_ga":"GA1.2.925942728.1734692721","_gid":"GA1.2.867391880.1734692721","_gat":"1","ZConsent":"timestamp=1734692722907&location=https://zalo.me/pc","_ga_RYD7END4JE":"GS1.2.1734692721.1.1.1734692728.53.0.0","_zlang":"vn","zpsid":"9YTy.426330329.9.xm6CmOlhrg5Iex-uX-lMeVwOf9MvtUMIkzZacB5GdJou1OuyYcsPnEphrg4","zpw_sek":"9TE5.426330329.a0.4aEL27KLA4EiNK5QL1KeGmutJIXNBmeD94HzD2mbIYabKte95tjXAYzaQpOqA1LX22-J2EWcnXle5AuC478eGm","__zi":"3000.SSZzejyD0jydXQckra00a3BBfxQL71AQV8UZjDvJ5PXvXgdut5OVq7w8gFlONHdKCm.1","__zi-legacy":"3000.SSZzejyD0jydXQckra00a3BBfxQL71AQV8UZjDvJ5PXvXgdut5OVq7w8gFlONHdKCm.1","ozi":"2000.SSZzejyD0jydXQckra00a3BBfxQK71AQVOUaizzP49bvZgUzt1KJbdl6eBFT5XUTD3Cp.1","app.event.zalo.me":"7280909900899205763"})

client = CustomClient('api_key', 'secret_key', imei=imei, session_cookies=session_cookies)
client.listen()