class User(object):
    def __init__(self, cursor):
        self._id = cursor['_id']
        self.username = cursor['username']
        self.password = cursor['password']
        
        
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self._id)
        
    def __repr__(self):
        return '<User %r>' % (self.username)

        