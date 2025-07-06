#!/usr/bin/env python3
"""
Internship Watcher for GitHub Actions - Runs once and exits
Modified version of internship_watcher.py for GitHub Actions scheduling
"""

import os
import re
import json
import smtplib
import logging
from datetime import datetime
from typing import List, Dict, Set
import requests

# Email imports with fallback for different Python versions
try:
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
except ImportError:
    from email.MIMEText import MIMEText as MimeText
    from email.MIMEMultipart import MIMEMultipart as MimeMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InternshipWatcher:
    def __init__(self):
        self.github_url = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"
        self.data_file = "previous_internships.json"
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        
        # Validate email configuration
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.email_from, self.email_to]):
            raise ValueError("Missing email configuration in environment variables")
    
    def fetch_repository_data(self) -> str:
        """Fetch the README content from the GitHub repository."""
        try:
            response = requests.get(self.github_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Failed to fetch repository data: {e}")
            return ""
    
    def parse_internships(self, content: str) -> List[Dict[str, str]]:
        """Parse internship listings from the README markdown content."""
        internships = []
        
        # Find the software engineering section table
        se_pattern = r'## 💻 Software Engineering Internship Roles.*?(?=##|\Z)'
        se_match = re.search(se_pattern, content, re.DOTALL)
        
        if se_match:
            se_section = se_match.group()
            internships.extend(self._parse_table_section(se_section, "Software Engineering"))
        
        # Find the quantitative finance section table
        quant_pattern = r'## 📈 Quantitative Finance Internship Roles.*?(?=##|\Z)'
        quant_match = re.search(quant_pattern, content, re.DOTALL)
        
        if quant_match:
            quant_section = quant_match.group()
            internships.extend(self._parse_table_section(quant_section, "Quantitative Finance"))
        
        # Find the hardware engineering section table
        hw_pattern = r'## 🔧 Hardware Engineering Internship Roles.*?(?=##|\Z)'
        hw_match = re.search(hw_pattern, content, re.DOTALL)
        
        if hw_match:
            hw_section = hw_match.group()
            internships.extend(self._parse_table_section(hw_section, "Hardware Engineering"))
        
        # Find the data science section table
        ds_pattern = r'## 🤖 Data Science, AI & Machine Learning.*?(?=##|\Z)'
        ds_match = re.search(ds_pattern, content, re.DOTALL)
        
        if ds_match:
            ds_section = ds_match.group()
            internships.extend(self._parse_table_section(ds_section, "Data Science, AI & ML"))
        
        return internships
    
    def _parse_table_section(self, section: str, category: str) -> List[Dict[str, str]]:
        """Parse a specific table section and extract internship data."""
        internships = []
        
        # Find table rows (lines starting with |)
        lines = section.split('\n')
        in_table = False
        current_company = ""  # Track the current company for arrow entries
        
        for line in lines:
            line = line.strip()
            if line.startswith('|') and '---' not in line:
                if 'Company' in line and 'Role' in line:  # Header row
                    in_table = True
                    continue
                elif in_table and line.count('|') >= 4:  # Data row
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 5:
                        company = self._clean_text(parts[1])
                        role = self._clean_text(parts[2])
                        location = self._clean_text(parts[3])
                        
                        # Handle arrow entries (additional positions for the same company)
                        if company.startswith('↳'):
                            # Use the previously seen company name
                            company = current_company
                        elif company and role:
                            # Update the current company for future arrow entries
                            current_company = company
                        
                        # Include if we have valid company and role
                        if company and role and company.strip():
                            # Create a unique identifier for this internship
                            internship_id = f"{company}_{role}_{location}_{category}".replace(" ", "_").replace("/", "_").replace(",", "_")
                            internships.append({
                                'id': internship_id,
                                'company': company,
                                'role': role,
                                'location': location,
                                'category': category,
                                'timestamp': datetime.now().isoformat()
                            })
        
        return internships
    
    def _clean_text(self, text: str) -> str:
        """Clean markdown formatting and HTML from text."""
        # Remove markdown links
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
        # Remove markdown bold
        text = re.sub(r'\*\*([^\*]*)\*\*', r'\1', text)
        # Remove HTML tags like <br>, </br>, <div>, etc.
        text = re.sub(r'<[^>]+>', '', text)
        # Replace </br> with comma separator for locations
        text = re.sub(r'</br>', ', ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def load_previous_internships(self) -> Set[str]:
        """Load previously seen internship IDs from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('internship_ids', []))
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Failed to load previous internships: {e}")
        return set()
    
    def save_internships(self, internships: List[Dict[str, str]]):
        """Save current internship data to file."""
        data = {
            'last_updated': datetime.now().isoformat(),
            'internship_ids': [internship['id'] for internship in internships],
            'internships': internships
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logging.error(f"Failed to save internships: {e}")
    
    def send_email(self, new_internships: List[Dict[str, str]]):
        """Send email notification about new internships."""
        if not new_internships:
            return
        
        subject = f"🚨 {len(new_internships)} New Summer 2026 Internship(s) Found!"
        
        # Create HTML email body
        html_body = self._create_email_html(new_internships)
        
        # Create text version
        text_body = self._create_email_text(new_internships)
        
        msg = MimeMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        
        msg.attach(MimeText(text_body, 'plain'))
        msg.attach(MimeText(html_body, 'html'))
        
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logging.info(f"Email sent successfully for {len(new_internships)} new internship(s)")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    
    def _create_email_html(self, internships: List[Dict[str, str]]) -> str:
        """Create HTML email body."""
        html = f"""
        <html>
        <head></head>
        <body>
            <h2>🚨 New Summer 2026 Internships Found!</h2>
            <p>Found {len(internships)} new internship listing(s):</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px;">Company</th>
                    <th style="padding: 8px;">Role</th>
                    <th style="padding: 8px;">Location</th>
                    <th style="padding: 8px;">Category</th>
                </tr>
        """
        
        for internship in internships:
            html += f"""
                <tr>
                    <td style="padding: 8px;">{internship['company']}</td>
                    <td style="padding: 8px;">{internship['role']}</td>
                    <td style="padding: 8px;">{internship['location']}</td>
                    <td style="padding: 8px;">{internship['category']}</td>
                </tr>
            """
        
        html += """
            </table>
            <br>
            <p>Check the full repository for application links: 
            <a href="https://github.com/SimplifyJobs/Summer2026-Internships">
            Summer 2026 Internships Repository</a></p>
            <p><em>This email was sent by your automated GitHub Actions Internship Watcher.</em></p>
        </body>
        </html>
        """
        
        return html
    
    def _create_email_text(self, internships: List[Dict[str, str]]) -> str:
        """Create plain text email body."""
        text = f"🚨 New Summer 2026 Internships Found!\n\n"
        text += f"Found {len(internships)} new internship listing(s):\n\n"
        
        for i, internship in enumerate(internships, 1):
            text += f"{i}. {internship['company']} - {internship['role']}\n"
            text += f"   Location: {internship['location']}\n"
            text += f"   Category: {internship['category']}\n\n"
        
        text += "Check the full repository for application links:\n"
        text += "https://github.com/SimplifyJobs/Summer2026-Internships\n\n"
        text += "This email was sent by your automated GitHub Actions Internship Watcher."
        
        return text
    
    def check_for_new_internships(self):
        """Main function to check for new internships and send notifications."""
        logging.info("🔍 Checking for new internships...")
        
        # Fetch current data
        content = self.fetch_repository_data()
        if not content:
            logging.error("Failed to fetch repository data")
            return
        
        # Parse internships
        current_internships = self.parse_internships(content)
        current_ids = {internship['id'] for internship in current_internships}
        
        # Load previous internships
        previous_ids = self.load_previous_internships()
        
        # Find new internships
        new_ids = current_ids - previous_ids
        new_internships = [internship for internship in current_internships 
                          if internship['id'] in new_ids]
        
        if new_internships:
            logging.info(f"🎉 Found {len(new_internships)} new internship(s)!")
            for internship in new_internships:
                logging.info(f"  📝 New: {internship['company']} - {internship['role']} ({internship['location']})")
            self.send_email(new_internships)
        else:
            logging.info("✅ No new internships found")
        
        # Save current state
        self.save_internships(current_internships)
        
        logging.info(f"📊 Total internships tracked: {len(current_internships)}")

def main():
    """Main function for GitHub Actions execution."""
    try:
        logging.info("🚀 Starting GitHub Actions Internship Watcher...")
        watcher = InternshipWatcher()
        watcher.check_for_new_internships()
        logging.info("✅ Internship check completed successfully!")
        
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        raise  # Re-raise to fail the GitHub Action

if __name__ == "__main__":
    main() 