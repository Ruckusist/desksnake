import deskapp
from desksnake.client import Login
from desksnake import SnakeBot

def main(bots=[]):
    app = deskapp.App([Login], demo_mode=False)
    app.data['messages'] = []
    app.data['grid'] = []
    app.data['bots'] = bots
    app.start()


if __name__ == "__main__":
    main()