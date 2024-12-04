import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import json
import requests  
import socket
import threading

# Defining port 5006 as listening port on all peers and assuming it is free on all peers , to be used by 
# p2p application

# Define the path for the user state file
USER_STATE_PATH = os.path.join(os.getenv('USERPROFILE'), 'ProgramFiles', 'P2P_fileShare', 'user_state.json')

# Tracker server URL (to send user registration data)
TRACKER_SERVER_URL = "http://172.16.88.86:5005"  

#checking if user already registered ( direct login )
def check_user_state(): 
    if os.path.exists(USER_STATE_PATH):
        with open(USER_STATE_PATH, 'r') as f:
            user_data = json.load(f)
            if user_data.get("username"):
                return user_data
    return None

#user state for global acces
user_data = check_user_state()



#some common design elements ->
# Function to create a header
def create_header(parent, text):
    header_label = tk.Label(
        parent,
        text=text,
        font=("Helvetica", 18, "bold"),
        bg="#198AA0",
        fg="white",
        padx=10,
        pady=10,
    )
    header_label.pack(fill="x")

# Function to create an instruction label
def create_instruction_label(parent, text):
    instruction_label = tk.Label(
        parent,
        text=text,
        font=("Arial", 12),
        bg="#B1F6E6",
        fg="#333333",
    )
    instruction_label.pack(pady=(20, 10))

# Function to create a styled button
def create_button(parent, text, command):
    button = tk.Button(
        parent,
        text=text,
        font=("Arial", 14, "bold"),
        bg="#198AA0",
        fg="white",
        activebackground="#106A7B",
        activeforeground="white",
        command=command,
    )
    return button

# function for center aligning window 
def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width // 2) - (width // 2)
    y_coordinate = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")





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
    register_window.geometry("600x470")
    register_window.configure(bg="#B1F6E6")

    # Center-aligning window on the screen
    center_window(register_window, 600, 470)

    # Create UI components
    create_header(register_window, "Welcome to P2P File Share")
    create_instruction_label(register_window, "Please register by entering your username below:")

    # Username input
    username_label = tk.Label(
        register_window, text="Enter Username:", font=("Arial", 12), bg="#B1F6E6", fg="#333333"
    )
    username_label.pack(pady=(10, 5))

    username_entry = tk.Entry(register_window, font=("Arial", 12), width=30)
    username_entry.pack(ipady=5, pady=5)

    # On register button click
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

    # Create Register button
    register_button = create_button(register_window, "Register", on_register)
    register_button.pack(pady=(20, 0), ipadx=20, ipady=5)

    # Footer note
    footer_label = tk.Label(
        register_window, text="© 2024 - made by Harshvardhan and his AI friend (chatgpt not ammar).",
        font=("Arial", 10),
        bg="#B1F6E6",
        fg="#666666",
    )
    footer_label.pack(side="bottom", pady=10)

    # Mainloop to run the application
    register_window.mainloop()






#main page ---->
def open_main_page(username):
    main_page = tk.Tk()
    main_page.title("Main Program")
    main_page.geometry("1000x700")
    main_page.configure(bg="#B1F6E6")

    # Center-aligning window on the screen
    center_window(main_page, 1000, 700)

    # Create UI components
    create_header(main_page, f"Welcome, {username}!")
    create_instruction_label(main_page, "Use the buttons below to manage your files:")

    # Horizontal frame for buttons
    button_frame = tk.Frame(main_page, bg="#B1F6E6")
    button_frame.pack(pady=(20, 10))

    # Add File button
    add_file_button = create_button(
        button_frame, "Add File", command=lambda: open_file_dialog(username, history_box)
    )
    add_file_button.pack(side="left", padx=10, ipadx=20, ipady=5)

    # Search Files button
    search_file_button = create_button(
        button_frame, "Search Files", command=lambda: open_search_window(username)
    )
    search_file_button.pack(side="left", padx=10, ipadx=20, ipady=5)

    # File history section
    history_label = tk.Label(
        main_page,
        text="Uploaded Files History",
        font=("Arial", 14, "bold"),
        bg="#B1F6E6",
        fg="#333333",
    )
    history_label.pack(pady=(30, 10))

    history_box = tk.Listbox(main_page, width=130, height=25)
    history_box.pack(pady=10, padx=20)

    # Load previously added files from user data
    load_file_history(history_box, username)

    # Mainloop to run the application
    main_page.mainloop()





