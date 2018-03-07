from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, \
                  abort, jsonify
from app.core.repository import *
from app.core.models.user import User
from app.core.models.guest import Guest
from app.core.DB import DB
from app import *
from app.core.files import File
from functools import wraps
from datetime import datetime

import requests

mod = Blueprint('core', __name__)

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('active'):
#             return redirect(url_for('core/signin', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function

@app.context_processor
def inject_stuff():
    action = DB()
    if session.get('id'):
        user_id = session['id']
        folders = action.getFoldersByUserId(session['id'])
        tagCounts = {}
        tagCounts['starred'] = action.getStarredImageCountByUserId(user_id)
        tagCounts['toedit'] = action.getToEditImageCountByUserId(user_id)
        tagCounts['edited'] = action.getEditedImageCountByUserId(user_id)
        tagCounts['public'] = action.getPublicImageCountByUserId(user_id)
        tagCounts['deleted'] = action.getDeletedImageCountByUserId(user_id)
        return {'now': datetime.utcnow(), 'tagCounts': tagCounts, 'folders': folders}
    return {'now': datetime.utcnow(), 'tagCounts': 0}



@mod.route('/')
# @login_required
def index(message=None, type='info'):
    if session.get('active'):
        repository = Repository()
        action = DB()
        user_id = session['id']
        # folders = action.getFoldersByUserId(session['id'])
        access_level_id = session['access_level_id']
        if access_level_id == 3:
            return redirect('/album/public')
        foldersFeatures = action.getFoldersByUserIdWithFeatureImage(session['id'])
        return (render_template('core/index.html', mainFolder=user_id, foldersFeatures=foldersFeatures, active=False))
    else:
        if message:
            flash(message, type)
        return render_template('core/signin.html')


@mod.route('/album')
@mod.route('/album/<album>')
@mod.route('/album/<album>/<image_id>')
@mod.route('/<user_id>/album/<album>/<image_id>')
def folder(user_id=None, album=None, image_id=None):
    if session.get('active'):
        action = DB()
        access_level_id = session['access_level_id']
        if access_level_id == 3:
            album = 'public'
        if album:
            user_id = session['id']
            hideFolders = True
            zoomImage = False
            active = str(album)
            images = False
            nextImage = False
            previousImage = False
            showFeatureFlag = False
            if not image_id:
                action.logAction(user_id, app.config['ACTIVITY_FOLDER_VIEW'], image_id=None, folder_id=album)
            if album == 'starred':
                albumName = 'Starred'
                images = action.getStarredImagesByUserID(user_id)
            elif album == 'toedit':
                albumName = 'To Edit'
                images = action.getToEditImagesByUserID(user_id)
            elif album == 'edited':
                albumName = 'Edited'
                images = action.getEditedImagesByUserID(user_id)
            elif album == 'public':
                albumName = 'Public'
                images = action.getPublicImagesByUserID(user_id)
            elif album == 'deleted':
                albumName = 'Deleted'
                images = action.getDeletedImagesByUserID(user_id)
            elif album:
                active = int(album)
                showFeatureFlag = True
                albumName = action.getFoldersLabelByID(album)
                images = action.getImagesByFolderId(album)
            if image_id:
                zoomImage = action.getImageByImageAndUserId(image_id, user_id)
                action.logAction(user_id, app.config['ACTIVITY_VIEW_ZOOMED'], image_id, album)
                if images and zoomImage:
                    if zoomImage in images:
                        imageLocation = images.index(zoomImage)
                        if imageLocation == len(images) - 1:
                            nextImage = False
                        else:
                            nextImage = action.getImageByImageAndUserId(images[imageLocation + 1][1], user_id)
                        if imageLocation == 0:
                            previousImage = False
                        else:
                            previousImage = action.getImageByImageAndUserId(images[imageLocation - 1][1], user_id)

            return (render_template('core/index.html', showFeatureFlag=showFeatureFlag, nextImage=nextImage, previousImage=previousImage, zoomImage=zoomImage, hideFolders=hideFolders, albumName=albumName, images=images, active=active))
    return index('You must be signed in to see this page', 'warning')


