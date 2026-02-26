from pywinauto.application import Application
import config
import time
import os

def login_his(username, password):
    """
    Logs into the HIS desktop application.
    """
    print(f"Attempting to launch HIS System at {config.HIS_APP_PATH}...")
    
    if not os.path.exists(config.HIS_APP_PATH):
        print(f"Error: HIS executable not found at {config.HIS_APP_PATH}")
        return False

    try:
        app = Application(backend="uia").start(config.HIS_APP_PATH)
        
        # Wait for the login window
        # We use a timeout loop to find the window
        print("Waiting for login window...")
        # Note: You might need to adjust the window title regex or exact name
        # app.windows() can help list available windows if this fails
        
        # Attempt to connect to the app if start() didn't return the connected app instance properly
        # or if it takes time to appear.
        time.sleep(5) 
        
        # This is a heuristic. We try to find the window.
        # If the user provided a specific title, use it.
        dlg = app.window(title_re=".*Login.*") 
        if not dlg.exists():
             dlg = app.window(title_re=".*HIS.*")
        
        if dlg.exists():
            print("Login window found.")
            dlg.set_focus()
            
            # Standard interaction: Type username, Tab, Password, Enter
            # This is the most common pattern for desktop login forms.
            # If the fields are named, we could use dlg.child_window(auto_id="User").type_keys(...)
            
            print("Sending keystrokes...")
            dlg.type_keys(username)
            dlg.type_keys("{TAB}")
            dlg.type_keys(password)
            dlg.type_keys("{ENTER}")
            
            print("Credentials entered.")
            return True
        else:
            print("Could not find login window. Please check the window title in his_login.py")
            return False

    except Exception as e:
        print(f"HIS Login Error: {e}")
        return False

if __name__ == "__main__":
    # Test stub
    login_his("testuser", "testpass")
