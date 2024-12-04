# P2P LAN File Sharing System

A peer-to-peer (P2P) file sharing system designed for seamless file discovery, sharing, and transfer over a local area network (LAN). The system leverages a tracker server for peer and file discovery, while all file-sharing operations are conducted directly between peers.

## System Layout
- **Peer-to-Peer Architecture**: File sharing and transfer are fully decentralized.
- **Tracker Server**: Facilitates peer registration and maintains metadata for file discovery.
  - Peers register with the tracker server and upload file metadata.
  - Other peers query the tracker server to discover files and their locations.

## Features
- **User Registration**: 
  - First-time users register and their state is stored locally (`C://users/<username>`), enabling automatic login on subsequent launches.
- **File Sharing**: Add file metadata to the tracker server to make files discoverable.
- **Search Functionality**: Search for files with support for categorization.
- **FTP-like Protocol**: Efficient upload and download of shared files.
- **LAN Connectivity**: Facilitates local peer-to-peer connections.
- **Enhanced User Interface**: Built using the Python Tkinter library.

### Additional Features
- **File Categorization**: Supports categories such as audio, video, text, etc.
- **File Comments**: Add comments when sharing files.
- **Network Discovery**: Check the online status of peers.
- **Progress Bars**: Displays upload and download progress.

## Technology Used
- **Programming Language**: Python
- **Tracker Server**: Built using Flask and SQLite for database management.
- **Peer Application**:
  - Socket and request libraries for file transfers.
  - Thread library for handling concurrent tasks.
  - Tkinter for building a user-friendly interface.

## Video Demonstration
For a detailed walkthrough of this Project, please watch the following video:
[![Watch the video](https://img.youtube.com/vi/ljjtaA0QRGY/0.jpg)](https://www.youtube.com/watch?v=ljjtaA0QRGY)


## How It Works
1. **Registration**: Users register with the tracker server, which stores their details.
2. **File Sharing**: Users add file metadata (e.g., name, category, comments) to the tracker server.
3. **Search**: Peers search the tracker server for files and their corresponding hosts.
4. **Transfer**: Direct peer-to-peer connections are established for uploading and downloading files.
5. **Network Discovery**: Online peers are identified by pinging them over the network.

## Installation
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the tracker server and copy the private hosted ip address of it.
4. Paste it in Peer.py file in the start and run peer.py program
5. Enjoy sharing!!!

## Future Enhancements
- Support for additional network protocols.
- Implement File security and System security

---

