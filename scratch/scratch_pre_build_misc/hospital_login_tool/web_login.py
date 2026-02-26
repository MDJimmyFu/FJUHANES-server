from playwright.sync_api import sync_playwright
import config
import time

def login_web(username, password):
    """
    Logs into the hospital web system using Playwright.
    """
    print(f"Attempting to log in to Web System at {config.WEB_LOGIN_URL}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) # Headless=False to see the browser
            page = browser.new_page()
            page.goto(config.WEB_LOGIN_URL)
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")

            # TODO: These selectors are generic. 
            # You will likely need to inspect the page and update 'name="username"' etc.
            # Common selectors: 'input[name="username"]', '#username', 'input[type="text"]'
            
            print("Filling credentials...")
            # Attempting to find common username fields
            if page.is_visible('input[name="username"]'):
                page.fill('input[name="username"]', username)
            elif page.is_visible('input[id="username"]'):
                page.fill('input[id="username"]', username)
            elif page.is_visible('input[type="text"]'):
                 # Risky if multiple text inputs, but a fallback
                page.fill('input[type="text"]', username)
            else:
                print("Could not find username field. Please update selectors in web_login.py")
                return False

            # Attempting to find common password fields
            if page.is_visible('input[name="password"]'):
                page.fill('input[name="password"]', password)
            elif page.is_visible('input[type="password"]'):
                page.fill('input[type="password"]', password)
            else:
                print("Could not find password field. Please update selectors in web_login.py")
                return False

            # Submit
            # Look for a button with type submit or text "Login"
            if page.is_visible('button[type="submit"]'):
                page.click('button[type="submit"]')
            elif page.is_visible('input[type="submit"]'):
                page.click('input[type="submit"]')
            else:
                # Try pressing Enter
                page.keyboard.press('Enter')
            
            print("Login submitted. Keeping browser open...")
            
            # Keep browser open for the user to use
            # In a real script, we might detach or just wait. 
            # For this tool, we probably want to keep it open.
            # However, sync_playwright closes when the script ends. 
            # To keep it open, we might need a loop or just wait for a long time/manual close.
            
            # A simple way to keep it open for this session:
            try:
                page.wait_for_timeout(3600000) # Wait for 1 hour or until closed
            except:
                pass
                
            browser.close()
            return True

    except Exception as e:
        print(f"Web Login Error: {e}")
        return False

if __name__ == "__main__":
    # Test stub
    login_web("testuser", "testpass")
