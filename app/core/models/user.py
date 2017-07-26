from app.core.files import File

class User(object):

    def __init__(self, first, last, email, password=None):
        self.first    = first
        self.last     = last
        self.email    = email
        self.password = password
        # self.folder   = email.split('@')[0]
        # self.setParentFolder(self.folder)
        self.folders = self.setFolders(self.folder)

    def setParentFolder(self, folder):
        File().makeDirectory(folder)

    def setFolders(self, folder):
        return File().getFolders(folder)

    def setStarred(self):
        pass

    def setDeleted(self):
        pass