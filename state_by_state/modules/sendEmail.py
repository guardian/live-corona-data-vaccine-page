import smtplib
from email.mime.text import MIMEText
import os

def sendEmail(text, subject, to):
	
	EMAIL_ALERT_PASSWORD = os.environ['EMAIL_ALERT_PASSWORD']
	
	fromaddr = "alerts@nickevershed.com"
	recipients = ["nick.evershed@theguardian.com"]
	
	msg = MIMEText(text, 'html')
	msg['Subject'] = subject
	msg['From'] = fromaddr
	msg['To'] = ", ".join(to)	
	server = smtplib.SMTP_SSL('mail.nickevershed.com', 465)
	server.login(fromaddr, EMAIL_ALERT_PASSWORD)
	text = msg.as_string()
	print("Sending email")
	server.sendmail(fromaddr, to, text)
	server.quit()
	print("Email sent")