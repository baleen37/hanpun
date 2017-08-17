from manager import Manager

from mangus import storage

manage = Manager()


@manage.command
def run():
    pass


@manage.command
def init_db():
    storage.init_db()


@manage.command
def drop_db():
    storage.drop_db()


@manage.command
def reset_db():
    storage.drop_db()
    storage.init_db()


if __name__ == '__main__':
    manage.main()
