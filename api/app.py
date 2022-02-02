from fileinput import filename
from flask import Flask, jsonify, send_file, request
import models as models
from database import SessionLocal, engine
from getAllFiles import *
from werkzeug.utils import secure_filename
from security import *
app = Flask(__name__)

parent = "assets"

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        # get credentials
        username = ""
        password = ""
        try:
            username = request.get_json()["username"]
            password = request.get_json()["password"]
        except:
            return {"message": "Invalid request"}, 400
        # check if user exists
        user = db.query(models.User).filter(models.User.username == username).first()
        if user == None:
            return {"message": "User not found"}, 404
        # check if password is correct
        if verify_passwd(password, user.password):
            # get access_token for user
            access_token = create_access_token(username)
            return {"access_token": access_token}, 200
        else:
            return {"message": "Incorrect password"}, 401

@app.route("/register", methods=["POST"])
def register():
    # check if registeration allowed
    signup = os.environ.get("SIGNUP")
    if signup == "False":
        return {"message": "Registration is disabled"}, 403
    if request.method == "POST":
        # get credentials
        username = ""
        password = ""
        try:
            username = request.get_json()["username"]
            password = request.get_json()["password"]
        except:
            return {"message": "Invalid request"}, 400
        # check if user exists
        user = db.query(models.User).filter(models.User.username == username).first()
        if user != None:
            return {"message": "User already exists"}, 409
        # create user
        user = models.User(username=username, password=hashMe(password))
        db.add(user)
        db.commit()
        return {"message": "User created"}, 201

@app.route("/")
def index():
    # security check 
    try:
        access_token = request.headers.get("Authorization")
        if verify_token(access_token):
            print(verify_token(access_token), "came!")
        else:
            return {"message": "Invalid access token"}, 401
    except:
        return {"message": "Invalid access token"}, 401
    allFiles = getFiles(parent)
    return jsonify(allFiles)

# file path
@app.route("/<path:path>", methods=["GET", "POST", "DELETE", "PUT"])
def getFile(path):
    # edit path and remove /media. NOTE: This is specific to the DSC-TIET official website project
    path = path.replace("media/", "")
    
    # if request is get
    if request.method == "GET":
        # check if its a file or folder
        if os.path.isdir(os.path.join(parent, path)):
            # authorization
            try:
                access_token = request.headers.get("Authorization")
                if verify_token(access_token):
                    print(verify_token(access_token), "came!")
                else:
                    return {"message": "Invalid access token"}, 401
            except:
                return {"message": "Invalid access token"}, 401

            # All good!
            allFiles = getFiles(os.path.join(parent, path))
            return jsonify(allFiles), 403

        elif os.path.isfile(os.path.join(parent, path)):
            # this is a file
            try:
                return send_file(os.path.join(parent, path))        
            except:
                return "empty file"
        else:
            print(os.path.join(parent,path))
            return {"message": "File not found"}, 404
    
    # if request is post
    elif request.method == "POST":
        # verify access token
        try:
            access_token = request.headers.get("Authorization")
            if verify_token(access_token):
                print(verify_token(access_token), "came!")
            else:
                return {"message": "Invalid access token"}, 401
        except:
            return {"message": "Invalid access token"}, 401
        
        # check if a file or folder exists with the same name
        # check if the user has uploaded a file
        if "file" in request.files:
            file = request.files["file"]
            # check if the file is empty
            if file.filename == "":
                return {"message": "No file selected"}, 400
            # check if the file already exists
            file.filename = file.filename.replace(" ", "_")
            if os.path.isfile(os.path.join(parent, path, file.filename)):
                new_name = ""
                count = 1
                while(os.path.isfile(os.path.join(parent, path, new_name))) or new_name == "":
                    new_name = file.filename + "." + str(count)
                    count += 1
                file.filename = new_name
            # save the file
            file.save(os.path.join(parent, path, file.filename))
            return {"message": "File uploaded"}, 201

        if os.path.exists(os.path.join(parent, path)):
            return {"message": "File already exists"}, 409
        else:
            # create folder recursive
            os.makedirs(os.path.join(parent, path), exist_ok=True)
            return {"message": "Folder created"}, 201

    # delete folder/file
    elif request.method == "DELETE":
        # authorization
        try:
            access_token = request.headers.get("Authorization")
            if verify_token(access_token):
                print(verify_token(access_token), " came!")
            else:
                return {"message": "Invalid access token"}, 401
        except:
            return {"message": "Invalid access token"}, 401
        # check if a file or folder exists with the same name
        if os.path.exists(os.path.join(parent, path)):
            # delete folder recursive
            try:
                # check if its a file
                if os.path.isfile(os.path.join(parent, path)):
                    # remove
                    os.remove(os.path.join(parent, path))
                    return {"message": "File deleted"}, 200
                os.rmdir(os.path.join(parent, path))
            except OSError as e:
                return {"message": "Folder not empty"}, 409
            return {"message": "Folder deleted"}, 200
        else:
            return {"message": "File or folder not found"}, 404
    
    # rename folder/file
    elif request.method == "PUT":
        # authorization
        try:
            access_token = request.headers.get("Authorization")
            if verify_token(access_token):
                print(verify_token(access_token), " came!")
            else:
                return {"message": "Invalid access token"}, 401
        except:
            return {"message": "Invalid access token"}, 401
        # get the new name from request body
        try:
            newName = request.get_json()["newName"]
        except:
            return {"message": "Invalid request"}, 400
        # remove spaces from new name
        newName = newName.replace(" ", "_")
        # check if a file or folder exists with the same name
        if os.path.exists(os.path.join(parent, path)):
            # rename folder
            try:
                os.rename(os.path.join(parent, path), os.path.join(parent, newName))
            except OSError as e:
                return {"message": "File already exists"}, 409
            return {"message": "File renamed"}, 200
        else:
            return {"message": "File or folder not found"}, 404
