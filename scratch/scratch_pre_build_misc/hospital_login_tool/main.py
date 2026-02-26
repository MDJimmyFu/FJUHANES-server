import tkinter as tk
from tkinter import messagebox
import threading
import web_login
import his_login

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Auto-Login Tool")
        self.root.geometry("300x250")

        # Username Label and Entry
        self.lbl_user = tk.Label(root, text="Username / ID:")
        self.lbl_user.pack(pady=5)
        self.ent_user = tk.Entry(root)
        self.ent_user.pack(pady=5)

        # Password Label and Entry
        self.lbl_pass = tk.Label(root, text="Password:")
        self.lbl_pass.pack(pady=5)
        self.ent_pass = tk.Entry(root, show="*")
        self.ent_pass.pack(pady=5)

        # Login Button
        self.btn_login = tk.Button(root, text="Login to All Systems", command=self.start_login_thread)
        self.btn_login.pack(pady=20)

        # Status Label
        self.lbl_status = tk.Label(root, text="Ready", fg="gray")
        self.lbl_status.pack(side=tk.BOTTOM, pady=5)

    def start_login_thread(self):
        username = self.ent_user.get()
        password = self.ent_pass.get()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        self.btn_login.config(state=tk.DISABLED)
        self.lbl_status.config(text="Logging in...", fg="blue")

        # Run login in a separate thread to keep GUI responsive
        t = threading.Thread(target=self.perform_login, args=(username, password))
        t.start()

    def perform_login(self, username, password):
        # 1. Web Login
        self.update_status("Logging into Web System...")
        web_success = web_login.login_web(username, password)
        
        # 2. HIS Login
        self.update_status("Logging into HIS System...")
        his_success = his_login.login_his(username, password)

        # Result
        if web_success and his_success:
            self.update_status("Login Sequence Completed.", "green")
            messagebox.showinfo("Success", "Login sequence finished for both systems.")
        elif web_success or his_success:
            self.update_status("Partial Success.", "orange")
            messagebox.showwarning("Partial Success", "One system logged in, check console for errors.")
        else:
            self.update_status("Login Failed.", "red")
            messagebox.showerror("Error", "Failed to log in to systems.")

        self.root.after(0, lambda: self.btn_login.config(state=tk.NORMAL))

    def update_status(self, text, color="blue"):
        self.root.after(0, lambda: self.lbl_status.config(text=text, fg=color))

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
