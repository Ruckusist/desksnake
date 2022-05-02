import deskapp
from desksnake.client import Login


def main():
    app = deskapp.App([Login], demo_mode=False)
    app.data['messages'] = []
    app.data['grid'] = []
    app.start()


if __name__ == "__main__":
    main()