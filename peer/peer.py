import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import requests  
import socket
import threading


# Define the path for the user state file
USER_STATE_PATH = os.path.join(os.getenv('USERPROFILE'), 'ProgramFiles', 'P2P_fileShare', 'user_state.json')

# Tracker server URL (to send user registration data)
TRACKER_SERVER_URL = "http://172.16.88.86:5005"  

# Defining port 5006 as listening port on all peers and assuming it is free on all peers , to be used by 
# p2p application




# user registation block--->

def get_peer_address():
    try:
        # sending a dummy packet to get the local ip of machine
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error getting peer address: {e}")
        return "Unknown"

# Save user state after registration
def save_user_state(username):
    os.makedirs(os.path.dirname(USER_STATE_PATH), exist_ok=True)  # Create directory if it doesn't exist
    user_data = {"username": username}
    with open(USER_STATE_PATH, 'w') as f:
        json.dump(user_data, f)

# Clear user state (optional, for logout functionality)
def clear_user_state():
    if os.path.exists(USER_STATE_PATH):
        os.remove(USER_STATE_PATH)

# Send registration data to the tracker server
def register_user_on_server(username):
    try:
        peer_address = get_peer_address()  # Get the local peer address
        response = requests.post(TRACKER_SERVER_URL+"/register_user", json={"username": username,"peer_address": peer_address  })
        if response.status_code == 200:
            messagebox.showinfo("Success", "User registered successfully!")
            return True
        else:
            messagebox.showerror("Error", f"Failed to register user: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error contacting tracker server: {e}")
        return False

# Function to handle user registration
def show_register_screen():
    register_window = tk.Tk()
    register_window.title("Register for P2P File Share")
    register_window.geometry("400x300")

    def on_register():
        username = username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return
        
        # Register user on the tracker server
        if register_user_on_server(username):
            save_user_state(username)  
            register_window.destroy() 
            threading.Thread(target=start_peer_server, daemon=True).start()
            open_main_page(username) 

    # Registration form
    username_label = tk.Label(register_window, text="Enter Username:", font=("Arial", 12))
    username_label.pack(pady=10)

    username_entry = tk.Entry(register_window)
    username_entry.pack(pady=5)

    register_button = tk.Button(register_window, text="Register", command=on_register)
    register_button.pack(pady=20)

    register_window.mainloop()






