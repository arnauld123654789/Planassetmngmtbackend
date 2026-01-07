import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from app.core.config import settings
from app.models.operations import Transfer
from app.models.asset import Asset

class PDFService:
    @staticmethod
    def generate_transfer_pdf(transfer: Transfer, asset: Asset, initiator_name: str, 
                              from_name: str, to_name: str, from_loc: str, to_loc: str,
                              approver_name: str, approval_date: datetime) -> str:
        
        import tempfile
        # Use temp file - not stored permanently
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="transfer_")
        file_path = temp_file.name
        temp_file.close()
        
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
        line_height = 0.7 * cm
        
        # 1. Asset ID
        c.drawString(left_margin + 0.3*cm, y, f"Asset ID: {asset.scom_asset_id}")
        y -= line_height
        
        # 2. Destination (To Location / User)
        dest_text = to_loc if to_loc else (to_name if to_name else "N/A")
        c.drawString(left_margin + 0.3*cm, y, f"Destination: {dest_text}")
        y -= line_height

        # 3. Acquisition Date
        acq_date = asset.date_of_acquisition.strftime('%Y-%m-%d') if asset.date_of_acquisition else "N/A"
        c.drawString(left_margin + 0.3*cm, y, f"Acquisition Date: {acq_date}")
        y -= line_height

        # 4. Price
        price_text = f"{asset.acquisition_price:,.2f} {asset.currency}" if asset.acquisition_price else "N/A"
        c.drawString(left_margin + 0.3*cm, y, f"Price: {price_text}")
        y -= line_height

        # 5. Tag Number
        c.drawString(left_margin + 0.3*cm, y, f"Tag Number: {asset.physical_asset_tag_number or 'N/A'}")
        y -= line_height
        
        # 6. Status
        status_text = str(asset.asset_status).replace("AssetStatus.", "")
        c.drawString(left_margin + 0.3*cm, y, f"Status: {status_text}")
        y -= line_height

        # 7. Previous Owner (From Location / User)
        prev_owner_text = from_loc if from_loc else (from_name if from_name else "N/A")
        c.drawString(left_margin + 0.3*cm, y, f"Previous Owner: {prev_owner_text}")
        y -= line_height * 1.5
        
        # Description (Keeping it as it's useful context, though not explicitly requested to remove)
        desc_text = f"{asset.asset_name} ({asset.brand} {asset.model})"
        c.drawString(left_margin + 0.3*cm, y, f"Description: {desc_text}")
        y -= line_height * 2
        
        # SIGNATURES Section
        signature_y = 6 * cm
        
        c.setFillColor(sky_blue)
        c.rect(left_margin, signature_y + 3*cm, content_width, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(darker_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin + 0.3*cm, signature_y + 3.25*cm, "AUTHORIZATION & SIGNATURES")
        c.setFillColor(colors.black)
        
        # Three signature boxes: Initiator, Approver, Receiver
        box_width = (content_width - 1*cm) / 3
        
        # Prepare dates
        init_date = transfer.requested_at.strftime('%Y-%m-%d')
        app_date = approval_date.strftime('%Y-%m-%d') if approval_date else "N/A"

        boxes = [
            {
                "x": left_margin + 0.3*cm,
                "label": "Initiated By:",
                "name": initiator_name,
                "date_label": f"Date: {init_date}"
            },
            {
                "x": left_margin + 0.3*cm + box_width + 0.5*cm,
                "label": "Approved By:",
                "name": approver_name,
                "date_label": f"Date: {app_date}"
            },
            {
                "x": left_margin + 0.3*cm + 2*box_width + 1*cm,
                "label": "Received By:",
                "name": to_name if to_name else "Location Manager",
                "date_label": "" # No date for receiver
            }
        ]
        
        c.setFont("Helvetica-Bold", 10)
        for box in boxes:
            c.drawString(box["x"], signature_y + 2.3*cm, box["label"])
            c.setFont("Helvetica", 9)
            c.drawString(box["x"], signature_y + 1.9*cm, box["name"])
            
            # Signature Line
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.line(box["x"], signature_y + 1.2*cm, box["x"] + box_width - 0.5*cm, signature_y + 1.2*cm)
            
            c.setFont("Helvetica", 8)
            c.drawString(box["x"], signature_y + 0.8*cm, "Signature")
            
            # Date below signature (only if label exists)
            if box["date_label"]:
                c.setFont("Helvetica", 9)
                c.drawString(box["x"], signature_y + 0.3*cm, box["date_label"])
            
            c.setFont("Helvetica-Bold", 10)
        
        # Generated Date at the very end (Footer)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, 2*cm, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        c.save()
        return file_path
    
    @staticmethod
    def generate_asset_holder_form(user_name: str, user_id: str, assets_data: list, generator_name: str) -> str:
        """
        Generate Asset Holder Form PDF listing all assets assigned to a user.
        assets_data is a list of dicts: {'asset': Asset, 'attribution_date': datetime|None}
        """
        from datetime import datetime
        
        import tempfile
        # Use temp file - not stored permanently
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="asset_holder_")
        file_path = temp_file.name
        temp_file.close()
        
        # Landscape A4
        page_size = landscape(A4)
        c = canvas.Canvas(file_path, pagesize=page_size)
        width, height = page_size
        
        # Color Palette - Professional & Clean
        primary_blue = colors.Color(0.20, 0.35, 0.60) # Deep Navy
        secondary_blue = colors.Color(0.90, 0.95, 0.98) # Very Light Blue for backgrounds
        accent_line = colors.Color(0.70, 0.70, 0.70) # Light Grey for lines
        
        # Layout Constants
        margin = 1.5 * cm
        content_width = width - (2 * margin)
        
        # --- HEADER SECTION ---
        # Logo on Left
        logo_path = "planlogo.png"
        logo_width = 3 * cm
        logo_height = 0
        
        # Draw Logo if exists
        if os.path.exists(logo_path):
            logo_height = 2.5 * cm
            # Place logo at top left inside margin
            c.drawImage(logo_path, margin, height - margin - logo_height, width=logo_width, preserveAspectRatio=True, mask='auto')
        
        # Title Centered relative to content, but offset by logo to avoid overlap if needed
        # Actually, let's put Title clearly to the right of Logo
        title_y = height - margin - 1.2 * cm
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(primary_blue)
        # Center title in the remaining space or just center of page
        c.drawCentredString(width / 2, title_y, "ASSET HOLDER FORM")
        
        # Generated Date - Top Right
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        c.drawRightString(width - margin, height - margin - 1 * cm, f"Generated: {date_str}")
        
        # Horizontal Line below Header
        y = height - margin - 2.8 * cm
        c.setStrokeColor(primary_blue)
        c.setLineWidth(2)
        c.line(margin, y, width - margin, y)
        
        # --- USER INFO SECTION ---
        y -= 0.5 * cm
        
        # Background box for User Info
        c.setFillColor(secondary_blue)
        # Rect: x, y, w, h (y is bottom left)
        # We need a height of about 2cm
        box_height = 1.8 * cm
        c.rect(margin, y - box_height, content_width, box_height, fill=1, stroke=0)
        
        # User Details labels - Adjusted spacing to avoid overlaps
        text_y = y - 1 * cm
        c.setFillColor(primary_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 0.5 * cm, text_y, "Asset Holder:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(margin + 3.8 * cm, text_y, user_name)
        
        # Move User ID to 11cm to give more space for the ID value
        # Gap for Name: ~7cm (11 - 3.8 - padding)
        c.setFillColor(primary_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 11.0 * cm, text_y, "User ID:") 
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(margin + 13.0 * cm, text_y, user_id)
        
        # Move Total Assets to 22.5cm to leave ~9.5cm for User ID
        c.setFillColor(primary_blue)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 22.5 * cm, text_y, "Total Assets:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(margin + 25.5 * cm, text_y, str(len(assets_data)))
        
        # Move Y down below box
        y -= (box_height + 1 * cm)
        
        # --- ASSETS TABLE ---
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=rl_colors.white,
            alignment=TA_CENTER
        )
        
        cell_style = ParagraphStyle(
            'CustomCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            alignment=TA_CENTER,
            leading=10
        )
        
        # Columns: SCOMID, Name, Acq. Price, Acq. Date, Serial No., Attr. Date, Status
        headers = ["SCOMID", "Name", "Acq. Price", "Acq. Date", "Serial No.", "Attr. Date", "Status"]
        table_data = [[Paragraph(h, header_style) for h in headers]]
        
        for item in assets_data:
            asset = item['asset']
            attr_date = item['attribution_date']
            
            # Format dates
            acq_date_str = asset.date_of_acquisition.strftime('%Y-%m-%d') if asset.date_of_acquisition else "-"
            attr_date_str = attr_date.strftime('%Y-%m-%d') if attr_date else "N/A"
            
            # Format Price
            currency = asset.currency if asset.currency else ""
            price_str = f"{asset.acquisition_price:,.2f} {currency}" if asset.acquisition_price else "-"
            
            status = str(asset.asset_status).replace("AssetStatus.", "")
            
            table_data.append([
                Paragraph(str(asset.scom_asset_id), cell_style),
                Paragraph(asset.asset_name, cell_style),
                Paragraph(price_str, cell_style),
                Paragraph(acq_date_str, cell_style),
                Paragraph(str(asset.physical_asset_tag_number or "-"), cell_style),
                Paragraph(attr_date_str, cell_style),
                Paragraph(status, cell_style)
            ])
        
        # Column Widths
        # Total Width = ~29.7cm - 3cm = 26.7cm
        # Let's distribute
        col_widths = [3.5*cm, 7.5*cm, 3.5*cm, 3*cm, 3.7*cm, 3*cm, 2.5*cm]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            ('BACKGROUND', (0, 1), (-1, -1), rl_colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), rl_colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            ('GRID', (0, 0), (-1, -1), 0.5, accent_line),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [rl_colors.white, secondary_blue]),
        ]))
        
        table_width, table_height = table.wrap(content_width, height)
        
        # Pagination Check
        # Need space for footer (approx 5cm)
        footer_height = 5.5 * cm
        if y - table_height < footer_height:
            c.showPage()
            # New page header simplified
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(width/2, height - 2*cm, "ASSET HOLDER FORM - CONTINUED")
            y = height - 3*cm
        
        table.drawOn(c, margin, y - table_height)
        y = y - table_height - 1.5 * cm
        
        # --- SIGNATURE / ACKNOWLEDGEMENT SECTION ---
        # Ensure we have space
        if y < footer_height:
            c.showPage()
            y = height - 3 * cm
            
        # Draw separate boxes for Supply Chain and Asset Holder
        
        # Box 1: Supply Chain (Generator)
        box_width = (content_width / 2) - 0.5*cm
        box_height = 4.5 * cm
        
        # Left Box
        left_box_x = margin
        left_box_y = y - box_height
        
        c.setStrokeColor(primary_blue)
        c.setFillColor(secondary_blue)
        c.roundRect(left_box_x, left_box_y, box_width, box_height, 4, fill=1, stroke=1)
        
        c.setFillColor(primary_blue)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(left_box_x + box_width/2, left_box_y + box_height - 0.8*cm, "ISSUED BY (SUPPLY CHAIN)")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(left_box_x + 0.5*cm, left_box_y + 2.8*cm, f"Name: {generator_name}")
        c.drawString(left_box_x + 0.5*cm, left_box_y + 2.0*cm, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        c.drawString(left_box_x + 0.5*cm, left_box_y + 0.8*cm, "Signature:")
        c.line(left_box_x + 2.5*cm, left_box_y + 0.8*cm, left_box_x + box_width - 1*cm, left_box_y + 0.8*cm)
        
        # Box 2: Asset Holder (Receiver)
        right_box_x = margin + box_width + 1*cm
        right_box_y = y - box_height
        
        c.setStrokeColor(primary_blue)
        c.setFillColor(secondary_blue)
        c.roundRect(right_box_x, right_box_y, box_width, box_height, 4, fill=1, stroke=1)
        
        c.setFillColor(primary_blue)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(right_box_x + box_width/2, right_box_y + box_height - 0.8*cm, "RECEIVED BY (ASSET HOLDER)")
        
        # Acknowledgement Text
        c.setFillColor(colors.black)
        # BOLD Text request
        c.setFont("Helvetica-Bold", 9)
        ack_text = "I acknowledge receipt and responsibility for the"
        ack_text2 = "assets listed above."
        c.drawCentredString(right_box_x + box_width/2, right_box_y + 3.2*cm, ack_text)
        c.drawCentredString(right_box_x + box_width/2, right_box_y + 2.8*cm, ack_text2)
        
        c.setFont("Helvetica", 10)
        c.drawString(right_box_x + 0.5*cm, right_box_y + 2.0*cm, f"Name: {user_name}")
        c.drawString(right_box_x + 0.5*cm, right_box_y + 1.2*cm, "Date: __________________")
        
        c.drawString(right_box_x + 0.5*cm, right_box_y + 0.4*cm, "Signature:")
        c.line(right_box_x + 2.5*cm, right_box_y + 0.4*cm, right_box_x + box_width - 1*cm, right_box_y + 0.4*cm)
        
        c.save()
        return file_path

