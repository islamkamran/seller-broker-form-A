from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from fpdf import FPDF
import os
from typing import List

from app.db.models import AgentAgreement
from app.db.schemas import AgentAgreementCreate
from app.db.db_setup import get_db

router = APIRouter()


class AgreementPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=30)  # Increased bottom margin
        # More generous margins
        self.set_margins(left=25, top=15, right=25)
        self.set_font("Arial", size=10)  # Set default font
    
    def header(self):
        self.image("uploads/indus.png", x=25, y=10, w=25)  # Smaller image, adjusted position
        self.set_font("Arial", "B", 14)  # Slightly smaller title
        self.cell(0, 8, "AGENT TO AGENT AGREEMENT", ln=1, align="C")
        self.set_font("Arial", "", 9)  # Smaller subtitle
        self.cell(0, 5, "As per the Real Estate Brokers By-Law No. (85) of 2006", ln=1, align="C")
        self.ln(8)  # Reduced spacing
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 7)  # Smaller footer text
        self.cell(0, 4, "203 Al Sharafi Building | Bur Dubai, Dubai UAE | P.O Box 118163", ln=1, align="C")
        self.cell(0, 4, "Phone: +971 4 3519995 | Fax: +971 43515611 | www.indus-re.com", ln=1, align="C")
    
    def section_title(self, title):
        if self.get_y() > self.h - 40:  # More conservative page break check
            self.add_page()
        self.set_font("Arial", "B", 11)  # Smaller section titles
        self.cell(0, 6, title, ln=1)
        self.ln(3)  # Reduced spacing
        
    def bordered_section(self, title, data):
        # More conservative height estimation
        estimated_height = (len(data) * 7) + 15
        if self.get_y() + estimated_height > self.h - 40:
            self.add_page()
            
        x_start = self.get_x()
        y_start = self.get_y()
    
        # Narrower section to fit within margins
        section_width = 160
        self.rect(x_start, y_start, section_width, estimated_height)
    
        self.set_font("Arial", "B", 10)  # Smaller title font
        self.cell(0, 6, title, ln=1)
        self.ln(2)
    
        self.set_xy(x_start + 5, self.get_y())
    
        for label, value in data.items():
            self.set_font("Arial", "B", 9)  # Smaller label font
            self.cell(60, 6, f"{label}:", 0, 0, "L")  # Narrower label column
        
            line_x = self.get_x()
            line_y = self.get_y()
            self.line(line_x, line_y, line_x, line_y + 6)  # Shorter divider
            self.cell(3, 6, "", 0, 0)  # Smaller spacer
        
            self.set_font("Arial", "", 9)  # Smaller value font
            value_str = str(value) if value is not None else ""
        
            # Calculate width with new dimensions
            text_width = section_width - 60 - 3 - 10
            self.set_xy(line_x + 3, line_y)
            self.multi_cell(text_width, 6, value_str, 0, "L")  # Smaller line height
        
            self.set_xy(x_start + 5, self.get_y())
            self.line(x_start, self.get_y(), x_start + section_width, self.get_y())
    
        self.set_xy(x_start, y_start + estimated_height)
        self.ln(4)  # Reduced spacing

