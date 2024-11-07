from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'  # SQLite database for tracking users and files
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model with peer_address column
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    peer_address = db.Column(db.String(100), nullable=True)  # Added column for peer address

# Define the File model with a comments column
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False) # it will store the whole file address + name
    filetype = db.Column(db.String(50), nullable=False)
    filesize = db.Column(db.Integer, nullable=False)
    peer_name = db.Column(db.String(100), nullable=False)  # Peer who uploaded the file
    comments = db.Column(db.String(500), nullable=True)

# Manually create the database tables when the server starts
with app.app_context():
    db.create_all()

# User Registration Endpoint
@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    peer_address = data.get('peer_address')  # Get peer address from request

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists!"}), 400

    # Register new user
    new_user = User(username=username, peer_address=peer_address)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 200

# File Upload Endpoint (for registering file metadata)
@app.route('/upload_file', methods=['POST'])
def upload_file():
    data = request.get_json()
    filename = data.get('filename')
    filetype = data.get('filetype')
    filesize = data.get('filesize')
    peer_name = data.get('peer_name')
    comments = data.get('comments', '')  # Optional comments field

    # Store the file metadata in the database
    new_file = File(filename=filename, filetype=filetype, filesize=filesize, peer_name=peer_name, comments=comments)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully!"}), 200

# Query Files Endpoint (with parameters)
@app.route('/query_files', methods=['GET'])
def query_files():
    filename = request.args.get('filename', default='', type=str)
    filetype = request.args.get('filetype', default='', type=str)
    min_filesize = request.args.get('min_filesize', default=None, type=int)
    max_filesize = request.args.get('max_filesize', default=None, type=int)

    # Perform the query
    query = File.query

    if filename:
        query = query.filter(
            (File.filename.ilike(f'%{filename.lower()}%')) |  # Search in filename
            (File.comments.ilike(f'%{filename.lower()}%'))   # Search in comments
        )

    if filetype:
        query = query.filter(File.filetype == filetype)

    if min_filesize is not None:
        query = query.filter(File.filesize >= min_filesize)

    if max_filesize is not None:
        query = query.filter(File.filesize <= max_filesize)

    files = query.all()

    # If no files match, return an empty response
    if not files:
        return jsonify([]), 200

    # Prepare the response data with peer_address from User table
    result = []
    for file in files:
        user = User.query.filter_by(username=file.peer_name).first()
        peer_address = user.peer_address if user else "Unknown"  # Default to 'Unknown' if no peer address is found

        result.append({
            "filename": file.filename,
            "filetype": file.filetype,
            "filesize": file.filesize,
            "peer_name": file.peer_name,
            "comments": file.comments,
            "peer_address": peer_address
        })

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