#main page ---->
def open_main_page(username):
    main_page = tk.Tk()
    main_page.title("Main Program")
    main_page.geometry("600x400")
    
    welcome_label = tk.Label(main_page, text=f"Welcome, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=20)
    
    add_file_button = tk.Button(main_page, text="Add File", command=lambda: open_file_dialog(username,history_box))
    add_file_button.pack(pady=10)
    
    search_file_button = tk.Button(main_page, text="Search Files", command=lambda: open_search_window(username))
    search_file_button.pack(pady=10)

    # File history section
    history_label = tk.Label(main_page, text="Uploaded Files History", font=("Arial", 14))
    history_label.pack(pady=10)

    history_box = tk.Listbox(main_page, width=50, height=10)
    history_box.pack(pady=10)
    
    # Load previously added files from user data
    load_file_history(history_box, username)

    main_page.mainloop()





#feature -> searching file on tracker server

def open_search_window(username):
    search_window = tk.Toplevel()
    search_window.title("Searched Files")
    search_window.geometry("500x300")

    # Search bar for entering keyword
    search_label = tk.Label(search_window, text="Search Keyword:")
    search_label.pack(pady=5)
    
    search_entry = tk.Entry(search_window, width=40)
    search_entry.pack(pady=5)

    # Dropdown for selecting file type
    filetype_label = tk.Label(search_window, text="Select File Type:")
    filetype_label.pack(pady=5)

    filetype_var = tk.StringVar(search_window)
    filetype_var.set("all")  # Default value for dropdown (can search all file types)

    filetype_options = ["all", "text", "audio", "image", "video", "document", "other"]
    filetype_dropdown = tk.OptionMenu(search_window, filetype_var, *filetype_options)
    filetype_dropdown.pack(pady=5)

    # Lower and upper bound inputs for file size
    size_label = tk.Label(search_window, text="Enter file size range (in bytes):")
    size_label.pack(pady=5)

    low_size_label = tk.Label(search_window, text="Min size:")
    low_size_label.pack(pady=2)

    low_size_entry = tk.Entry(search_window, width=10)
    low_size_entry.pack(pady=2)

    high_size_label = tk.Label(search_window, text="Max size:")
    high_size_label.pack(pady=2)

    high_size_entry = tk.Entry(search_window, width=10)
    high_size_entry.pack(pady=2)

    # Button to trigger search
    search_button = tk.Button(search_window, text="Search", command=lambda: perform_file_search(search_entry.get(), filetype_var.get(), low_size_entry.get(), high_size_entry.get(), username))
    search_button.pack(pady=10)

def perform_file_search(keyword, filetype, min_size, max_size, username):
    search_params = {}
    
    if keyword:
        search_params['filename'] = keyword
    if filetype != "all":
        search_params['filetype'] = filetype
    if min_size.isdigit():
        search_params['min_filesize'] = int(min_size)
    if max_size.isdigit():
        search_params['max_filesize'] = int(max_size)
    
    try:
        # Send search request to the server
        response = requests.get(f"{TRACKER_SERVER_URL}/query_files", params=search_params)
        
        if response.status_code == 200:
            result_data = response.json()
            open_search_results_window(result_data)  # Display search results
        else:
            messagebox.showerror("Error", f"Failed to search files: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error contacting tracker server: {e}")


def is_peer_online(peer_address):
    try:
        # Try to connect to peer at port 5006 to check if it's online on that peer
        with socket.create_connection((peer_address, 5006), timeout=0.6):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def open_search_results_window(result_data):
    search_output_window = tk.Toplevel()
    search_output_window.title("Search Results")
    search_output_window.geometry("800x600")

    results_label = tk.Label(search_output_window, text="Search Results", font=("Arial", 14))
    results_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

    if not result_data:
        empty_label = tk.Label(search_output_window, text="No files found matching the search criteria.")
        empty_label.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        return

    # Create headers for the columns
    tk.Label(search_output_window, text="File").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(search_output_window, text="Comment").grid(row=1, column=1, padx=10, pady=5)
    tk.Label(search_output_window, text="Size (bytes)").grid(row=1, column=2, padx=10, pady=5)
    tk.Label(search_output_window, text="Peer").grid(row=1, column=3, padx=10, pady=5)
    tk.Label(search_output_window, text="Status").grid(row=1, column=4, padx=10, pady=5)
    tk.Label(search_output_window, text="Action").grid(row=1, column=5, padx=10, pady=5)

    # Iterate over results and display each file's details
    for index, file_info in enumerate(result_data, start=2):  # Start from row 2 (after the headers)
        filename = file_info["filename"]
        comments=file_info["comments"]
        filesize = file_info["filesize"]
        peer_name = file_info["peer_name"]
        peer_address = file_info["peer_address"]

        # Create labels for file details
        filename_label = tk.Label(search_output_window, text=os.path.basename(filename))
        filename_label.grid(row=index, column=0, padx=10, pady=5)

        comments_label = tk.Label(search_output_window, text=comments)
        comments_label.grid(row=index, column=1, padx=10, pady=5)

        filesize_label = tk.Label(search_output_window, text=filesize)
        filesize_label.grid(row=index, column=2, padx=10, pady=5)

        peer_label = tk.Label(search_output_window, text=peer_name)
        peer_label.grid(row=index, column=3, padx=10, pady=5)

        # Check peer online status
        peer_status = "Online" if is_peer_online(peer_address) else "Offline"
        status_label = tk.Label(search_output_window, text=peer_status)
        status_label.grid(row=index, column=4, padx=10, pady=5)

        # Download button (with file path selection)
        def on_download(peer_address, filename):
             download_path = filedialog.askdirectory()
             if download_path:
                 download_file_from_peer(peer_address, filename, download_path)

        # Enable the download button only for online peers
        button_state = 'normal'  if peer_status == 'Online' else 'disabled'

        download_button = tk.Button(search_output_window, text="Download", command=lambda peer_address=peer_address, filename=filename: on_download(peer_address, filename), state=button_state)
        download_button.grid(row=index, column=5, padx=10, pady=5)






# Feature -> ( adding file to server )

def open_file_dialog(username,history_box):
    # Open file dialog to select a file
    file_path = filedialog.askopenfilename()
    if file_path:
        # Extract filename and size
        filename = file_path
        filesize = os.path.getsize(file_path)
        
        # Create a new window to input the comment
        comment_window = tk.Toplevel()
        comment_window.title(f"Add Comment for {os.path.basename(file_path)}")
        comment_window.geometry("400x200")
        
        comment_label = tk.Label(comment_window, text="Enter Comment:")
        comment_label.pack(pady=10)
        
        comment_entry = tk.Entry(comment_window)
        comment_entry.pack(pady=10)

        # Add a label and dropdown for selecting file type
        filetype_label = tk.Label(comment_window, text="Select File Type:")
        filetype_label.pack(pady=5)

        filetype_var = tk.StringVar(comment_window)
        filetype_var.set("text")  # Default value for dropdown

        filetype_options = ["text", "audio", "image", "video", "document", "other"]
        filetype_dropdown = tk.OptionMenu(comment_window, filetype_var, *filetype_options)
        filetype_dropdown.pack(pady=5)

        

        def on_add_file():
            comment = comment_entry.get().strip()
            if comment == "":
                comment = None  # Optional, can be None if no comment
            
            # Add file details to the server
            filetype = filetype_var.get()
            if upload_file_to_server( filename, filesize, comment,filetype, username):
                comment_window.destroy()  # Close the comment input window
                # Update the history box after a successful upload
                update_file_history(username, os.path.basename(filename), comment)
                load_file_history(history_box, username)
        
        # Button to confirm adding the file
        add_file_button = tk.Button(comment_window, text="Add File", command=on_add_file)
        add_file_button.pack(pady=20)


def upload_file_to_server( filename, filesize, comment,filetype, username):
    """ Send the file metadata and add it to the server """
    try:
        # Send metadata (filename, size, comment, username) to the server
        response = requests.post(f"{TRACKER_SERVER_URL}/upload_file", json={
            "filename": filename,
            "filetype": filetype,  # Placeholder for file type
            "filesize": filesize,
            "peer_name": username,
            "comments": comment
        })
        
        if response.status_code == 200:
            messagebox.showinfo("Success", "File uploaded successfully!")
            # You can add logic here to store the file information locally for history
            return True
        else:
            messagebox.showerror("Error", f"Failed to upload file: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error contacting tracker server: {e}")
        return False


#feature -> showing user's file history

# Load file history from the user's local data
def load_file_history(history_box, username):
    history_box.delete(0, tk.END)  # Clear the history box before reloading
    try:
        # Load the user's data from the user_state.json
        with open(USER_STATE_PATH, 'r') as f:
            user_data = json.load(f)
            if "uploaded_files" in user_data:
                for file in user_data["uploaded_files"]:
                    history_box.insert(tk.END, f"{file['filename']} ({file['comments']})")
    except Exception as e:
        print(f"Error loading file history: {e}")

# Update file history locally after a successful upload
def update_file_history(username, filename, comment):
    try:
        # Load the user's data from user_state.json
        with open(USER_STATE_PATH, 'r') as f:
            user_data = json.load(f)

        # Ensure the "uploaded_files" key exists
        if "uploaded_files" not in user_data:
            user_data["uploaded_files"] = []

        # Add the new file to the list
        user_data["uploaded_files"].append({
            "filename": filename,
            "comments": comment if comment else "No comment"
        })

        # Save the updated user data
        with open(USER_STATE_PATH, 'w') as f:
            json.dump(user_data, f)
    except Exception as e:
        print(f"Error updating file history: {e}")







#file upload download start here ( tcp like)

# listening server for file requests
def start_peer_server():
    def handle_client_connection(client_socket):
        try:
            requested_file = client_socket.recv(1024).decode('utf-8')
            print(f"Peer requested file: {requested_file}")
            
            # Find and open the requested file
            if os.path.exists(requested_file):
                with open(requested_file, 'rb') as f:
                    file_data = f.read()
                
                # Send file size first
                client_socket.send(str(len(file_data)).encode('utf-8'))
                
                # Wait for acknowledgment
                client_socket.recv(1024)
                
                # Send the actual file data
                client_socket.sendall(file_data)
                print(f"File {requested_file} sent successfully.")
            else:
                client_socket.send(b'ERROR: File not found.')
        except Exception as e:
            print(f"Error sending file: {e}")
        finally:
            client_socket.close()

    # Create a socket to listen on port 5006
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 5006))  # Bind to all available interfaces
    server_socket.listen(5)
    print("Peer server started, listening for file requests on port 5006.")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        # Handle file requests in a new thread
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()


