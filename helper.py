from models import db, User

# Get a user from the database or add a new one
def get_or_add_user(whatsapp_number, name=None):
    user = User.query.filter_by(whatsapp_number=whatsapp_number).first()
    if user:
        if name:
            user.name = name
            db.session.commit() # Update the name of the user
        return user
    elif name:
        new_user = User(whatsapp_number=whatsapp_number, name=name)
        db.session.add(new_user) # Add a new user to the database
        db.session.commit() # Commit the changes
        return new_user
    return None

# Get the name of a user from the database
def get_user_name(whatsapp_number):
    user = User.query.filter_by(whatsapp_number=whatsapp_number).first() # Get the user from the database
    if user:
        return user.name
    return None
