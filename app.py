import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# Set page configuration
st.set_page_config(page_title="Foodiza - Tiffin Service", layout="wide")
st.title("🍱 Welcome to Foodiza!")
st.markdown("""
<style>
    .big-title {
        font-size: 40px;
        font-weight: bold;
        color: #ff6347;
        text-align: center;
    }
</style>
<div class="big-title">Delicious Homemade Tiffin Service</div>
""", unsafe_allow_html=True)

# Data for the menu with pricing
menu_data = {
    "Lunch Box": {"items": ["Paneer Butter Masala", "Dal Tadka", "4 Chapatis", "Sabzi", "Dal", "Rice"], "price": 2200},
    "Mini Lunch Box": {"items": ["Chapati", "Sabzi", "Dal", "Chawal"], "price": 1500},
    "Gym Lunch Box": {"items": ["Eggs", "Chicken", "Sprouts", "Fruits", "Paneer"], "price": 1000},
    "Special Meal Box": {"items": ["Shahi Paneer", "Mushroom", "Shahi Dal Tadka", "Egg Curry"], "price": 3500}
}

# Initialize SQLite database
conn = sqlite3.connect('foodiza_orders.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    contact TEXT,
    selected_box TEXT,
    description TEXT,
    total_amount REAL
)
""")
conn.commit()

# Email notification function
def send_email(name, address, contact, selected_box, description, total_amount):
    sender_email = "foodiza.0@gmail.com"  # Replace with your email
    sender_password = "emig ielk ygzy lugo"  # Replace with your app password
    recipient_email = "foodiza.0@gmail.com"  # Replace with the recipient email

    subject = "New Order from Foodiza"
    body = f"""
    New Order Details:
    Name: {name}
    Address: {address}
    Contact: {contact}
    Tiffin Box: {selected_box}
    Description: {description}
    Total Amount: ₹{total_amount}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# WhatsApp notification function
def send_whatsapp(contact, message):
    account_sid = 'ACaf6d6b2708a1529c3ac5521af2d4b0cc'  # Replace with your Twilio SID
    auth_token = 'cc1737de19a4087e7da6428645bface7'  # Replace with your Twilio Auth Token
    twilio_phone_number = 'whatsapp:+14155238886'  # Twilio's WhatsApp Sandbox Number (or your own WhatsApp number)

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=f'whatsapp:+918602432586'  # WhatsApp number of the customer
        )
        print("WhatsApp message sent successfully!")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

# Home Section
st.header("🏠 Home")
st.write("Welcome to Foodiza! We deliver fresh, homemade tiffins to your doorstep.")
st.markdown("Best meal box at your doorstep! Offering the best tiffin box services in Bhopal, just like ghar ka khana!")
st.write("Explore our menu and order your favorite meals today!")

# Menu Section
st.header("📜 Menu")
st.write("Explore our range of customizable tiffin boxes:")
for box_name, details in menu_data.items():
    st.subheader(f"{box_name} - ₹{details['price']}")
    for item in details["items"]:
        st.write(f"- {item}")

# Place Order Section
st.header("🛒 Place Your Order")
st.write("Select your preferred tiffin box and add any special details for your order:")

with st.form(key="order_form"):
    selected_box = st.selectbox("Choose a Tiffin Box", list(menu_data.keys()))
    if selected_box and selected_box != "Lunch Box":  # Exclude Lunch Box menu details
        st.write(f"**Menu for {selected_box}:**")
        for item in menu_data[selected_box]["items"]:
            st.write(f"- {item}")

    description = st.text_area("Any additional details about your order (e.g., customizations, allergies, etc.)")
    st.write("**Customer Details:**")
    name = st.text_input("Name")
    address = st.text_area("Delivery Address")
    contact = st.text_input("Contact Number")
    submit_button = st.form_submit_button("📦 Place Order")

    if submit_button:
        # Get the price for the selected box
        total_amount = menu_data[selected_box]["price"]
        
        if name and address and contact:
            cursor.execute("""
            INSERT INTO orders (name, address, contact, selected_box, description, total_amount)
            VALUES (?, ?, ?, ?, ?, ?)""", (name, address, contact, selected_box, description, total_amount))
            conn.commit()

            # Send email and WhatsApp notifications
            send_email(name, address, contact, selected_box, description, total_amount)
            send_whatsapp(contact, f"Hello {name}, your order from Foodiza has been received. We'll deliver it to {address}. Total: ₹{total_amount}.")
            
            st.success(f"Thank you, {name}! Your order has been placed.")
            st.write(f"Your order will be delivered to: **{address}**")
            st.write(f"**Contact Number:** {contact}")
        else:
            st.error("Please fill in all the details to place your order.")

# Footer Section
st.markdown("---")
st.write("Why Choose Us?") 
st.write("Home Made: We cook every meal with love, just like ghar ka khana.")
st.write("Healthy & Maida-Free: Our meals are free of Maida and focus on health.")
st.write("Demo Lunch Box: Want to try before you decide? We offer demo lunch boxes so you can taste the goodness before committing.")
st.markdown("---")
st.markdown("Thank you for choosing Foodiza! Your satisfaction is our priority.")
