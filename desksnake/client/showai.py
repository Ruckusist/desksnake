import random, time, threading
import deskapp
from deskserver import ClientSession
# from .bot import SnakeBot

ClassID = random.random()
class ShowAI(deskapp.Module):
    name = "AI View"

    def __init__(self, app, AI):
        super().__init__(app)
        self.classID = ClassID
        self.app = app
        self.score = 0
        self.index = 1
        self.bot = AI()
        self.username = self.bot.name
        self.password = self.username + "password"
        self.server_host = self.app.data['server_host']        
        self.client = ClientSession(SERVER_HOST=self.server_host, VERBOSE=False)
        if self.login():
            self.client.add_sub('snake')            
            # LAST THING!
            self.bot.start(self.client)
            self.register_module()
        else:
            self.app.data['messages'].append("AI Client Failed to Load. Error!")

    def page(self, panel):
        index = 1
        max_h = self.app.frontend.winright_upper_dims[0]
        max_w = self.app.frontend.winright_upper_dims[1]
        top_line = f"╔═══| {self.username} |{'═'*10}| {str(self.bot.score):>5s} |╗"
        # panel.addstr(self.index, 4, f"AI  -- {self.username} | score: {self.bot.score}", self.frontend.chess_white); self.index+=1
        panel.addstr(index, 2, top_line, self.frontend.palette[5]); index+=1
        panel.addstr(index, 2, f"Main View                    AI View", self.frontend.palette[3]); index+=1
        # if not self.client.data.get('snake', False): return
        if not self.client.data['snake'].get('grid', False): return
        grid = self.client.data['snake']['grid']
        botgrid = self.bot.grid

        hardline_gl1 = "╔" + "═" * (len(grid[1])) + "╗"
        hardline_gl2 = "╚" + "═" * (len(grid[1])) + "╝"
        hardline_bl1 = "╔" + "═" * (len(grid[1])) + "╗"
        hardline_bl2 = "╚" + "═" * (len(grid[1])) + "╝"
        panel.addstr(index, 2, f"{hardline_gl1}  {hardline_bl1}", self.frontend.palette[7]); index+= 1
        master = []
        for grid_line, bot_line in zip(grid, botgrid):
            gl = ''.join(['*' if x == 99 else (
                str(x) if x else ' ') for x in grid_line])
            print_string = f"║{gl}║  ║{bot_line}║"
            master.append(print_string)

        color_switch = 2
        color_table = {}
        for x in range(len(master)):
            line_len = len(master[x])
            for y in range(line_len):
                char = master[x][y]
                color = 0  # self.app.frontend.palette[1]
                # INT STUFFS
                if False:
                    try:
                        char = int(char)
                        char = str(char)
                        if not color_table.get(char, False):
                            color_table[char] = self.app.frontend.palette[color_switch]
                            color_switch += 1
                        color = color_table[char]
                        char = '█'
                    except: pass
                if char == '#':
                    color = self.app.frontend.palette[2]
                if char == '$' or char == '*':
                    color = self.app.frontend.palette[3]
                if char == "║":
                    color = self.app.frontend.palette[7]
                if char == "%":
                    color = self.app.frontend.palette[2]
                if char in ['V', '>','^','<']:
                    color = self.app.frontend.palette[1]
                if color:
                    panel.addstr(index+x, y+2, char, color)
                else:
                    panel.addstr(index+x, y+2, char)
        index += len(master)
        panel.addstr(index, 2, f"{hardline_gl2}  {hardline_bl2}", self.frontend.palette[7]); index+= 2
        
        for message in self.bot.messages:
            panel.addstr(index, 2, f"{message:60s}", self.frontend.palette[5]); index+= 1

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
                    time.sleep(.1)
                continue
            
            if not self.client.logged_in:
                self.client.login(self.username, self.password)
                time.sleep(.5)
                continue
            
            success = True
        # successful login.
        if success:
            self.client.username = self.username
            return True
        return False

    @deskapp.callback(ClassID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        self.client.send_message(snake=True, respawn=True)

    @deskapp.callback(ClassID, deskapp.Keys.W)
    def on_W(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=3
        )

    @deskapp.callback(ClassID, deskapp.Keys.A)
    def on_A(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=4
        )

    @deskapp.callback(ClassID, deskapp.Keys.S)
    def on_S(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=1
        )

    @deskapp.callback(ClassID, deskapp.Keys.D)
    def on_D(self, *args, **kwargs):
        self.client.send_message(
            snake=True,
            dir_key=2
        )