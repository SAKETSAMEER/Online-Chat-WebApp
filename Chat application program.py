import flet as ft
from datetime import datetime

class Message():
    def __init__(self, user_name: str, text: str, message_type: str, avatar: str = None):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.avatar = avatar
        self.timestamp = datetime.now().strftime("%H:%M")

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        avatar_content = ft.Image(src=message.avatar, width=40, height=40) if message.avatar else ft.CircleAvatar(
            content=ft.Text(self.get_initials(message.user_name)),
            color=ft.colors.WHITE,
            bgcolor=self.get_avatar_color(message.user_name),
        )

        self.controls = [
            avatar_content,
            ft.Column(
                [
                    ft.Row([
                        ft.Text(message.user_name, weight="bold"),
                        ft.Text(message.timestamp, size=10, color=ft.colors.GREY),
                    ], spacing=10),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "?"  # Fallback to "?" if None

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)] if user_name else ft.colors.GREY

def main(page: ft.Page):
    page.horizontal_alignment = "stretch"
    page.title = "Flet Chat"
    online_users = {}

    avatar_options = [
        "https://via.placeholder.com/40/FF5733/FFFFFF?text=A",
        "https://via.placeholder.com/40/33FF57/FFFFFF?text=B",
        "https://via.placeholder.com/40/3357FF/FFFFFF?text=C",
        "https://via.placeholder.com/40/FF33A6/FFFFFF?text=D",
    ]

    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        elif not avatar_selector.value:
            join_user_name.error_text = "Please select an avatar!"
            join_user_name.update()
        else:
            user_name = join_user_name.value
            avatar = avatar_options[int(avatar_selector.value)]
            page.session.set("user_name", user_name)
            page.session.set("avatar", avatar)
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user_name}: ")
            online_users[user_name] = avatar
            update_online_status()
            page.pubsub.send_all(Message(user_name=user_name, text=f"{user_name} has joined the chat.", message_type="login_message", avatar=avatar))
            page.update()

    def send_message_click(e):
        if new_message.value.strip() != "":
            message = Message(
                user_name=page.session.get("user_name"),
                text=new_message.value.strip(),
                message_type="chat_message",
                avatar=page.session.get("avatar")
            )
            page.pubsub.send_all(message)
            new_message.value = ""
            new_message.focus()
            page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
            chat.controls.append(m)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
            chat.controls.append(m)
        chat.update()

    def update_online_status():
        online_list.controls = [
            ft.Row([
                ft.Image(src=avatar, width=20, height=20),
                ft.Text(user, color=ft.colors.GREEN),
            ], spacing=5)
            for user, avatar in online_users.items()
        ]
        online_list.update()

    def change_avatar_click(e):
        page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Change Avatar"),
            content=ft.Dropdown(
                label="Select new avatar",
                options=[ft.dropdown.Option(str(i), text=f"Avatar {i+1}") for i in range(4)],
                on_change=lambda ev: update_avatar(int(ev.control.value))
            ),
            actions=[ft.ElevatedButton(text="Close", on_click=lambda _: setattr(page.dialog, 'open', False))],
            actions_alignment="end",
        )
        page.update()

    def update_avatar(avatar_index):
        new_avatar = avatar_options[avatar_index]
        page.session.set("avatar", new_avatar)
        online_users[page.session.get("user_name")] = new_avatar
        update_online_status()
        page.dialog.open = False
        page.update()

    page.pubsub.subscribe(on_message)

    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
    )

    avatar_selector = ft.Dropdown(
        label="Select your avatar",
        options=[ft.dropdown.Option(str(i), text=f"Avatar {i+1}") for i in range(4)],
    )

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name, avatar_selector], width=300, height=150, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment="end",
    )

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    online_list = ft.Column(
        [ft.Text("Online Users", weight="bold")],
        spacing=5,
    )

    page.add(
        ft.Row([
            ft.Container(
                content=chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Container(
                content=online_list,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                width=150,
            ),
        ], expand=True),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
                ft.IconButton(
                    icon=ft.icons.PERSON,
                    tooltip="Change Avatar",
                    on_click=change_avatar_click,
                ),
            ]
        ),
    )

ft.app(port=8550, target=main, view=ft.WEB_BROWSER)