def generate_agreement(data: dict) -> str:
    pdf = AgreementPDF()
    pdf.add_page()
    
    # Header with date
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Date: {data['dated']}", ln=1, align="R")
    pdf.ln(8)
    
    # PART 1: THE PARTIES
    pdf.section_title("PART 1 - THE PARTIES")
    
    # Agent A Section (updated with all fields)
    agent_a_data = {
        "Establishment": data['agent_a_establishment'],
        "Address": data['agent_a_address'],
        "Phone": data['agent_a_phone'],
        "Fax": data['agent_a_fax'],
        "Email": data['agent_a_email'],
        "OR Number": data['agent_a_orn'],
        "License": data['agent_a_license'],
        "PO Box": data['agent_a_po_box'],
        "Emirates": data['agent_a_emirates'],
        "Agent Name": data['agent_a_name'],
        "BRN": data['agent_a_brn'],
        "Date Issued": data['agent_a_date_issued'],
        "Mobile": data['agent_a_mobile'],
        "Personal Email": data['agent_a_email_personal']
    }
    pdf.bordered_section("A) THE AGENT (LANDLORD'S AGENT)", agent_a_data)
    
    # Agent B Section (updated with all fields)
    agent_b_data = {
        "Establishment": data['agent_b_establishment'],
        "Address": data['agent_b_address'],
        "Phone": data['agent_b_phone'],
        "Fax": data['agent_b_fax'],
        "Email": data['agent_b_email'],
        "OR Number": data['agent_b_orn'],
        "License": data['agent_b_license'],
        "PO Box": data['agent_b_po_box'],
        "Emirates": data['agent_b_emirates'],
        "Agent Name": data['agent_b_name'],
        "BRN": data['agent_b_brn'],
        "Date Issued": data['agent_b_date_issued'],
        "Mobile": data['agent_b_mobile'],
        "Personal Email": data['agent_b_email_personal']
    }
    pdf.bordered_section("B) THE AGENT (TENANT'S AGENT)", agent_b_data)
    pdf.ln(8)
    
    # PART 2: THE PROPERTY
    pdf.section_title("PART 2 - THE PROPERTY")
    
    property_data = {
        "Address": data['property_address'],
        "Master Developer": data['master_developer'],
        "Master Project": data['master_project'],
        "Building Name": data['building_name'],
        "Listed Price": data['listed_price'],
        "Description": data['property_description'],
        "MOU Exists": "Yes" if data['mou_exist'] else "No",
        "Property Tenanted": "Yes" if data['property_tenanted'] else "No",
        "Maintenance Description Fee P.A": f"{data['maintenance_description']} per sq.ft"
    }
    pdf.bordered_section("PROPERTY DETAILS", property_data)
    pdf.ln(8)
    
    # PART 3: THE COMMISSION
    pdf.section_title("PART 3 - THE COMMISSION")
    
    commission_data = {
        "Seller Agent %": f"{data['seller_agent_percent']}%",
        "Buyer Agent %": f"{data['buyer_agent_percent']}%",
        "Buyer Name": data['buyer_name'],
        "Transfer Fee Paid By": data['transfer_fee'].replace(",", " & "),
        "Pre-Finance Approval": "Yes" if data['pre_finance_approval'] else "No",
        "Buyer Contacted Agent": "Yes" if data['buyer_contacted_agent'] else "No"
    }
    pdf.bordered_section("COMMISSION DETAILS", commission_data)
    pdf.ln(8)
    
    # PART 4: SIGNATURES
    pdf.section_title("PART 4 - SIGNATURES")
    
    # Notice text with better formatting
    pdf.set_font("Arial", "", 9)
    notice_text = [
        "Both Agents are required to co-operate fully, complete this FORM & BOTH retain a fully signed & stamped copy on file."
    ]
    
    for line in notice_text:
        if line:
            pdf.cell(0, 5, line, ln=1)
        else:
            pdf.ln(3)
    
    pdf.ln(10)
    
    # Signature lines with actual signatures
    pdf.set_font("Arial", "", 10)
    # Agent A Section
    # First get the current Y position
    start_y = pdf.get_y()

    # Signature
    pdf.cell(50, 10, f"Agent A: {data['agent_a_signature']}", 0, 0, "C")
    # Stamp (positioned relative to signature)
    pdf.image("uploads/stamp.png", x=30, y=start_y-5, w=40)

    # Agent B Section - same approach
    start_y = pdf.get_y() - 5  # Reset to align with Agent A section
    pdf.cell(110, 10, f"Agent B: {data['agent_b_signature']}", 0, 0, "C")
    
    # Move down for the "Signature & Stamp" label
    pdf.ln(15)  # Adjust this value to position the text properly
    pdf.cell(50, 10, "Signature & Stamp", 0, 0, "C")


    # Save PDF
    os.makedirs("pdf_output", exist_ok=True)
    filename = f"pdf_output/agreement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    
    return filename

