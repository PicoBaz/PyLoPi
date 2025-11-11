import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailNotifier:
    def __init__(self, config):
        self.config = config
        self.enabled = config.get('email_notifications', False)
        self.email_address = config.get('email_address', '')
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username', '')
        self.smtp_password = config.get('smtp_password', '')

    def send_notification(self, log_id, log_data):
        if not self.enabled or not self.email_address:
            return

        try:
            subject = f"PyLoPi Alert: {log_data['error_type']} detected"

            html_body = self.create_html_email(log_id, log_data)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = self.email_address

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"Email notification sent for log ID: {log_id}")
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def create_html_email(self, log_id, log_data):
        severity_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }

        severity_color = severity_colors.get(log_data['severity'], '#6c757d')

        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .severity-badge {{
                    display: inline-block;
                    padding: 5px 15px;
                    background: {severity_color};
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .info-row {{
                    margin: 10px 0;
                    padding: 10px;
                    background: white;
                    border-left: 3px solid #667eea;
                }}
                .label {{
                    font-weight: bold;
                    color: #667eea;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 PyLoPi Error Alert</h1>
                <p>A new error has been detected and analyzed</p>
            </div>

            <div class="content">
                <div class="severity-badge">{log_data['severity'].upper()}</div>

                <div class="info-row">
                    <span class="label">Error Type:</span> {log_data['error_type']}
                </div>

                <div class="info-row">
                    <span class="label">Error Message:</span><br>
                    {log_data['error_message']}
                </div>

                <div class="info-row">
                    <span class="label">Log File:</span> {log_data['log_file']}
                </div>

                <div class="info-row">
                    <span class="label">Timestamp:</span> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>

                <div class="info-row">
                    <span class="label">Quick Analysis:</span><br>
                    {log_data['analysis'][:200]}...
                </div>

                <center>
                    <a href="http://localhost:5000/#/log/{log_id}" class="button">
                        View Full Analysis & Solution
                    </a>
                </center>
            </div>

            <div class="footer">
                <p>This is an automated message from PyLoPi</p>
                <p>You can configure notification settings in the PyLoPi dashboard</p>
            </div>
        </body>
        </html>
        '''

        return html