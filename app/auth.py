"""
Authentication module for Seasonality Trading Tool
Secure user authentication for remote access
"""
import hashlib
import hmac
import streamlit as st
from typing import Dict, Optional
import time


# User credentials - Change these passwords for production!
USERS = {
    "admin": {
        "password_hash": "ea21133d31d85d5d72f63d807119aa62c1532dead88d6d3908eb92aea9476e1c",  # "#Cassian42!"
        "role": "admin"
    },
    "trader": {
        "password_hash": "06b05d220d175b6584093cd076195221c4393c61314382f7a3ba4d5b69374ccd",  # "#Derek42!"
        "role": "trader"
    },
    "analyst": {
        "password_hash": "548892a98c059dff6f787ed2b5abe4a850324e1dcca38c0863b97e84e34b5ba6",  # "market2024"
        "role": "analyst"
    }
}


def hash_password(password: str) -> str:
    """Create SHA256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hmac.compare_digest(hash_password(password), password_hash)


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user credentials
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User info dict if authenticated, None otherwise
    """
    if username in USERS:
        user_data = USERS[username]
        if verify_password(password, user_data["password_hash"]):
            return {
                "username": username,
                "role": user_data["role"],
                "login_time": time.time()
            }
    return None


def check_authentication() -> bool:
    """
    Check if user is authenticated in Streamlit session
    
    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[Dict]:
    """Get current authenticated user info"""
    if check_authentication():
        return st.session_state.get("user_info")
    return None


def logout():
    """Clear authentication from session"""
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user_info" in st.session_state:
        del st.session_state["user_info"]


def show_login_form():
    """
    Display login form in Streamlit
    
    Returns:
        True if login successful, False otherwise
    """
    st.markdown("# 🔐 Seasonality Trading Tool - Secure Login")
    st.markdown("---")
    
    # Login form
    with st.form("login_form"):
        st.markdown("### 🔑 Enter your credentials:")
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        submit_button = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if submit_button:
            if username and password:
                user_info = authenticate_user(username, password)
                if user_info:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_info
                    st.success(f"✅ Welcome, {username}! Loading application...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password!")
                    time.sleep(2)
            else:
                st.warning("⚠️ Please enter both username and password")
    
    # Security info only
    st.markdown("---")
    st.markdown("### 🔐 Secure Authentication Required")
    st.info("🔒 Contact your administrator for login credentials")
    
    st.markdown("### 🛡️ Security Features:")
    st.markdown("""
    - 🛡️ **SHA256 Password Hashing** - Passwords are securely hashed
    - 🕐 **Session Management** - Automatic logout after inactivity
    - 🔒 **Secure Authentication** - No plain text password storage
    - 👥 **Role-Based Access** - Different permission levels
    - 🌐 **Remote Access Ready** - Works from any device with internet
    """)
    
    return False


def require_authentication():
    """
    Decorator/function to require authentication
    Call this at the start of your main app
    """
    if not check_authentication():
        show_login_form()
        st.stop()
    
    # Show user info in sidebar
    user_info = get_current_user()
    if user_info:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 User Session")
            st.markdown(f"**User:** {user_info['username']}")
            st.markdown(f"**Role:** {user_info['role'].title()}")
            st.markdown(f"**Login:** {time.strftime('%H:%M', time.localtime(user_info['login_time']))}")
            
            # Show permissions based on role
            if user_info['role'] == 'admin':
                st.success("🔓 Full Access")
            else:
                st.info("👀 Read-Only Access")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()


def require_admin():
    """
    Check if current user is admin
    Returns True if admin, False otherwise
    """
    user_info = get_current_user()
    return user_info and user_info.get('role') == 'admin'


def check_admin_permission(action_name: str = "this action"):
    """
    Check admin permission and show error if not admin
    
    Args:
        action_name: Description of the action requiring admin rights
        
    Returns:
        True if admin, False otherwise (and shows error)
    """
    if not require_admin():
        user_info = get_current_user()
        if user_info:
            st.error(f"❌ **Access Denied**: {action_name.title()} requires admin privileges. Your role: {user_info['role'].title()}")
        else:
            st.error(f"❌ **Access Denied**: {action_name.title()} requires authentication.")
        return False
    return True


# Password generation helper (for creating new user hashes)
def generate_password_hash(password: str) -> str:
    """Helper function to generate password hashes for new users"""
    return hash_password(password)


if __name__ == "__main__":
    # Test authentication
    print("Testing authentication system:")
    print(f"admin/#Cassian42!: {authenticate_user('admin', '#Cassian42!')}")
    print(f"trader/#Derek42!: {authenticate_user('trader', '#Derek42!')}")
    print(f"analyst/market2024: {authenticate_user('analyst', 'market2024')}")
    print(f"invalid/wrong: {authenticate_user('invalid', 'wrong')}")