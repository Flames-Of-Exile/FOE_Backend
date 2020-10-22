from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from passlib.hash import sha256_crypt

from app import create_app
from models import db, User

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_admin():
    admin = User('DiscordBot', sha256_crypt.encrypt('admin'), User.Role.ADMIN)
    admin.discord_confirmed = True
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
