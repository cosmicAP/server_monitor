#!/usr/bin/env python3

import smtplib
import psutil
import time
import logging
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        return json.load(f)


def send_email(subject, body, email_config):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config['email_from']
        msg['To'] = email_config['email_to']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['email_from'], email_config['email_password'])
        server.send_message(msg)
        server.quit()

        logging.info("Email alert sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def check_system_resources(config):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    logging.info(f"CPU: {cpu}%, Memory: {memory}%")

    if cpu > config['cpu_threshold'] or memory > config['memory_threshold']:
        subject = "Server Alert: High Resource Usage"
        body = (
            f"CPU usage: {cpu}% (limit: {config['cpu_threshold']}%)\n"
            f"Memory usage: {memory}% (limit: {config['memory_threshold']}%)"
        )
        send_email(subject, body, config)


def main():
    config = load_config()

    logging.basicConfig(
        filename="server_monitor.log",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Monitoring started...")

    try:
        while True:
            check_system_resources(config)
            time.sleep(config['check_interval'])
    except KeyboardInterrupt:
        logging.info("Monitoring stopped.")


if __name__ == "__main__":
    main()
