import imaplib
import email
from email.header import decode_header
from tkinter import *
from tkinter import messagebox, simpledialog, Scrollbar
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def connect_to_email():
    try:
        print("Connecting to email server...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        print("Connected successfully.")
        return mail
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
        return None

def fetch_emails(search_criteria="ALL"):
    mail = connect_to_email()
    if mail:
        try:
            print(f"Searching emails with criteria: {search_criteria}")
            result, data = mail.search(None, search_criteria)
            email_ids = data[0].split()
            print(f"Found {len(email_ids)} emails.")

            inbox_list.delete(0, END)  # Clear the listbox before inserting new items

            for num in email_ids[:50]:  # Limit to first 50 emails for testing
                result, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Decode email subject and sender
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")
                
                inbox_list.insert(END, f"From: {from_} | Subject: {subject}")

            print("Emails fetched and displayed successfully.")
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Failed to fetch emails: {str(e)}")
        finally:
            mail.logout()
    else:
        print("Failed to connect to email server.")

def search_emails():
    search_criteria = simpledialog.askstring("Search", "Enter search criteria (e.g., 'FROM \"example@example.com\"'):")
    if search_criteria:
        fetch_emails(search_criteria)

def show_email_details(event):
    try:
        selected_index = inbox_list.curselection()[0]
        email_id = email_ids[selected_index]
        mail = connect_to_email()
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        from_ = msg.get("From")
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        
        details_window = Toplevel(root)
        details_window.title("Email Details")
        details_window.geometry("600x400")
        
        details_text = Text(details_window, wrap=WORD, font=("Arial", 12))
        details_text.insert(END, f"From: {from_}\nSubject: {subject}\n\n{body}")
        details_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display email details: {str(e)}")

# Set up the GUI
root = Tk()
root.title("Professional Email Reader")
root.geometry("800x600")

# Create a frame for the inbox list
inbox_frame = Frame(root)
inbox_frame.pack(fill=BOTH, expand=True)

# Create a scrollable listbox for the inbox
inbox_list = Listbox(inbox_frame, width=100, height=20, font=("Arial", 12))
inbox_scrollbar = Scrollbar(inbox_frame, orient=VERTICAL, command=inbox_list.yview)
inbox_list.config(yscrollcommand=inbox_scrollbar.set)

inbox_list.pack(side=LEFT, fill=BOTH, expand=True)
inbox_scrollbar.pack(side=RIGHT, fill=Y)

# Create a frame for the buttons
button_frame = Frame(root)
button_frame.pack(pady=10)

fetch_button = Button(button_frame, text="Fetch Emails", command=lambda: fetch_emails("ALL"), font=("Arial", 12))
fetch_button.pack(side=LEFT, padx=5)

search_button = Button(button_frame, text="Search Emails", command=search_emails, font=("Arial", 12))
search_button.pack(side=LEFT, padx=5)

inbox_list.bind("<Double-1>", show_email_details)  # Bind double-click event to show email details

root.mainloop()