#feature -> searching file on tracker server
def open_search_window(username):
    search_window = tk.Toplevel()
    search_window.title("Searched Files")
    search_window.geometry("600x430")
    center_window(search_window, 600, 430)
    search_window.configure(bg="#B1F6E6")

    # Header
    create_header(search_window, "Search Files")

    # Search bar for entering a keyword
    create_instruction_label(search_window, "Enter Search Keyword:")
    search_entry = tk.Entry(search_window, font=("Arial", 12), width=30)
    search_entry.pack(pady=5)

    # Dropdown for selecting file type
    create_instruction_label(search_window, "Select File Type:")
    filetype_var = tk.StringVar(search_window)
    filetype_var.set("all")  # Default value for dropdown (can search all file types)
    filetype_options = ["all", "text", "audio", "image", "video", "document", "other"]
    filetype_dropdown = tk.OptionMenu(search_window, filetype_var, *filetype_options)
    filetype_dropdown.config(
            font=("Arial", 12),
            bg="#198AA0",
            fg="white",
            activebackground="#106A7B",
            activeforeground="white",
        )
    filetype_dropdown.pack(pady=5)

    # File size range input
    create_instruction_label(search_window, "Enter File Size Range (in Mega Bytes):")
    size_frame = tk.Frame(search_window, bg="#B1F6E6")
    size_frame.pack(pady=5)

    # Align Min and Max size input fields on the same row
    low_size_label = tk.Label(size_frame, text="Min size:", font=("Arial", 12), bg="#B1F6E6")
    low_size_label.grid(row=0, column=0, padx=(5, 10))

    low_size_entry = tk.Entry(size_frame, font=("Arial", 12), width=10)
    low_size_entry.grid(row=0, column=1, padx=(0, 10))

    high_size_label = tk.Label(size_frame, text="Max size:", font=("Arial", 12), bg="#B1F6E6")
    high_size_label.grid(row=0, column=2, padx=(5, 10))

    high_size_entry = tk.Entry(size_frame, font=("Arial", 12), width=10)
    high_size_entry.grid(row=0, column=3, padx=(0, 10))

    # Search button
    search_button = create_button(
        search_window,
        "Search",
        lambda: perform_file_search(
            search_entry.get(),
            filetype_var.get(),
            low_size_entry.get(),
            high_size_entry.get(),
            username,
            search_window
        )
    )
    search_button.pack(pady=10)

def perform_file_search(keyword, filetype, min_size, max_size, username,par_window):
    search_params = {}
    
    if keyword:
        search_params['filename'] = keyword
    if filetype != "all":
        search_params['filetype'] = filetype
    if min_size.isdigit():
        search_params['min_filesize'] = int(min_size)*1024*1024
    if max_size.isdigit():
        search_params['max_filesize'] = int(max_size)*1024*1024
    
    try:
        # Send search request to the server
        response = requests.get(f"{TRACKER_SERVER_URL}/query_files", params=search_params)
        
        if response.status_code == 200:
            result_data = response.json()
            open_search_results_window(result_data,par_window)  # Display search results
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

