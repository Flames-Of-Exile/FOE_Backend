import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from passlib.hash import sha256_crypt

from app import create_app, socketio
from config import main_config
from models import db, Guild, User
import socketevents  # noqa: F401

app = create_app(main_config)

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


@manager.command
def run():
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)


@manager.command
def migrate_media():
    from models import Campaign
    os.chdir('mediafiles')
    os.mkdir('campaigns')
    os.chdir('campaigns')
    for campaign in Campaign.query.all():
        os.rename(f'/usr/src/app{campaign.image}', f'/usr/src/app/mediafiles/campaigns/{campaign.image.split("/")[2]}')
        os.mkdir(campaign.name.replace(' ', '_'))
        os.chdir(campaign.name)
        for world in campaign.worlds:
            os.rename(f'/usr/src/app{world.image}',
                      f'/usr/src/app/mediafiles/campaigns/{campaign.name.replace(" ", "_")}/{world.image.split("/")[2]}')
            os.mkdir(world.name)


if __name__ == '__main__':
    manager.run()
