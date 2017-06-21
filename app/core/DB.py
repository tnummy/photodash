from app import mysql
from flask                    import session
import hashlib


class DB(object):

    def getCursor(self):
        db = mysql.get_db()
        return db.cursor()

    def createUser(self, registrant):
        query = ("INSERT INTO users ( \
                            first, \
                            last, \
                            email, \
                            password) \
                      VALUES (%s,%s,%s,%s)")
        values = (registrant.first, registrant.last, registrant.email, registrant.password)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def addImage(self, image_id, folder_id, user_id, location, resolution, possible_duplicate):
        query = ("INSERT INTO images ( \
                            image_id, \
                            folder_id, \
                            user_id, \
                            location, \
                            resolution, \
                            possible_duplicate) \
                      VALUES (%s,%s,%s,%s,%s,%s)")
        values = (image_id, folder_id, user_id, location, resolution, possible_duplicate)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def checkUserExists(self, email):
        query = "SELECT COUNT(*) FROM users u WHERE u.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def checkHasFeatureImageByFolderId(self, folder_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.featured = 1 AND i.folder_id = %s AND i.deleted = 0"
        values = (folder_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def validateCreds(self, email, password):
        query = "SELECT COUNT(*) FROM users u WHERE u.email = %s AND u.password = %s"
        values = (email, password)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getUserInfoByEmail(self, email):
        query = "SELECT first, last, email FROM users u WHERE u.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def getUserList(self):
        query = "SELECT user_id, first, last, email, password, created FROM users u WHERE u.admin = 0 AND u.deleted = 0"
        cursor = self.getCursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    def getUserWithFolderList(self):
        query = "SELECT u.user_id, u.first, u.last, f.folder_id, f.label FROM users u LEFT JOIN folders f ON f.user_id = u.user_id WHERE u.deleted = 0 AND f.folder_id IS NOT NULL"
        cursor = self.getCursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    def getUserIdByEmail(self, email):
        query = "SELECT user_id FROM users u WHERE u.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getUserIdByFolderId(self, folder_id):
        query = "SELECT user_id FROM folders f WHERE f.folder_id = %s"
        values = (folder_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getUserFolderByFolderId(self, folder_id):
        query = "SELECT u.email FROM folders f LEFT JOIN users u ON u.user_id = f.user_id WHERE f.folder_id = %s"
        values = (folder_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0].split('@')[0]

    def getFoldersByUserId(self, id):
        query = "SELECT folder_id, label FROM folders f WHERE f.user_id = %s AND deleted = 0 ORDER BY folder_order"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getFoldersByUserIdWithFeatureImage(self, id):
        query = "SELECT f.folder_id, f.label, i.image_id FROM folders f LEFT JOIN images i ON i.folder_id = f.folder_id WHERE f.user_id = %s AND f.deleted = 0 AND i.deleted = 0 AND i.featured = 1 ORDER BY folder_order"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getFoldersLabelByID(self, id):
        query = "SELECT label FROM folders f WHERE f.folder_id = %s"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getFolderCountByID(self, id):
        query = "SELECT COUNT(*) FROM folders f WHERE f.user_id = %s"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getImagesByFolderId(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution, featured FROM images i WHERE i.folder_id = %s AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getImageByImageAndUserId(self, image_id, user_id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution, featured FROM images i WHERE i.user_id = %s AND image_id = %s"
        values = (user_id, image_id)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def getFeatureImageByFolderId(self, id):
        query = "SELECT location FROM images i WHERE i.folder_id = %s AND featured = 1"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getStarredImagesByUserID(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution FROM images i WHERE i.user_id = %s AND starred = 1 AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getToEditImagesByUserID(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND to_edit = 1 AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getEditedImagesByUserID(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution FROM images i WHERE i.user_id = %s AND edited = 1 AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getPublicImagesByUserID(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND public = 1 AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getDeletedImagesByUserID(self, id):
        query = "SELECT location, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND deleted = 1 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def recordLogin(self, user_id):
        query = ("INSERT INTO login_history (user_id) \
                      VALUES (%s)")
        values = (user_id,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()


    def createFolder(self, user_id, label='NULL'):
        folderOrder = self.getFolderCountByID(user_id)
        query = ("INSERT INTO folders (user_id, label, folder_order) \
                      VALUES (%s, %s, %s)")
        values = (user_id, label, folderOrder)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def createToken(self, string):
        m = hashlib.md5()
        m.update(string)
        hash = m.hexdigest()
        query = ("INSERT INTO access_tokens (token) \
                      VALUES (%s)")
        values = (hash,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()
        return hash

    def voidHash(self, hash):
        query = "UPDATE access_tokens at SET at.used = 1 WHERE at.token = %s"
        values = (hash,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def deleteUserById(self, user_id):
        query = "UPDATE user u SET u.deleted = 1 WHERE u.user_id = %s"
        values = (user_id,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def deleteImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.deleted = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def undeleteImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.deleted = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def starImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.starred = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unstarImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.starred = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def toEditImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.to_edit = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unToEditImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.to_edit = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def shareImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.public = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unshareImageByImageId(self, image_id, user_id):
        query = "UPDATE images i SET i.public = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def clearFeatureImageByFolderId(self, id):
        query = "UPDATE images i SET i.featured = 0 WHERE i.featured = 1 AND i.folder_id = %s"
        values = (id,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def setFeatureImageByFolderId(self, image_id, folder_id):
        self.clearFeatureImageByFolderId(folder_id)
        query = "UPDATE images i SET i.featured = 1 WHERE i.image_id = %s AND i.folder_id = %s"
        values = (image_id, folder_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def setEditedTagByImageId(self, image_id, folder_id):
        self.clearFeatureImageByFolderId(folder_id)
        query = "UPDATE images i SET i.edited = 1 WHERE i.image_id = %s AND i.folder_id = %s"
        values = (image_id, folder_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def checkHash(self, hash):
        query = "SELECT COUNT(*) FROM access_tokens at WHERE at.token = %s AND at.used = 0"
        values = (hash,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]