def open_search_results_window(result_data,par_window):
    search_output_window = tk.Toplevel()
    search_output_window.title("Search Results")
    search_output_window.configure(bg="#B1F6E6")
    search_output_window.geometry("1000x700")
    center_window(search_output_window, 1000, 700)

    # Create header for the window
    create_header(search_output_window, "Search Results")

    if not result_data:
        create_instruction_label(search_output_window, "No files found matching the search criteria.")
        return

    # Create container frame for grid layout
    results_frame = tk.Frame(search_output_window, bg="#B1F6E6")
    results_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create headers for the result columns
    headers = ["File", "Comment", "Size (MB)", "Peer", "Status", "Action"]
    for col, header in enumerate(headers):
        tk.Label(results_frame, text=header, font=("Arial", 12, "bold"), bg="#198AA0", fg="white") \
            .grid(row=0, column=col, padx=10, pady=5, sticky="ew")

    # Populate the search results
    for index, file_info in enumerate(result_data, start=1):
        filename = os.path.basename(file_info["filename"])
        comments = file_info["comments"]
        filesize = file_info["filesize"]
        filesize = round(filesize / (1024 * 1024), 3)
        peer_name = file_info["peer_name"]
        peer_address = file_info["peer_address"]

        # Check peer online status
        peer_status = "Online" if is_peer_online(peer_address) else "Offline"

        # Add file details to the grid
        tk.Label(results_frame, text=filename, bg="#B1F6E6", fg="#333333").grid(row=index, column=0, padx=10, pady=5)
        tk.Label(results_frame, text=comments, bg="#B1F6E6", fg="#333333").grid(row=index, column=1, padx=10, pady=5)
        tk.Label(results_frame, text=filesize, bg="#B1F6E6", fg="#333333").grid(row=index, column=2, padx=10, pady=5)
        tk.Label(results_frame, text=peer_name, bg="#B1F6E6", fg="#333333").grid(row=index, column=3, padx=10, pady=5)
        tk.Label(results_frame, text=peer_status, bg="#B1F6E6", fg="#333333").grid(row=index, column=4, padx=10, pady=5)

        # Download button (enabled only for online peers)
        def on_download(peer_address=peer_address, filename=file_info["filename"]):
            download_path = filedialog.askdirectory()
            if download_path:
                download_file_from_peer(peer_address, filename, download_path)

        button_state = "normal" if peer_status == "Online" else "disabled"
        tk.Button(
            results_frame, 
            text="Download", 
            state=button_state, 
            command=on_download,
            bg="#198AA0", fg="white", font=("Arial", 10, "bold"), 
            activebackground="#106A7B", activeforeground="white"
        ).grid(row=index, column=5, padx=10, pady=5)
    par_window.destroy()






# Feature -> ( adding file to server )

def open_file_dialog(username, history_box):
    # Open file dialog to select a file
    file_path = filedialog.askopenfilename()
    if file_path:
        # Extract filename and size
        filename = file_path
        filesize = os.path.getsize(file_path)

        # Create a new window to input the comment
        comment_window = tk.Toplevel()
        comment_window.title(f"Add Comment for {os.path.basename(file_path)}")
        comment_window.geometry("600x400")
        comment_window.configure(bg="#B1F6E6")

        # Center-aligning the window on the screen
        center_window(comment_window, 600, 400)

        # Add header
        create_header(comment_window, f"Add Comment for {os.path.basename(file_path)}")

        # Comment input
        comment_label = tk.Label(
            comment_window,
            text="Enter Comment:",
            font=("Arial", 12),
            bg="#B1F6E6",
            fg="#333333",
        )
        comment_label.pack(pady=(10, 5))

        comment_entry = tk.Text(comment_window, font=("Arial", 12), width=30, height=5, wrap="word")
        comment_entry.pack(pady=5)

        # File type dropdown
        filetype_label = tk.Label(
            comment_window,
            text="Select File Type:",
            font=("Arial", 12),
            bg="#B1F6E6",
            fg="#333333",
        )
        filetype_label.pack(pady=(10, 5))

        filetype_var = tk.StringVar(comment_window)
        filetype_var.set("text")  # Default value

        filetype_options = ["text", "audio", "image", "video", "document", "other"]
        filetype_dropdown = tk.OptionMenu(comment_window, filetype_var, *filetype_options)
        filetype_dropdown.config(
            font=("Arial", 12),
            bg="#198AA0",
            fg="white",
            activebackground="#106A7B",
            activeforeground="white",
        )
        filetype_dropdown.pack(pady=5)

        # Function to handle adding file
        def on_add_file():
            comment =comment_entry.get("1.0", "end-1c").strip()
            if not comment:
                comment = None  # Optional, set to None if no comment provided

            # Add file details to the server
            filetype = filetype_var.get()
            if upload_file_to_server(filename, filesize, comment, filetype, username):
                comment_window.destroy()  # Close the comment input window
                # Update the history box after successful upload
                update_file_history(username, os.path.basename(filename), comment)
                load_file_history(history_box, username)

        # Styled "Add File" button
        add_file_button = create_button(comment_window, "Add File", on_add_file)
        add_file_button.pack(pady=(20, 0), ipadx=20, ipady=5)

        # Mainloop to run the comment window
        comment_window.mainloop()


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

