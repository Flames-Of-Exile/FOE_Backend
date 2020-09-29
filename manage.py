import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import db, User

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def create_admin():
    admin = User('admin', '21232f297a57a5a743894a0e4a801fc3', 'email@email.com', User.Role.ADMIN)
    db.session.add(admin)
    db.session.commit()


if __name__ == '__main__':
    manager.run()