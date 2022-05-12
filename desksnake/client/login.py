import random, time
import deskapp
from deskserver import ClientSession
from desksnake.client import Show, ShowAI

ClassID = random.random()
class Login(deskapp.Module):
    name = "Login"

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.classID = ClassID
        self.scroll = 3
        self.elements = ['Login', 'Exit']
        self.index = 1  # Verticle Print Position
        self.result_message = "Result: Not yet Logged in..."
        self.server_host = 'localhost'
        # self.server_host = 'ruckusist.com'
        self.username = 'SnakeUser'
        self.password = 'SnakePass'
        self.pass_len = 0
        self.client = ClientSession(VERBOSE=False)
        # LAST THING!
        self.register_module()

    def string_decider(self, panel, string_input):
        if self.scroll == 0:  # on the server selection
            self.server_host = string_input
        if self.scroll == 1:  # on the username selection
            self.username = string_input
        elif self.scroll == 2:  # on the password selection
            self.pass_len = len(string_input)
            self.password = string_input
        else:
            self.context['text_input'] = string_input

    def page(self, panel):
        self.index = 1  # reset this to the top of the box every round
        panel.addstr(self.index, 4, "    Login to play DeskSnakes!",
                     self.frontend.chess_white)
        self.index += 2

        self.scroll_elements = [
            f"Server: {self.server_host}",
            f"Username: {self.username}",
            f"Password: {'*'*self.pass_len}",
            "Login",
            "Exit",
        ]

        for index, element in enumerate(self.scroll_elements):
            color = self.frontend.chess_white if index is not self.scroll else self.frontend.color_rw
            panel.addstr(self.index, 4, element, color)
            self.index += 1

        self.index += 2  # increment the Verticle Print Position

        panel.addstr(self.index, 4, f"{self.context['text_output']}",
                     self.frontend.chess_white)
        self.index += 1
        return False

    def login(self) -> bool:
        failed = 0
        success = 0
        while True:
            time.sleep(.1)
            if failed >= 2: break
            if success: break
            if not self.client.connected:
                connected = self.client.connect()
                if not connected: 
                    failed += 1
                    time.sleep(.5)
                continue
            
            if not self.client.logged_in:
                if not self.username and not self.password:
                    self.context['text_output'] = f"Please Enter Username and Password"
                    break
                self.client.login(self.username, self.password)
                time.sleep(.1)
                continue
            
            success = True
        # successful login.
        self.app.data['server_host'] = self.server_host
        self.client.username = self.username
        self.app.data['client'] = {
            'client': self.client,
            'username': self.username,
        }
        try:
            self.app.logic.setup_panel(Show(self.app))
        except Exception as e:
            self.context['text_output'] = f"{e}"

        try:
            # for name in ['Contra', 'Blunder', 'Nemesis']:
            for bot in self.app.data['bots']:
                self.app.logic.setup_panel(ShowAI(self.app, bot))
        except Exception as e:
            self.context['text_output'] = f"{e}"
            
        return True

    def end_safely(self):
        # if self.client:
        
        #     self.client.end_safely()
        pass

    @deskapp.callback(ClassID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.scroll == 3:  # on the login selection
            self.context['text_output'] = "logging in."
            self.login()

        if self.scroll == 4:  # on the exit selection
            self.context['text_output'] = "Exitting App."
            self.app.close()
