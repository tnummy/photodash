class Guest(object):

    def __init__(self, first, last, email, guest_of=None, access_level_id=None, password=None):
        self.first    = first
        self.last     = last
        self.email    = email
        self.password = password
        self.guest_of = guest_of
        self.access_level_id = access_level_id
        # self.folder   = email.split('@')[0]
        # self.setParentFolder(self.folder)
        # self.folders = self.setFolders(self.folder)