def download_file_from_peer(peer_address, filename, download_path):
    if not filename:
        messagebox.showerror("Error", "Invalid filename provided.")
        print("Error: Invalid filename provided.")
        return

    try:
       
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_address, 5006))
            s.send(filename.encode('utf-8'))  # Request the file

            # Receive the file size first
            file_size_data = s.recv(1024)
            if not file_size_data:
                raise ValueError("Failed to receive file size from the peer.")

            file_size = int(file_size_data.decode('utf-8'))
            if file_size <= 0:
                raise ValueError("Received invalid file size.")

            s.send(b'ACK')  # Send acknowledgment

            # Receive the actual file data
            file_data = b""
            while len(file_data) < file_size:
                packet = s.recv(1024)
                if not packet:
                    raise ValueError("Connection lost or failed to receive complete file data.")
                file_data += packet

            # Save the file to the specified download path
            with open(os.path.join(download_path, os.path.basename(filename)), 'wb') as f:
                f.write(file_data)

            messagebox.showinfo("Download Success", f"File {filename} downloaded successfully.")
            print(f"File {filename} downloaded successfully.")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download file: {e}")
        print(f"Error downloading file: {e}")






#checking if user already registered ( direct login )
def check_user_state(): 
    if os.path.exists(USER_STATE_PATH):
        with open(USER_STATE_PATH, 'r') as f:
            user_data = json.load(f)
            if user_data.get("username"):
                return user_data
    return None

def main():
    user_data = check_user_state()

    if not user_data: # showing register screen if not registered
        show_register_screen()
    
    else :
        username = user_data["username"]
        threading.Thread(target=start_peer_server, daemon=True).start()
        open_main_page(username)

# Run the application
main()
