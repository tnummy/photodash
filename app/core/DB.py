from app import *
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
        user_id = cursor.lastrowid
        db.commit()
        return str(user_id)

    def createGuest(self, registrant):
        query = ("INSERT INTO guests ( \
                            first, \
                            last, \
                            email, \
                            password) \
                      VALUES (%s,%s,%s,%s)")
        values = (registrant.first, registrant.last, registrant.email, registrant.password)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        guest_id = cursor.lastrowid
        db.commit()
        query = ("INSERT INTO guest_access ( \
                            guest_id, \
                            user_id, \
                            access_level_id) \
                      VALUES (%s,%s,%s)")
        values = (guest_id, registrant.guest_of, registrant.access_level_id)
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

    def validateUserCreds(self, email, password):
        query = "SELECT COUNT(*) FROM users u WHERE u.email = %s AND u.password = %s AND u.deleted = 0"
        values = (email, password)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def validateGuestCreds(self, email, password):
        query = "SELECT COUNT(*) FROM guests g WHERE g.email = %s AND g.password = %s AND g.deleted = 0"
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

    def getGuestAccessUserByGuestID(self, id):
        query = "SELECT ga.user_id, ga.access_level_id FROM guest_access ga WHERE ga.guest_id = %s LIMIT 1"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def getGuestInfoByEmail(self, email):
        query = "SELECT g.first, g.last, g.email FROM guests g WHERE g.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def getUserEmailByUserId(self, user_id):
        query = "SELECT email FROM users u WHERE u.user_id = %s"
        values = (user_id,)
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

    def getGuestList(self, user_id):
        query = "SELECT guest_id FROM guest_access ga WHERE ga.user_id = %s"
        values = (user_id, )
        cursor = self.getCursor()
        cursor.execute(query, values)
        guest_ids = cursor.fetchall()
        query = "SELECT guest_id, first, last, email, created FROM guests g WHERE g.deleted = 0 AND g.guest_id IN %s"
        values = (guest_ids, )
        cursor = self.getCursor()
        cursor.execute(query, values)
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

    def getGuestIdByEmail(self, email):
        query = "SELECT guest_id FROM guests g WHERE g.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getUserPasswordByEmail(self, email):
        query = "SELECT password FROM users u WHERE u.email = %s"
        values = (email,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getUserIdByPasswordHash(self, hash):
        query = "SELECT user_id FROM password_reset_tokens prt WHERE prt.token = %s"
        values = (hash,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getNewGuestRegistrationInfoByHash(self, hash):
        query = "SELECT email, user_id, access_level_id FROM guest_tokens gt WHERE gt.token = %s"
        values = (hash,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

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
        query = "SELECT f.folder_id, f.label, COUNT(i.image_id) FROM folders f LEFT JOIN images i ON i.folder_id = f.folder_id AND i.deleted = 0 WHERE f.user_id = %s AND f.deleted = 0 GROUP BY f.folder_id ORDER BY folder_order"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        # for result in results:
        #     result.append(self.getImageCountByFolderId(result[0]))
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

    def getImageCountByFolderId(self, folder_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.folder_id = %s AND i.deleted = 0"
        values = (folder_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getStarredImageCountByUserId(self, user_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.user_id = %s AND i.deleted = 0 AND i.starred = 1"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getToEditImageCountByUserId(self, user_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.user_id = %s AND i.deleted = 0 AND i.to_edit = 1"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getEditedImageCountByUserId(self, user_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.user_id = %s AND i.deleted = 0 AND i.edited = 1"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getPublicImageCountByUserId(self, user_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.user_id = %s AND i.deleted = 0 AND i.public = 1"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getDeletedImageCountByUserId(self, user_id):
        query = "SELECT COUNT(*) FROM images i WHERE i.user_id = %s AND i.deleted = 1 AND i.hard_deleted = 0 "
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def getImagesByFolderId(self, id):
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution, featured FROM images i WHERE i.folder_id = %s AND deleted = 0 ORDER BY image_id"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getImageByImageAndUserId(self, image_id, user_id):
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution, featured FROM images i WHERE i.user_id = %s AND image_id = %s AND deleted = 0"
        values = (user_id, image_id)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def getFeatureImageByFolderId(self, id):
        query = "SELECT user_id FROM images i WHERE i.folder_id = %s AND featured = 1"
        values = (id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results[0]

    def getStarredImagesByUserID(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_VIEW_STARRED'])
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution FROM images i WHERE i.user_id = %s AND starred = 1 AND deleted = 0 ORDER BY image_id"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getToEditImagesByUserID(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_VIEW_TOEDIT'])
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND to_edit = 1 AND deleted = 0 ORDER BY image_id"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getEditedImagesByUserID(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_VIEW_EDITED'])
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution FROM images i WHERE i.user_id = %s AND edited = 1 AND deleted = 0 ORDER BY image_id"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getPublicImagesByUserID(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_VIEW_PUBLIC'])
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND public = 1 AND deleted = 0 ORDER BY image_id"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getDeletedImagesByUserID(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_VIEW_DELETED'])
        query = "SELECT user_id, image_id, starred, to_edit, public, deleted, resolution  FROM images i WHERE i.user_id = %s AND deleted = 1 AND hard_deleted = 0 ORDER BY image_id"
        values = (user_id,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchall()
        return results

    def getActivityIdByKeyword(self, keyword):
        query = "SELECT activity_id FROM activity a WHERE a.activity_keyword = %s AND deleted = 0"
        values = (keyword,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        results = cursor.fetchone()
        return results

    def recordLogin(self, user_id, guest_id=None):
        query = ("INSERT INTO login_history (user_id, guest_id, login) \
                      VALUES (%s, %s, 1)")
        values = (user_id, guest_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()


    def recordLogout(self, user_id):
        query = ("INSERT INTO login_history (user_id, logout) \
                      VALUES (%s, 1)")
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

    def createGuestToken(self, email, user_id, access_level_id):
        m = hashlib.md5()
        string = email + str(user_id) + str(access_level_id)
        m.update(string)
        hash = m.hexdigest()
        query = ("INSERT INTO guest_tokens (email, user_id, access_level_id, token) \
                      VALUES (%s,%s,%s,%s)")
        values = (email, user_id, access_level_id, hash,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()
        return hash

    def createPasswordResetToken(self, email):
        m = hashlib.md5()
        m.update(email)
        user_id = self.getUserIdByEmail(email)
        old_password = self.getUserPasswordByEmail(email)
        hash = m.hexdigest()
        self.voidOldResetPasswordHash(hash)
        query = ("INSERT INTO password_reset_tokens (user_id, old_password, token) \
                      VALUES (%s, %s, %s)")
        values = (user_id, old_password, hash,)
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

    def voidGuestHash(self, hash, guest_of):
        query = "UPDATE guest_tokens gt SET gt.used = 1 WHERE gt.token = %s AND gt.user_id = %s"
        values = (hash, guest_of)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def voidResetPasswordHash(self, hash):
        query = "UPDATE password_reset_tokens prt SET prt.used = 1 WHERE prt.token = %s"
        values = (hash,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def voidOldResetPasswordHash(self, hash):
        query = "UPDATE password_reset_tokens prt SET prt.used = 1 WHERE prt.token = %s"
        values = (hash,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def resetPassword(self, newPassword, hash):
        self.voidResetPasswordHash(hash)
        user_id = self.getUserIdByPasswordHash(hash)
        query = "UPDATE users u SET u.password = %s WHERE u.user_id = %s"
        values = (newPassword, user_id)
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

    def deleteGuestById(self, guest_id):
        query = "UPDATE guests g SET g.deleted = 1 WHERE g.guest_id = %s"
        values = (guest_id,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def deleteImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_DELETED'], image_id=image_id)
        query = "UPDATE images i SET i.deleted = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def undeleteImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_UNDELETED'], image_id=image_id)
        query = "UPDATE images i SET i.deleted = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def logAction(self, user_id, action_keyword, image_id=None, folder_id=None):
        query = ("INSERT INTO activity_history (user_id, action, image_id, folder_id) \
                      VALUES (%s, %s, %s, %s)")
        action = self.getActivityIdByKeyword(action_keyword)
        values = (user_id, action, image_id, folder_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def emptyTrashByUserId(self, user_id):
        self.logAction(user_id, app.config['ACTIVITY_EMPTY_TRASH'])
        query = "UPDATE images i SET i.hard_deleted = 1 WHERE i.user_id = %s AND i.deleted = 1"
        values = (user_id,)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def starImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_STARRED'], image_id=image_id)
        query = "UPDATE images i SET i.starred = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unstarImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_UNSTARRED'], image_id=image_id)
        query = "UPDATE images i SET i.starred = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def toEditImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_TOEDIT'], image_id=image_id)
        query = "UPDATE images i SET i.to_edit = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unToEditImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_UNTOEDIT'], image_id=image_id)
        query = "UPDATE images i SET i.to_edit = 0 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def shareImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_SHARED'], image_id=image_id)
        query = "UPDATE images i SET i.public = 1 WHERE i.image_id = %s AND i.user_id = %s"
        values = (image_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def unshareImageByImageId(self, image_id, user_id):
        self.logAction(user_id, app.config['ACTIVITY_UNSHARED'], image_id=image_id)
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

    def setFeatureImageByFolderId(self, user_id, image_id, folder_id):
        self.logAction(user_id, app.config['ACTIVITY_FLAGGED'], image_id=image_id, folder_id=folder_id)
        self.clearFeatureImageByFolderId(folder_id)
        query = "UPDATE images i SET i.featured = 1 WHERE i.image_id = %s AND i.folder_id = %s AND i.user_id = %s"
        values = (image_id, folder_id, user_id)
        db = mysql.get_db()
        cursor = db.cursor()
        cursor.execute(query, values)
        db.commit()

    def setEditedTagByImageId(self, image_id, folder_id):
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

    def checkGuestHash(self, hash):
        query = "SELECT COUNT(*) FROM guest_tokens gt WHERE gt.token = %s AND gt.used = 0"
        values = (hash,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]

    def checkPasswordResetHash(self, hash):
        query = "SELECT COUNT(*) FROM password_reset_tokens prt WHERE prt.token = %s AND prt.used = 0"
        values = (hash,)
        cursor = self.getCursor()
        cursor.execute(query, values)
        count = cursor.fetchone()
        return count[0]