@mod.route('/profile')
def profile():
    return (render_template('core/cover.html'))


@mod.route('/feature', methods=['POST'])
def feature():
    if request.method == 'POST':
        action = DB()
        action.setFeatureImageByFolderId(session['id'], request.form['inputImage'], request.form['inputAlbum'])
        flash('Image marked as album feature image.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/star', methods=['POST'])
def star():
    if request.method == 'POST':
        action = DB()
        action.starImageByImageId(request.form['inputImage'], session['id'])
        flash('Image starred.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/to-edit', methods=['POST'])
def toEdit():
    if request.method == 'POST':
        action = DB()
        action.toEditImageByImageId(request.form['inputImage'], session['id'])
        flash('Image marked to be edited.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/share', methods=['POST'])
def share():
    if request.method == 'POST':
        action = DB()
        action.shareImageByImageId(request.form['inputImage'], session['id'])
        flash('Image added to public album.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/delete', methods=['POST'])
def delete():
    if request.method == 'POST':
        action = DB()
        action.deleteImageByImageId(request.form['inputImage'], session['id'])
        flash('Image deleted.', 'warning')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')


@mod.route('/unstar', methods=['POST'])
def unstar():
    if request.method == 'POST':
        action = DB()
        action.unstarImageByImageId(request.form['inputImage'], session['id'])
        flash('Image unstarred.', 'warning')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/un-to-edit', methods=['POST'])
def unToEdit():
    if request.method == 'POST':
        action = DB()
        action.unToEditImageByImageId(request.form['inputImage'], session['id'])
        flash('Image removed from \"to be edited\".', 'warning')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/unshare', methods=['POST'])
def unshare():
    if request.method == 'POST':
        action = DB()
        action.unshareImageByImageId(request.form['inputImage'], session['id'])
        flash('Image removed from public album.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')

@mod.route('/undelete', methods=['POST'])
def undelete():
    if request.method == 'POST':
        action = DB()
        action.undeleteImageByImageId(request.form['inputImage'], session['id'])
        flash('Image restored.', 'success')
        if request.form['inputZoom'] == str(1):
            return redirect('/album/' + request.form['inputAlbum'] + '/' + request.form['inputImage'])
        return redirect('/album/'+request.form['inputAlbum'])
    return redirect('/')


@mod.route('/uploadimages')
def uploadimages():
    action = DB()
    users = action.getUserWithFolderList()
    return render_template('core/uploadimage.html', users=users, active='uploadImages')

@mod.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        image_files = request.files.getlist('images')
        for image_file in image_files:
            try:
                action = DB()
                if image_file and allowed_file(image_file.filename):
                    folder_id = request.form['inputFolder']
                    user_id = action.getUserIdByFolderId(folder_id)
                    # user_folder = action.getUserFolderByFolderId(folder_id)
                    File().saveImage(image_file, folder_id, user_id, request.form['inputEditTag'])
            except Exception as e:
                flash(image_file.filename + ' is an invalid file type. ' + e, 'danger')
    return redirect('/uploadimages')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in app.config['ALLOWED_EXTENSIONS']

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

@mod.route('/generate-register')
def generateRegister():
    return render_template('core/generate.html', active='generateRegister')


@mod.route('/generate-guest-register')
def generateGuestRegister():
    return render_template('core/generateguest.html', active='generateGuestRegister')


@mod.route('/generate-register-action', methods=['POST'])
def generateRegisterAction():
    if request.method == 'POST':
        string = request.form['inputString']
        action = DB()
        hash = action.createToken(string)
        flash('photos.timnummyphotography.com/register/' + hash, 'success')
    return render_template('core/generate.html')


@mod.route('/generate-guest-register-action', methods=['POST'])
def generateGuestRegisterAction():
    if request.method == 'POST':
        email = request.form['inputEmail']
        access_level_id = request.form['inputAccessLevelId']
        user_id = session['id']
        action = DB()
        hash = action.createGuestToken(email, user_id, access_level_id)
        flash('photos.timnummyphotography.com/register/guest/' + hash, 'success')
    return render_template('core/generateguest.html')


