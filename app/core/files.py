import os
from app import *
from flask import flash
from app.core.DB import DB
from PIL import Image

class File(object):

    def makeDirectory(self, folder):
        # baseRoot = os.path.join(app.root_path, app.config['BASE_UPLOAD_FOLDER'])
        baseRoot = app.config['BASE_UPLOAD_FOLDER']
        if not os.path.isdir(os.path.join(baseRoot, folder)):
            os.makedirs(os.path.join(baseRoot, folder))

    def getFolders(self, folder):
        baseRoot = app.config['BASE_UPLOAD_FOLDER']
        # return os.walk(os.path.join(baseRoot, folder))[1]
        return [x[0].split('/')[-1] for x in os.walk(os.path.join(baseRoot, folder))][1:]


    def saveImage(self, image, folder_id, user_id, edited):
        baseRoot = app.config['BASE_UPLOAD_FOLDER']
        location = baseRoot + str(user_id)
        # return os.walk(os.path.join(baseRoot, folder))[1]
        try:
            filename = image.filename.strip()
            possible_duplicate = 0
            i = 1
            originalFilename = filename
            while os.path.isfile(location + '/' + filename):
                possible_duplicate = 1
                filename = str(i) + '_' + originalFilename
                i += 1
            image.save(os.path.join(location, filename))
            action = DB()
            imageObject = Image.open(image)
            width, height = imageObject.size
            resolution = '[' + str(height) + ' x ' + str(width) + ']'
            action.addImage(filename, folder_id, user_id, 'storage/' + str(user_id), resolution, possible_duplicate)
            if not action.checkHasFeatureImageByFolderId(folder_id):
                action.setFeatureImageByFolderId(user_id, filename, folder_id)
            if edited == '1':
                action.setEditedTagByImageId(filename, folder_id)
            maxsize = app.config['WEBVIEW_SIZE']
            imageObject.thumbnail(maxsize)
            thumbnailFilename = 'mid_' + filename
            imageObject.save(os.path.join(location, thumbnailFilename))
            maxsize = app.config['THUMBNAIL_SIZE']
            imageObject.thumbnail(maxsize)
            thumbnailFilename = 'thumb_' + filename
            imageObject.save(os.path.join(location, thumbnailFilename))
            # return jsonify(url=session['url'])
        except Exception as e:
             flash('Image was not saved: ' + e, 'danger')

        # return [x[0].split('/')[-1] for x in os.walk(os.path.join(baseRoot, folder))][1:]
