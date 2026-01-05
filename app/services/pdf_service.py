import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from app.core.config import settings
from app.models.operations import Transfer
from app.models.asset import Asset

class PDFService:
    @staticmethod
    def generate_transfer_pdf(transfer: Transfer, asset: Asset, initiator_name: str, 
                              from_name: str, to_name: str, from_loc: str, to_loc: str) -> str:
        
        filename = f"transfer_{transfer.transfer_id}.pdf"
        output_dir = os.path.join(settings.UPLOAD_DIR, "transfers")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Define sky blue color
        sky_blue = colors.Color(0.53, 0.81, 0.92)  # Light sky blue
        darker_blue = colors.Color(0.25, 0.41, 0.88)  # Royal blue for headers
        
        # Simple border
        c.setStrokeColor(darker_blue)
        c.setLineWidth(2)
        c.rect(1.5*cm, 1.5*cm, width-3*cm, height-3*cm)
        
        # Header Section with Logo
        logo_path = "planlogo.png" 
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 2.5*cm, height-4*cm, width=3.5*cm, preserveAspectRatio=True, mask='auto')
        
        # Title
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(darker_blue)
        c.drawCentredString(width/2, height-3*cm, "GOOD ISSUE NOTE")
        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height-3.6*cm, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Start content
        y = height - 5.5 * cm
        left_margin = 2.5 * cm
        content_width = width - 5 * cm
        
        # Helper function for section headers
        def draw_section(title_text, y_pos):
            c.setFillColor(sky_blue)
            c.rect(left_margin, y_pos - 0.7*cm, content_width, 0.7*cm, fill=1, stroke=0)
            c.setFillColor(darker_blue)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin + 0.3*cm, y_pos - 0.45*cm, title_text)
            c.setFillColor(colors.black)
            return y_pos - 1.2*cm
        
        # ASSET INFORMATION Section
        y = draw_section("ASSET INFORMATION", y)
        c.setFont("Helvetica", 11)
        line_height = 0.6 * cm
        
        c.drawString(left_margin + 0.3*cm, y, f"Asset ID: {asset.scom_asset_id}")
        y -= line_height
        
        desc_text = f"{asset.asset_name} ({asset.brand} {asset.model})"
        c.drawString(left_margin + 0.3*cm, y, f"Description: {desc_text}")
        y -= line_height
        
        c.drawString(left_margin + 0.3*cm, y, f"Tag Number: {asset.physical_asset_tag_number or 'N/A'}")
        y -= line_height
        
        c.drawString(left_margin + 0.3*cm, y, f"Status: {asset.asset_status}")
        y -= line_height * 1.5
        
        # TRANSFER DETAILS Section
        y = draw_section("TRANSFER DETAILS", y)
        c.setFont("Helvetica", 11)
        
        c.drawString(left_margin + 0.3*cm, y, f"Transfer ID: {transfer.transfer_id}")
        y -= line_height
        
        c.drawString(left_margin + 0.3*cm, y, f"Reason: {transfer.reason}")
        y -= line_height
        
        c.drawString(left_margin + 0.3*cm, y, f"Initiated By: {initiator_name}")
        y -= line_height
        
        c.drawString(left_margin + 0.3*cm, y, f"Date: {transfer.requested_at.strftime('%Y-%m-%d')}")
        y -= line_height * 1.5
        
        # MOVEMENT Section
        y = draw_section("MOVEMENT", y)
        c.setFont("Helvetica-Bold", 11)
        
        col1_x = left_margin + 0.3*cm
        col2_x = left_margin + (content_width / 2)
        
        c.drawString(col1_x, y, "FROM (Origin)")
        c.drawString(col2_x, y, "TO (Destination)")
        y -= line_height
        
        c.setFont("Helvetica", 10)
        
        # FROM details
        if from_name:
            c.drawString(col1_x, y, f"User: {from_name}")
        if from_loc:
            y_temp = y if not from_name else y - 0.4*cm
            c.drawString(col1_x, y_temp, f"Location: {from_loc}")
        
        # TO details
        if to_name:
            c.drawString(col2_x, y, f"User: {to_name}")
        if to_loc:
            y_temp = y if not to_name else y - 0.4*cm
            c.drawString(col2_x, y_temp, f"Location: {to_loc}")
        
        y -= line_height * 2.5
        
        # SIGNATURES Section
        signature_y = 6 * cm
        
        c.setFillColor(sky_blue)
        c.rect(left_margin, signature_y + 3*cm, content_width, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(darker_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.3*cm, signature_y + 3.25*cm, "AUTHORIZATION & SIGNATURES")
        c.setFillColor(colors.black)
        
        # Three signature boxes
        box_width = (content_width - 1*cm) / 3
        boxes = [
            {
                "x": left_margin + 0.3*cm,
                "label": "Initiated By:",
                "name": initiator_name
            },
            {
                "x": left_margin + 0.3*cm + box_width + 0.5*cm,
                "label": "Handed Over By:",
                "name": from_name if from_name else "Location Manager"
            },
            {
                "x": left_margin + 0.3*cm + 2*box_width + 1*cm,
                "label": "Received By:",
                "name": to_name if to_name else "Location Manager"
            }
        ]
        
        c.setFont("Helvetica-Bold", 10)
        for box in boxes:
            c.drawString(box["x"], signature_y + 2.3*cm, box["label"])
            c.setFont("Helvetica", 9)
            c.drawString(box["x"], signature_y + 1.9*cm, box["name"])
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.line(box["x"], signature_y + 0.8*cm, box["x"] + box_width - 0.5*cm, signature_y + 0.8*cm)
            c.setFont("Helvetica", 8)
            c.drawString(box["x"], signature_y + 0.3*cm, "Signature / Date")
            c.setFont("Helvetica-Bold", 10)
        
        c.save()
        return file_path
    
    @staticmethod
    def generate_asset_holder_form(user_name: str, user_id: str, assets: list) -> str:
        """
        Generate Asset Holder Form PDF listing all assets assigned to a user.
        """
        from datetime import datetime
        
        filename = f"asset_holder_form_{user_id}.pdf"
        output_dir = os.path.join(settings.UPLOAD_DIR, "transfers")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Colors
        sky_blue = colors.Color(0.53, 0.81, 0.92)
        darker_blue = colors.Color(0.25, 0.41, 0.88)
        
        # Border
        c.setStrokeColor(darker_blue)
        c.setLineWidth(2)
        c.rect(1.5*cm, 1.5*cm, width-3*cm, height-3*cm)
        
        # Logo
        logo_path = "planlogo.png"
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 2.5*cm, height-4*cm, width=3.5*cm, preserveAspectRatio=True, mask='auto')
        
        # Title
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(darker_blue)
        c.drawCentredString(width/2, height-3*cm, "ASSET HOLDER FORM")
        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, height-3.6*cm, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # User Information
        y = height - 5.5 * cm
        left_margin = 2.5 * cm
        content_width = width - 5 * cm
        
        # User Section
        c.setFillColor(sky_blue)
        c.rect(left_margin, y - 0.7*cm, content_width, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(darker_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.3*cm, y - 0.45*cm, "ASSET HOLDER DETAILS")
        c.setFillColor(colors.black)
        y -= 1.2*cm
        
        c.setFont("Helvetica", 11)
        c.drawString(left_margin + 0.3*cm, y, f"Name: {user_name}")
        y -= 0.6*cm
        c.drawString(left_margin + 0.3*cm, y, f"User ID: {user_id}")
        y -= 0.6*cm
        c.drawString(left_margin + 0.3*cm, y, f"Total Assets: {len(assets)}")
        y -= 1.2*cm
        
        # Assets Table Header
        c.setFillColor(sky_blue)
        c.rect(left_margin, y - 0.7*cm, content_width, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(darker_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.3*cm, y - 0.45*cm, "ASSETS IN CUSTODY")
        c.setFillColor(colors.black)
        y -= 1.2*cm
        
        # Table column headers
        c.setFont("Helvetica-Bold", 9)
        col_x = [left_margin + 0.3*cm, left_margin + 5*cm, left_margin + 10*cm, left_margin + 13*cm]
        c.drawString(col_x[0], y, "Asset ID")
        c.drawString(col_x[1], y, "Description")
        c.drawString(col_x[2], y, "Tag Number")
        c.drawString(col_x[3], y, "Status")
        y -= 0.5*cm
        
        # Draw line under headers
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(left_margin, y, left_margin + content_width, y)
        y -= 0.4*cm
        
        # Assets data
        c.setFont("Helvetica", 8)
        for asset in assets:
            if y < 4*cm:  # Check if we need a new page
                c.showPage()
                # Redraw border on new page
                c.setStrokeColor(darker_blue)
                c.setLineWidth(2)
                c.rect(1.5*cm, 1.5*cm, width-3*cm, height-3*cm)
                y = height - 2*cm
            
            c.drawString(col_x[0], y, str(asset.scom_asset_id)[:20])
            desc = f"{asset.asset_name} ({asset.brand})"[:30]
            c.drawString(col_x[1], y, desc)
            c.drawString(col_x[2], y, str(asset.physical_asset_tag_number or "N/A")[:15])
            c.drawString(col_x[3], y, str(asset.asset_status)[:15])
            y -= 0.5*cm
        
        # Signature section at bottom
        signature_y = 3 * cm
        
        c.setFillColor(sky_blue)
        c.rect(left_margin, signature_y + 2*cm, content_width, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(darker_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.3*cm, signature_y + 2.25*cm, "ACKNOWLEDGMENT")
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 0.3*cm, signature_y + 1.5*cm, 
                     "I acknowledge that I have received and am responsible for the above assets.")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 0.3*cm, signature_y + 0.8*cm, f"Asset Holder: {user_name}")
        
        # Signature line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(left_margin + 5*cm, signature_y + 0.3*cm, left_margin + content_width - 2*cm, signature_y + 0.3*cm)
        c.setFont("Helvetica", 8)
        c.drawString(left_margin + 5*cm, signature_y, "Signature / Date")
        
        c.save()
        return file_path

