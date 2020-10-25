import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from passlib.hash import sha256_crypt

from app import create_app
from models import db, Guild, User

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_admin():
    foe_guild = Guild('Flames of Exile')
    db.session.add(foe_guild)
    db.session.commit
    foe_guild = db.session.query(Guild).filter_by(name='Flames of Exile').first()
    admin = User('DiscordBot', sha256_crypt.encrypt(os.environ['BOT_PASSWORD']), foe_guild.id, User.Role.ADMIN)
    admin.discord_confirmed = True
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
