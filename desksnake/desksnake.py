import random, time, threading
from timeit import default_timer as timer
from deskserver import Server, Engine, Session, Message, User, Errors

class SnakeUser(User):
    def __init__(self, username, password, session, AI=False):
        self.AI = AI
        self.highscore = 0
        self.snake = None
        super().__init__(username, password, session)


class Snake:
    """The actual Snake"""
    def __init__(self, head_coords, AI:bool=False) -> None:
        self.head_coords = head_coords
        self.max_length  = 4
        self.ai          = AI
        self.dead        = False
        self.filled      = [head_coords]
        self.facing      = random.randint(0,3)

    def __getstate__(self): return self.__dict__

    @property
    def score(self): return len(self.filled)

    @property
    def length(self): return len(self.filled)

    def move(self):
        """This is the AI"""
        # a 1/3 chance to move
        if random.choice([0,0,1]):
            # 1/2 chance to move left or right.
            self.facing += 1 if random.randint(0,1) else -1
            if self.facing >= 4: self.facing = 0
            if self.facing < 0: self.facing = 3


class SnakeGame:
    def __init__(self, engine:Engine) -> None:
        self.engine = engine
        self.should_shutdown = False
        self.map_size = (24, 21)  # google standard map size.
        self.blocked_tiles = []
        self.max_cherries = 3
        self.cherries = []
        self._grid = []
        self.frame_times = []
        self.highscore = (0, 'Nobody!')
        print(f"[Snk][{time.ctime()}]| SnakeGame is Online")
        
        # SPAWN SOME BOTS!
        for i in range(2):
            bot_name = f'Ruckusbot{i}'
            # self.new_ai(bot_name)
            self.engine.login(
                session=True,
                message=Message(
                    username = bot_name,
                    password = 'AI',
                    session  = True,
                )
            )
            bot = self.engine.users[bot_name]
            bot.AI = True
            self.respawn_player(bot)

        # START THE GAME
        
        self.thread = threading.Thread(target=self.game_loop)
        self.thread.start()

    @property
    def avg_frame_time(self):
        self.frame_times = self.frame_times[-30:]
        return int(self.frame_times/30)

    @property
    def grid(self) -> list:
        return self._grid

    def build_grid(self) -> None:
        # GOT IT... sets up range(y) in range(x)
        bare = [[0 for _ in range(self.map_size[1])] for _ in range(self.map_size[0])]
        self.blocked_tiles = []
        # SHOW ALL PLAYERS AS THEIR NUMBER
        for player_id, user in enumerate(self.engine.users):
            player = self.engine.users[user]
            if not player.online: continue
            if not player.snake: continue

            for coords in player.snake.filled:
                bare[coords[0]][coords[1]] = player_id+1
                self.blocked_tiles.append(coords)

        if self.cherries:
            for cherry in self.cherries:
                bare[cherry[0]][cherry[1]] = 99
        self._grid = bare

    def build_cherries(self) -> None:
        if len(self.cherries) < self.max_cherries:
            if random.randint(0,1):
                self.cherries.append(self.get_empty_tile())

    def build_report(self) -> None:
        report = {
            'grid': self.grid,
            'players_online': 0,  # should be a list of (player_num: player name)
        }
        self.engine.publish_data['snake'] = report

    def get_empty_tile(self):
        while True:
            new_tile = (
                    random.randint(0, self.map_size[0]-1),
                    random.randint(0, self.map_size[1]-1)
                    )
            if ( new_tile not in self.blocked_tiles and
                 new_tile not in self.cherries
            ): break
        return new_tile

    def respawn_player(self, player:SnakeUser):
        new_head_coords = self.get_empty_tile()
        new_snake = Snake(head_coords=new_head_coords, AI=player.AI)
        # print(f"[Snk][{time.ctime()}]| {player.username} respawning @ {new_head_coords}.")
        player.snake = new_snake

    def dead_player(self, player:SnakeUser):
        # copy the dead snake
        snake = player.snake
        # Kill the snake.
        player.snake = False

        if snake.score > player.highscore:
            msg = f"[Snk][{time.ctime()}]| "
            msg += f"\n\tPlayer: {player.username}"
            player.highscore = snake.score
            msg += f"\n\tSet a Personal High Score! **{snake.score}**"

            if snake.score > self.highscore[0]:
                self.highscore = (snake.score, player.username)
                msg += f"\n\tSet an ALL-TIME High Score! **{snake.score}** WOW!"

            else:
                msg += f"\n\tALL-TIME High Score is still **{self.highscore[0]}** |- {self.highscore[1]} -|"

            print(msg)
        # kill the copy
        del snake

    def move_player(self, snake:Snake):
        UP    = (snake.head_coords[0]+1, snake.head_coords[1]  )
        DOWN  = (snake.head_coords[0]-1, snake.head_coords[1]  )
        LEFT  = (snake.head_coords[0],   snake.head_coords[1]-1)
        RIGHT = (snake.head_coords[0],   snake.head_coords[1]+1)
        next_tile  = [UP, RIGHT, DOWN, LEFT][snake.facing]

         # IF NEXT TILE EQUALS DEATHE...
        if (
            next_tile[0] < 0 or 
            next_tile[1] < 0 or
            next_tile[0] >= self.map_size[0] or 
            next_tile[1] >= self.map_size[1] or
            next_tile in self.blocked_tiles
            ):
            snake.dead = True
            return snake
        pass

        # IF NEXT TILE IS A CHERRY!
        if next_tile in self.cherries:
            self.cherries.remove(next_tile)
            snake.max_length += 1

        # GROW THE SNAKE
        snake.head_coords = next_tile
        snake.filled.append(next_tile)

        if snake.length == snake.max_length:
            snake.filled.pop(0)
        
        return snake

    def frame(self):
        start_time = timer()
        self.build_grid()
        self.build_cherries()

        # The real Rules!
        # 1) Move every Player 1 tile in the direction they are facing.
        for user in self.engine.users:
            player = self.engine.users[user]
            if not player.snake: continue
            player.snake = self.move_player(player.snake)
            if player.snake.dead:
                self.dead_player(player)
                if player.AI:
                    self.respawn_player(player)
            if player.AI:
                player.snake.move()

        # REPORT
        self.build_report()

        # AND TIME!
        runtime = timer() - start_time
        self.frame_times.append(runtime)
        return runtime

    @Errors.protected
    def game_loop(self):
        # try:
        while True:
            if self.should_shutdown: break        
            frame_time = self.frame()
            sleep_time = .5-frame_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print(f"[Snk][{time.ctime()}]| Game is lagging by: {abs(sleep_time)} secs")
        self.engine.end_safely()

    def callback(self, session:Session, message:Message):
        username = session.username
        user = self.engine.users[username]
        if message.respawn:
            if not user.snake:
                self.respawn_player(user)
        if message.dir_key:    
            if user.snake:
                user.snake.facing = message.dir_key - 1


class Desksnake(Server):
    def __init__(self):
        super().__init__(USER=SnakeUser)
        self.game = SnakeGame(self.engine)
        
    def callback(self, session:Session, message:Message):
        super().callback(session, message)
        if message.snake:
            self.game.callback(session, message)


def main():
    x = Desksnake()

if __name__ == "__main__":
    main()
