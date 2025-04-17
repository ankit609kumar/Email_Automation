import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os
import time
import io

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Email Sender",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        background-color: black;
    }
    .stTextArea>div>div>textarea {
        background-color: black;
    }
    .css-1d391kg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: black;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .file-uploader {
        border: 2px dashed #ccc;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def send_email(sender_email, receiver_email, subject, body, password, attachments=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Add attachments if any
        if attachments:
            for attachment in attachments:
                # Create a MIME attachment
                part = MIMEBase('application', 'octet-stream')
                # Read the file data directly from the uploaded file
                part.set_payload(attachment.getvalue())
                encoders.encode_base64(part)
                # Add header
                part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

# Email templates
email_templates = {
    "Default": {
        "subject": "",
        "body": ""
    },
    "Meeting Invitation": {
        "subject": "Meeting Invitation: [Topic]",
        "body": """Dear [Name],

I hope this email finds you well. I would like to invite you to a meeting regarding [Topic].

Date: [Date]
Time: [Time]
Location: [Location/Platform]

Please let me know if this time works for you.

Best regards,
[Your Name]"""
    },
    "Follow-up": {
        "subject": "Follow-up: [Previous Topic]",
        "body": """Hi [Name],

I hope you're doing well. I'm following up on our previous conversation about [Topic].

[Your message]

Looking forward to your response.

Best regards,
[Your Name]"""
    },
    "Thank You": {
        "subject": "Thank You for [Reason]",
        "body": """Dear [Name],

I wanted to take a moment to thank you for [Reason].

[Your message]

Best regards,
[Your Name]"""
    }
}

def main():
    # Sidebar
    with st.sidebar:
        st.title("Settings")
        theme = st.selectbox("Select Theme", ["Light", "Dark"])
        st.markdown("---")
        st.info("💡 Quick Tips")
        st.markdown("""
        - Use Gmail App Password
        - Enable 2-Step Verification
        - Check spam folder
        - Max attachment size: 25MB
        """)

    # Main content
    st.title("📧 Email Sender")
    st.markdown("---")

    # Get default values from .env
    default_sender = os.getenv('SENDER_EMAIL')
    default_receiver = os.getenv('RECEIVER_EMAIL')
    default_password = os.getenv('EMAIL_PASSWORD')

    # Create two columns for the form
    col1, col2 = st.columns([2, 1])

    with col1:
        # Create form
        with st.form("email_form"):
            # Template selection
            template = st.selectbox("Select Email Template", list(email_templates.keys()))
            
            # Email fields
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                sender_email = st.text_input("Sender Email", value=default_sender)
            with col1_2:
                receiver_email = st.text_input("Receiver Email", value=default_receiver)
            
            # Subject and body with template
            subject = st.text_input("Subject", value=email_templates[template]["subject"])
            body = st.text_area("Message", value=email_templates[template]["body"], height=300)
            
            # File uploader
            st.markdown("### Attachments")
            attachments = st.file_uploader("Add files", accept_multiple_files=True, 
                                         help="You can upload multiple files")
            
            # Password field
            password = st.text_input("App Password", type="password", value=default_password)
            
            # Submit button
            submit_button = st.form_submit_button("Send Email")

    with col2:
        st.subheader("Preview")
        st.markdown("---")
        if subject or body:
            st.markdown("**Subject:**")
            st.info(subject)
            st.markdown("**Message:**")
            st.info(body)
            if attachments:
                st.markdown("**Attachments:**")
                for attachment in attachments:
                    st.info(f"📎 {attachment.name} ({attachment.size / 1024:.1f} KB)")
        else:
            st.info("Fill in the form to see preview")

    # Handle form submission
    if submit_button:
        if not all([sender_email, receiver_email, subject, body, password]):
            st.warning("Please fill in all required fields!")
        else:
            with st.spinner("Sending email..."):
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete + 1)
                
                if send_email(sender_email, receiver_email, subject, body, password, attachments):
                    st.success("Email sent successfully! 🎉")
                    st.balloons()
                else:
                    st.error("Failed to send email. Please check your credentials.")

    # Add some helpful information at the bottom
    st.markdown("---")
    with st.expander("Need Help?"):
        st.markdown("""
        ### How to Get Gmail App Password
        1. Go to your Google Account settings
        2. Enable 2-Step Verification
        3. Go to Security > App Passwords
        4. Generate a new app password
        5. Use this password in the form above

        ### About Attachments
        - You can attach multiple files
        - Maximum file size: 25MB
        - Supported file types: All
        - Files are sent as-is, no compression
        """)

if __name__ == "__main__":
    main() 