@mod.route('/generate-reset-password')
def generatePasswordReset():
    return render_template('core/generateresetpassword.html', active='generatePasswordReset')


@mod.route('/generate-reset-password-action', methods=['POST'])
def generatePasswordResetAction():
    if request.method == 'POST':
        email = request.form['inputEmail']
        action = DB()
        hash = action.createPasswordResetToken(email)
        flash('photos.timnummyphotography.com/reset-password/' + hash, 'success')
    return render_template('core/generateresetpassword.html')


@mod.route('/reset-password')
@mod.route('/reset-password/<hash>')
def resetPassword(hash=None):
    if session.get('active'):
        return redirect('/')
    if not hash:
        flash('Password reset not valid.', 'warning')
        return redirect('/signin')
    return (render_template('core/resetpassword.html', hash=hash))


@mod.route('/create-folder')
def createFolder():
    action = DB()
    users = action.getUserList()
    # session['folder'] = action.getFoldersByUserId(session['id'])
    return render_template('core/createfolder.html', users=users, active='createFolder')


@mod.route('/empty-trash')
def emptyTrash():
    action = DB()
    action.emptyTrashByUserId(session['id'])
    return redirect('/')

@mod.route('/user-list', methods=['GET'])
def userList():
    action = DB()
    users = action.getUserList()
    return render_template('core/user-list.html', users=users, active='userList', showpassword=request.args.get('password'))


@mod.route('/delete-user', methods=['POST'])
def deleteUser():
    if request.method == 'POST' and session.get('id') == 1:
        action = DB()
        action.deleteUserById(request.form['inputUserId'])
        return redirect('/user-list')



@mod.route('/settings')
def settings():
    return render_template('core/settings.html', active='settings')


@mod.route('/create-folder-action', methods=['POST'])
def createFolderAction():
    if request.method == 'POST' and session.get('active'):
        string = request.form['inputFolderName']
        action = DB()
        if request.form['inputUser']:
            user_id = request.form['inputUser']
        else:
            user_id = session['id']
        action.createFolder(user_id, string)
        flash('Folder created', 'success')
    return redirect('/')


@mod.route('/signin')
def signin():
    if session.get('active'):
        signout()
    return (render_template('core/signin.html'))


@mod.route('/signin-action', methods=['POST'])
def signinAction(email=None, password=None):
    if request.method == 'POST' or (email and password):
        action = DB()
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        if action.validateUserCreds(email, password):
            session['active'] = True
            userInfo = action.getUserInfoByEmail(email)
            user = User(userInfo[0], userInfo[1], userInfo[2])
            session['first'] = user.first
            session['last'] = user.last
            session['email'] = user.email
            # session['folder'] = user.folder
            user_id = action.getUserIdByEmail(email)
            session['folders'] = action.getFoldersByUserId(user_id)
            session['id'] = user_id
            session['access_level_id'] = 1
            action.recordLogin(user_id)
        elif action.validateGuestCreds(email, password):
            session['active'] = True
            guest_info = action.getGuestInfoByEmail(email)
            guest_id = action.getGuestIdByEmail(email)
            guest_access_info = action.getGuestAccessUserByGuestID(guest_id)
            guest = Guest(guest_info[0], guest_info[1], guest_info[2], guest_access_info[0], guest_access_info[1])
            session['first'] = guest.first
            session['last'] = guest.last
            session['email'] = guest.email
            session['guest_of'] = guest.guest_of
            session['access_level_id'] = guest.access_level_id
            # session['folder'] = user.folder
            session['folders'] = action.getFoldersByUserId(guest.guest_of)
            session['id'] = guest.guest_of
            action.recordLogin(guest.guest_of, guest_id)
        else:
            flash('Email and password don\'t match', 'danger')
            return render_template('core/signin.html')
    return redirect('/')


