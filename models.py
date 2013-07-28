class User(object):
    def __init__(self, cursor):
        self._id = cursor['_id']
        self.username = cursor['username']
        # self.password = cursor['password']
        self.email = cursor.get('email', None)
        # self.date = cursor.get('date', None)
        # self.ip = cursor.get('ip', None)
        self.group = cursor.get('group', None)
    
    def is_admin(self):
        return self.group == 'admin'
        
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self._id)
    
    def get_username(self):
        return self.username
        
    def get_email(self):
        return self.email
        
    def __repr__(self):
        return '<User %r>' % (self.username)

        