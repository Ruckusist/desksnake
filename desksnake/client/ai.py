import random, time, threading
import deskapp
from deskserver import ClientSession

class SnakeBot:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self.start_coords = 0
        self.head_coords = 0
        self.heading = 0
        self.lives = 0
        self.high_score = 0
        self.score = 0
        self.id = self.whoami()
        self.thread = threading.Thread(target=self.game_loop, daemon=True)
        self.thread.start()
        self.grid = []
        self.messages = []
        

    def add_message(self, value):
        if len(self.messages) > 7:
            self.messages.pop(0)
        self.messages.append(value)

    def whereami(self):
        grid = self.client.data['snake']['grid']
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                if self.id == grid[x][y]:
                    return (x,y)
        return False


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

    def get_heading(self):
        grid = self.client.data['snake']['grid']
        spots = []
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                if self.id == grid[x][y]:
                    spots.append((x,y))
        if len(spots) < 2: return 0
        spots.pop(self.start_coords)
        other_spot = spots[0]
        if other_spot[0] > self.start_coords[0]:
            # this is up
            heading = 3
        if other_spot[0] > self.start_coords[0]:
            # this is down
            heading = 1
        if other_spot[1] > self.start_coords[1]:
            # this is right
            heading = 2
        if other_spot[1] > self.start_coords[1]:
            # this is left
            heading = 4
        return heading

    def bot_view(self):
        grid = self.client.data['snake']['grid']
        new_grid = []
        for line in grid:
            # new_line = ''.join(
            new_line = [  # list(
                ' ' if not x else (
                    '$' if x==99 else (
                        '%' if x == self.id else (
                            '#'
                        ))) for x in line
            ]  # )
            new_grid.append(new_line)
        new_grid[self.start_coords[0]][self.start_coords[1]] = 'X'
        return [''.join(x) for x in new_grid]

    def movev2(self):
        self.add_message(f"Where am i? {self.head_coords}")
        if random.choice([0,0,1]):
            # 1/2 chance to move left or right.
            self.facing += 1 if random.randint(0,1) else -1
            if self.facing >= 4: self.facing = 0
            if self.facing < 0: self.facing = 3
    
    def move(self):
        self.add_message(f"Where am i? {self.head_coords}")
        self.add_message(f"Finding the Cherries")
        cherries = []
        for x in range(len(self.grid)):
            for y in range(len(self.grid[1])):
                if self.grid[x][y] == '$':
                    cherries.append((x, y))
        self.add_message( f"Found {len(cherries)} Cherries @ {cherries}" )
        self.add_message( f"Whats the Nearest CHerry?" )

        

        # new_heading = random.randint(0,3)
        # if new_heading != self.heading:
        #     # self.message = f"Moving to a new Heading {new_heading} from {self.heading}                     "
        #     self.heading = new_heading
        #     self.send_move(self.heading)
    
    def move_left(self): pass

    def move_right(self): pass

    def send_move(self, direction):
        self.client.send_message(
                snake=True,
                dir_key=direction
            )

    def update_head(self):
        UP    = (self.head_coords[0]+1, self.head_coords[1]  )
        DOWN  = (self.head_coords[0]-1, self.head_coords[1]  )
        LEFT  = (self.head_coords[0],   self.head_coords[1]-1)
        RIGHT = (self.head_coords[0],   self.head_coords[1]+1)
        next_tile  = [UP, RIGHT, DOWN, LEFT][self.heading-1]
        self.head_coords = next_tile
        

    def game_loop(self):
        while True:
            while True:
                if not self.start_coords:
                    self.start_coords = self.whereami()
                    self.head_coords = self.start_coords
                    time.sleep(.01)
                else: break
            while True:
                if not self.heading:
                    self.heading = self.get_heading()
                    time.sleep(.01)
                else: break
            self.update_head()
            self.grid = self.bot_view()
            self.get_score()
            new_grid = self.bot_view()
            if new_grid == self.grid: continue
            self.grid = new_grid
            dead = self.amidead()
            if dead:
                self.lives += 1
                self.add_message(f"Cur Score: {self.score}. I've died {self.lives} times, respawning...")
                self.client.send_message(snake=True, respawn=True)
                self.start_coords = 0
                self.heading = 0

            self.move()


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
                    color = self.app.frontend.palette[1]
                if color:
                    panel.addstr(index+x, y+2, char, color)
                else:
                    panel.addstr(index+x, y+2, char)
        index += len(master)
        panel.addstr(index, 2, f"{hardline_gl2}  {hardline_bl2}", self.frontend.palette[7]); index+= 2
        
        for message in self.bot.messages:
            panel.addstr(index, 2, f"{message:60s}", self.frontend.palette[5]); index+= 1

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