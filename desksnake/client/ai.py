import random, time, threading
import deskapp
from deskserver import ClientSession

class SnakeBot:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self.heading = 0
        self.lives = 0
        self.high_score = 0
        self.score = 0
        self.id = self.whoami()
        self.thread = threading.Thread(target=self.game_loop, daemon=True)
        self.thread.start()
        self.message = ""

    def whoami(self):
        self.client.send_message(snake=True, respawn=True)
        time.sleep(.5)
        for p in self.client.data['snake']['players_online']:
            if p[1] == self.username:
                return p[0]+1

    def get_score(self):
        for p in self.client.data['snake']['players_online']:
            if p[1] == self.username:
                self.score = p[2]
                return

    def amidead(self):
        grid = self.client.data['snake']['grid']
        for line in grid:
            if self.id in line:
                return False
        return True

    def move(self):
        new_heading = random.randint(0,3)
        if new_heading != self.heading:
            self.message = f"Moving to a new Heading {new_heading} from {self.heading}                     "
            self.heading = new_heading
            self.client.send_message(
                snake=True,
                dir_key=self.heading
            )

    def game_loop(self):
        while True:
            self.get_score()
            dead = self.amidead()
            if dead:
                self.lives += 1
                self.message = f"Cur Score: {self.score}. I've died {self.lives} times, respawning..."
                time.sleep(2)
                self.client.send_message(snake=True, respawn=True)
                # continue

            if random.choice([0,0,1]):
                self.message = "Trying to Move."
                self.move()
                time.sleep(1)
            time.sleep(1)




ClassID = random.random()
class ShowAI(deskapp.Module):
    name = "AI View"

    def __init__(self, app):
        super().__init__(app)
        self.classID = ClassID
        self.app = app
        # self.client = app.data['client']['client']
        # self.username = app.data['client']['username']
        self.score = 0
        self.index = 1
        self.server_host = self.app.data['server_host']
        self.app.data['AIUser'] = {
            'username': 'Contra',
            'client': ClientSession(SERVER_HOST=self.server_host, VERBOSE=False)
        }
        self.username = self.app.data['AIUser']['username']
        self.client = self.app.data['AIUser']['client']
        self.client.login(
            username=self.app.data['AIUser']['username'],
            password="AI"
        )
        
        self.client.add_sub('snake')
        self.setup()
        # LAST THING!
        self.register_module()

    def setup(self):
        time.sleep(1)
        self.bot = SnakeBot(self.client, self.username)


    def page(self, panel):
        panel.addstr(self.index, 4, f"AI  -- {self.username} | score: {self.bot.score}", self.frontend.chess_white)

        # if not self.client.data.get('snake', False): return
        if not self.client.data['snake'].get('grid', False): return
        grid = self.client.data['snake']['grid']
        
        index = 4
        # panel.addstr(4, 4, f"This is working")  # ; self.index+= 1
        hardline = "#" * (len(grid[1])+2)
        panel.addstr(index, 4, f"{hardline}"); index+= 1
        for line in grid:
            l = ''.join(['*' if x == 99 else (str(x) if x else ' ') for x in line])
            panel.addstr(index, 4, f"#{l}#"); index+= 1
        panel.addstr(index, 4, f"{hardline}"); index+= 2
        panel.addstr(index, 4, f"{self.bot.message}"); index+= 2

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