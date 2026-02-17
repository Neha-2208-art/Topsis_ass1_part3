import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# ==========================
# YOUR DETAILS
# ==========================
SENDER_EMAIL = "nneha_be23@thapar.edu"
SENDER_PASSWORD = "emoinislymzhgqin"

# ==========================
# EMAIL FUNCTION
# ==========================
def send_email(receiver_email, result_file):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "TOPSIS Result File - Neha"

        body = f"""Hello,

Please find the attached result file for your TOPSIS analysis.

Best regards,
Neha (102317062)
"""
        msg.attach(MIMEText(body, 'plain'))

        with open(result_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition",
                        f"attachment; filename= {result_file}")
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        st.error(f"Email Error: {e}")
        return False


# ==========================
# TOPSIS FUNCTION
# ==========================
def calculate_topsis(df, weights, impacts):

    data = df.iloc[:, 1:].values.astype(float)

    w = [float(i) for i in weights.split(',')]
    imp = impacts.split(',')

    if len(w) != data.shape[1] or len(imp) != data.shape[1]:
        return None, "Weights/Impacts count mismatch."

    rss = np.sqrt(np.sum(data**2, axis=0))
    norm_data = data / rss
    weighted_data = norm_data * w

    ideal_best = []
    ideal_worst = []

    for i in range(len(imp)):
        if imp[i] == '+':
            ideal_best.append(np.max(weighted_data[:, i]))
            ideal_worst.append(np.min(weighted_data[:, i]))
        elif imp[i] == '-':
            ideal_best.append(np.min(weighted_data[:, i]))
            ideal_worst.append(np.max(weighted_data[:, i]))
        else:
            return None, "Impacts must be '+' or '-'."

    dist_best = np.sqrt(np.sum((weighted_data - ideal_best)**2, axis=1))
    dist_worst = np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1))

    score = dist_worst / (dist_best + dist_worst)

    df['Topsis Score'] = score
    df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)

    return df, None


# ==========================
# STREAMLIT UI
# ==========================
st.title("TOPSIS Web Service")
st.markdown("Developed by **Neha** (Roll: 102317062)")
st.write("Upload CSV, enter weights & impacts, receive result via Email.")

uploaded_file = st.file_uploader("Upload CSV File", type="csv")
weights = st.text_input("Enter Weights (comma-separated)", "1,1,1,1,1")
impacts = st.text_input("Enter Impacts (comma-separated)", "+,+,+,+,+")
email_id = st.text_input("Enter Email ID")

if st.button("Submit"):

    if uploaded_file and weights and impacts and email_id:

        df = pd.read_csv(uploaded_file)

        result_df, error = calculate_topsis(df.copy(), weights, impacts)

        if error:
            st.error(error)
        else:
            st.success("Calculation Successful!")
            st.dataframe(result_df)

            output_filename = f"result-{email_id.split('@')[0]}.csv"
            result_df.to_csv(output_filename, index=False)

            if send_email(email_id, output_filename):
                st.success(f"Email sent to {email_id}")

            if os.path.exists(output_filename):
                os.remove(output_filename)

    else:
        st.warning("Please fill all fields.")