def show_progress_bar(filename, username, file_size, mode="Upload"):
    # Create a new window for the progress bar
    progress_window = tk.Toplevel()
    progress_window.title(f"{mode} Progress")

    # Display filename and username with conditional text
    if mode == "Upload":
        label_text = f"Uploading {filename} to user: {username}"
    else:  # mode == "Download"
        label_text = f"Downloading {filename} from user: {username}"
    
    tk.Label(progress_window, text=label_text).pack(pady=5)

    # Create a progress bar widget
    progress = ttk.Progressbar(progress_window, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=10)
    progress["maximum"] = file_size

    # Label to show the current progress percentage
    status_label = tk.Label(progress_window, text="Progress: 0%")
    status_label.pack()

    def update_progress(bytes_processed):
        # Update progress bar and status label
        progress["value"] = bytes_processed
        status_label.config(text=f"Progress: {bytes_processed / file_size * 100:.2f}%")
        progress_window.update_idletasks()

    return progress_window, update_progress


# listening server for file requests
def start_peer_server():
    def handle_client_connection(client_socket):
        try:
            # Receive username and requested file name
            username = client_socket.recv(1024).decode('utf-8')
            requested_file = client_socket.recv(1024).decode('utf-8')
            print(f"Peer {username} requested file: {requested_file}")

            # Create progress window for the uploader
            if os.path.exists(requested_file):
                print("difj")
                with open(requested_file, 'rb') as f:
                    file_data = f.read()
                file_size = len(file_data)

                # Show progress bar
                progress_window, update_progress = show_progress_bar(requested_file, username, file_size, mode="Upload")

                # Send file size and username to the client
                client_socket.send(f"{user_data["username"]},{file_size}".encode('utf-8'))

                 # Send the actual file data with progress updates
                bytes_sent = 0
                chunk_size = 1024*500
                for i in range(0, file_size, chunk_size):
                    chunk = file_data[i:i + chunk_size]
                    client_socket.sendall(chunk)
                    bytes_sent += len(chunk)
                    update_progress(bytes_sent)

                print(f"File {requested_file} sent successfully.")
                messagebox.showinfo("Upload Complete", f"File {requested_file} uploaded successfully.")

                #only close connection when peer have donwloaded file
                completion_message = client_socket.recv(1024).decode('utf-8')


            else:
                client_socket.send(b'ERROR: File not found.')
        except Exception as e:
            print(f"Error sending file: {e}")
        finally:
            client_socket.close()
            if 'progress_window' in locals():
                progress_window.destroy()

    # Create a socket to listen on port 5006
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 5006))
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
            s.send(user_data["username"].encode('utf-8'))  # Send your username
            s.send(filename.encode('utf-8'))  # Request the file

            # Receive username and file size first
            file_info = s.recv(1024).decode('utf-8')
            if not file_info:
                raise ValueError("Failed to receive file information from the peer.")
            
            username, file_size = file_info.split(',')
            file_size = int(file_size)

            # Show progress bar for the downloader
            progress_window, update_progress = show_progress_bar(filename, username, file_size, mode="Download")

            # Send acknowledgment
            s.send(b'ACK')

            # Receive the actual file data
            file_data = b""
            bytes_received = 0
            while len(file_data) < file_size:
                packet = s.recv(1024)
                if not packet:
                    raise ValueError("Connection lost or failed to receive complete file data.")
                file_data += packet
                bytes_received += len(packet)
                update_progress(bytes_received)

            # Save the file to the specified download path
            with open(os.path.join(download_path, os.path.basename(filename)), 'wb') as f:
                f.write(file_data)

            messagebox.showinfo("Download Success", f"File {filename} downloaded successfully.")

            #wait for sender
            s.send(b'Completed')
            print(f"File {filename} downloaded successfully.")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download file: {e}")
        print(f"Error downloading file: {e}")
    finally:
        if 'progress_window' in locals():
            progress_window.destroy()







def main():
    if not user_data: # showing register screen if not registered
        show_register_screen()
    
    else :
        username = user_data["username"]
        threading.Thread(target=start_peer_server, daemon=True).start()
        open_main_page(username)

# Run the application
main()