@router.post("/v1/submit-agreement")
async def create_agreement(
    request: Request,
    contract_number: str = Form(...),
    office_name: str = Form(...),
    license_authority: str = Form(...),
    agent_orn: str = Form(...),
    agent_license_no: str = Form(...),
    agent_fax: str = Form(...),
    agent_phone: str = Form(...),
    agent_address: str = Form(...),
    agent_email: str = Form(...),
    agent_name: str = Form(...),
    agent_brn: str = Form(None),
    agent_mobile: str = Form(...),
    agent_email_personal: str = Form(...),
    name_of_owner: str = Form(...),
    id_card_number: str = Form(...),
    nationality: str = Form(...),
    passport_number: str = Form(...),
    expiry_date: str = Form(...),
    owner_mobile: str = Form(...),
    po_box: str = Form(...),
    owner_phone: str = Form(...),
    owner_fax: str = Form(...),
    owner_address: str = Form(...),
    owner_email: str = Form(...),
    property_status: str = Form(...),
    plot_number: str = Form(...),
    type_of_area: str = Form(...),
    title_deed_number: str = Form(...),
    property_location: str = Form(...),
    property_number: str = Form(...),
    type_of_property: str = Form(...),
    project_name: str = Form(...),
    property_area: str = Form(...),
    owners_association_no: str = Form(...),
    present_use: str = Form(...),
    community_number: str = Form(...),
    property_approx_age: str = Form(...),
    no_of_car_parks: str = Form(...),
    no_of_bedrooms: str = Form(...),
    no_of_bathrooms: str = Form(...),
    no_of_kitchens: str = Form(...),
    no_of_units: List[str] = Form(...), 
    floor_no: str = Form(...),
    no_of_floors: str = Form(...),
    no_of_shops: str = Form(...),
    facilities: str = Form(...),
    extra_facilities: str = Form(...),
    additional_information: str = Form(...),
    listed_price: str = Form(...),
    orignal_price: str = Form(...),
    paid_amount: str = Form(...),
    balance_amount: str = Form(...),
    service_charge: str = Form(...),
    mortgage_status: str = Form(...),
    mortgage_registeration_no: str = Form(...),
    bank: str = Form(...),

    # ------------------------- start from here ----------------------
    mortgage_amount: str = Form(...),
    pre_closure_charges: str = Form(...),
    payment_schedule: str = Form(...),
    payment_date: str = Form(...),
    amount_aed: str = Form(...),
    is_property_rented: str = Form(...),
    contract_start_date: str = Form(...),
    contract_end_date: str = Form(...),
    commission_amount: str = Form(...),
    contract_type: str = Form(...),
    activity_reporting: str = Form(...),
    broker_office_name: str = Form(...),
    broker_office_title: str = Form(...),
    broker_office_signature_date: str = Form(...),
    broker_office_signature: str = Form(...),
    owner_name: str = Form(...),
    owner_signature: str = Form(...),
    legal_representative: str = Form(...),
    attorney_number: str = Form(...),
    legal_representative_signature: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert form data to dict

    transfer_fee_str = ",".join(transfer_fee)  # "buyer,seller"
    print(transfer_fee_str)
    agreement_data = {
        "contract_number": contract_number,
        "office_name": office_name,
        "license_authority": license_authority,
        "agent_orn":agent_orn,
        "agent_license_no":agent_license_no,
        "agent_fax":agent_fax,
        "agent_phone":agent_phone,
        "agent_address":agent_address,
        "agent_email":agent_email,
        "agent_name":agent_name,
        "agent_brn":agent_brn,
        "agent_mobile":agent_mobile,
        "agent_email_personal":agent_email_personal,
        "name_of_owner":name_of_owner,
        "id_card_number":id_card_number,
        "nationality":nationality,
        "passport_number":passport_number,
        "expiry_date":expiry_date,
        "owner_mobile":owner_mobile,
        "po_box":po_box,
        "owner_phone":owner_phone,
        "owner_fax":owner_fax,
        "owner_address":owner_address,
        "owner_email":owner_email,
        "property_status":property_status,
        "plot_number":plot_number,
        "type_of_area":type_of_area,
        "title_deed_number":title_deed_number,
        "property_location":property_location,
        "property_number":property_number,
        "type_of_property":type_of_property,
        "project_name":project_name,
        "property_area":property_area,
        "owners_association_no":owners_association_no,
        "present_use":present_use,
        "community_number":community_number,
        "property_approx_age":property_approx_age,
        "no_of_car_parks":no_of_car_parks,
        "no_of_bedrooms":no_of_bedrooms,
        "no_of_bathrooms":no_of_bathrooms,
        "no_of_kitchens":no_of_kitchens,
        "no_of_units":no_of_units,
        "floor_no":floor_no,
        "no_of_floors":no_of_floors,
        "no_of_shops":no_of_shops,
        "facilities":facilities,
        "extra_facilities":extra_facilities,
        "additional_information":additional_information,
        "listed_price":listed_price,
        "orignal_price":orignal_price,
        "paid_amount":paid_amount,
        "balance_amount":balance_amount,
        "service_charge":service_charge,
        "mortgage_status":mortgage_status,
        "mortgage_registeration_no":mortgage_registeration_no,
        "bank":bank,
        # ------------------------- start from here ----------------------

        "mou_exist": mou_exist.lower() == "yes",
        "property_tenanted":property_tenanted.lower() == "yes",
        "maintenance_description":maintenance_description,
        "seller_agent_percent":seller_agent_percent,
        "buyer_agent_percent":buyer_agent_percent,
        "buyer_name":buyer_name,
        "transfer_fee": transfer_fee_str,
        "pre_finance_approval": pre_finance_approval.lower() == "yes",
        "buyer_contacted_agent": buyer_contacted_agent.lower() == "yes",
        "agent_a_signature": agent_a_signature,
        "agent_b_signature": agent_b_signature
    }

    # Create database record
    db_agreement = AgentAgreement(**agreement_data)
    db.add(db_agreement)
    db.commit()
    db.refresh(db_agreement)

    # Generate PDF
    pdf_path = generate_agreement(agreement_data)

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename="agent_agreement.pdf"
    )