@mod.route('/signout')
def signout():
    action = DB()
    action.recordLogout(session['id'])
    session.clear()
    flash('Signed out, see you next time!', 'success')
    return redirect('/')


@mod.route('/register')
@mod.route('/register/<hash>')
def register(hash=None):
    if session.get('active'):
        return redirect('/')
    if not hash:
        flash('Open registration isn\'t allowed. Please contact Tim for a register link', 'info')
        return redirect('/signin')
    return (render_template('core/register.html', hash=hash))


@mod.route('/register/guest/<hash>')
def registerGuest(hash=None):
    if session.get('active'):
        return redirect('/')
    if not hash:
        flash('Open registration isn\'t allowed. Please contact Tim for a register link', 'info')
        return redirect('/signin')
    action = DB()
    new_guest_info = action.getNewGuestRegistrationInfoByHash(hash)
    ng_email = new_guest_info[0]
    ng_of = new_guest_info[1]
    ng_access_level_id = new_guest_info[2]
    return (render_template('core/registerguest.html', hash=hash, ng_email=ng_email, ng_of=ng_of, ng_access_level_id=ng_access_level_id))


@mod.route('/register-action', methods=['POST'])
def registerAction():
    if request.method == 'POST':
        action = DB()
        first = request.form['inputFirstName']
        last = request.form['inputLastName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        confirmPassword = request.form['confirmPassword']
        hash = request.form['inputHash']
        if not action.checkHash(hash):
            flash('Register link is no longer valid', 'danger')
            return render_template('core/register.html')
        if action.checkUserExists(email):
            flash('Email already used. Did you mean to log in?', 'danger')
            return render_template('core/register.html')
        if password != confirmPassword:
            flash('Passwords don\'t match', 'danger')
            return render_template('core/register.html')
        if len(password) < 6:
            flash('Password too short', 'danger')
            return render_template('core/register.html')
        registrant = User(first, last, email, password)
        user_id = action.createUser(registrant)
        File().makeDirectory(user_id)
        action.voidHash(hash)
        signinAction(email, password)
    return redirect('/')


@mod.route('/register-guest-action', methods=['POST'])
def registerGuestAction():
    if request.method == 'POST':
        action = DB()
        first = request.form['inputFirstName']
        last = request.form['inputLastName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        confirmPassword = request.form['confirmPassword']
        hash = request.form['inputHash']
        guest_of = request.form['inputGuestOfId']
        access_level_id = request.form['inputAccessLevelId']
        if not action.checkGuestHash(hash) or not guest_of or not access_level_id:
            flash('Register link is no longer valid', 'danger')
            return render_template('core/register.html')
        if action.checkUserExists(email):
            flash('Email already used. Did you mean to log in?', 'danger')
            return render_template('core/register.html')
        if password != confirmPassword:
            flash('Passwords don\'t match', 'danger')
            return render_template('core/register.html')
        if len(password) < 6:
            flash('Password too short', 'danger')
            return render_template('core/register.html')
        registrant = Guest(first, last, email, guest_of, access_level_id, password)
        action.createGuest(registrant)
        action.voidGuestHash(hash, guest_of)
        signinAction(email, password)
    return redirect('/')

@mod.route('/reset-password-action', methods=['POST'])
def resetPasswordAction():
    if request.method == 'POST':
        action = DB()
        newPassword = request.form['inputNewPassword']
        confirmNewPassword = request.form['confirmNewPassword']
        hash = request.form['inputHash']
        if not action.checkPasswordResetHash(hash):
            flash('Password reset is no longer valid', 'danger')
            return redirect('/')
        if newPassword != confirmNewPassword:
            flash('Passwords don\'t match', 'danger')
            return render_template('core/register.html')
        if len(newPassword) < 6:
            flash('Password too short', 'danger')
            return render_template('core/register.html')
        action.resetPassword(newPassword, hash)
        email = action.getUserEmailByUserId(action.getUserIdByPasswordHash(hash))
        flash('Password has been successfully updated.', 'success')
        # signinAction(email, newPassword)
    return redirect('/signin')



