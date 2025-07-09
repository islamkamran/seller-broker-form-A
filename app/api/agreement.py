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
        self.image("uploads/indus.png", x=25, y=5, w=25)  # Smaller image, adjusted position
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
        estimated_height = (len(data) * 7) + 10
        if self.get_y() + estimated_height > self.h - 10:
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
    
    # Header with contract number instead of date
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Contract Number: {data['contract_number']}", ln=1, align="R")
    pdf.ln(4)
    
    # PART 1: AGENT DETAILS
    pdf.section_title("PART 1 - AGENT DETAILS")
    
    agent_data = {
        "Office Name": data['office_name'],
        "License Authority": data['license_authority'],
        "OR Number": data['agent_orn'],
        "License No": data['agent_license_no'],
        "Fax": data['agent_fax'],
        "Phone": data['agent_phone'],
        "Address": data['agent_address'],
        "Email": data['agent_email'],
        "Agent Name": data['agent_name'],
        "BRN": data['agent_brn'],
        "Mobile": data['agent_mobile'],
        "Personal Email": data['agent_email_personal']
    }
    pdf.bordered_section("AGENT INFORMATION", agent_data)
    pdf.ln(10)
    
    # PART 2: OWNER DETAILS
    pdf.section_title("PART 2 - OWNER DETAILS")
    
    owner_data = {
        "Name": data['name_of_owner'],
        "ID Card Number": data['id_card_number'],
        "Nationality": data['nationality'],
        "Passport Number": data['passport_number'],
        "Expiry Date": data['expiry_date'],
        "Mobile": data['owner_mobile'],
        "PO Box": data['po_box'],
        "Phone": data['owner_phone'],
        "Fax": data['owner_fax'],
        "Address": data['owner_address'],
        "Email": data['owner_email']
    }
    pdf.bordered_section("OWNER INFORMATION", owner_data)
    pdf.ln(140)
    
    # PART 3: PROPERTY DETAILS
    pdf.section_title("PART 3 - PROPERTY DETAILS")
    
    property_data = {
        "Property Status": data['property_status'],
        "Plot Number": data['plot_number'],
        "Type of Area": data['type_of_area'],
        "Title Deed Number": data['title_deed_number'],
        "Location": data['property_location'],
        "Property Number": data['property_number'],
        "Type": data['type_of_property'],
        "Project Name": data['project_name'],
        "Area": data['property_area'],
        "Owners Association No": data['owners_association_no'],
        "Present Use": data['present_use'],
        "Community Number": data['community_number'],
        "Approx. Age": data['property_approx_age'],
        "No. of Car Parks": data['no_of_car_parks'],
        "No. of Bedrooms": data['no_of_bedrooms'],
        "No. of Bathrooms": data['no_of_bathrooms'],
        "No. of Kitchens": data['no_of_kitchens'],
        "No. of Units": ", ".join(data['no_of_units']),
        "Floor No": data['floor_no'],
        "No. of Floors": data['no_of_floors'],
        "No. of Shops": data['no_of_shops'],
        "Facilities": data['facilities'],
        "Extra Facilities": data['extra_facilities'],
        "Additional Information": data['additional_information']
    }
    pdf.bordered_section("PROPERTY INFORMATION", property_data)
    pdf.ln(40)
    
    # PART 4: FINANCIAL DETAILS
    pdf.section_title("PART 4 - FINANCIAL DETAILS")
    
    financial_data = {
        "Listed Price": data['listed_price'],
        "Original Price": data['orignal_price'],
        "Paid Amount": data['paid_amount'],
        "Balance Amount": data['balance_amount'],
        "Service Charge": data['service_charge'],
        "Mortgage Status": data['mortgage_status'],
        "Mortgage Registration No": data['mortgage_registeration_no'],
        "Bank": data['bank'],
        "Mortgage Amount": data['mortgage_amount'],
        "Pre-Closure Charges": data['pre_closure_charges'],
        "Payment Schedule": data['payment_schedule'],
        "Next Payment Date": data['payment_date'],
        "Amount (AED)": data['amount_aed'],
        "Is Property Rented": "Yes" if data['is_property_rented'] else "No",
        "Contract Start Date": data['contract_start_date'],
        "Contract End Date": data['contract_end_date'],
        "Commission Amount": data['commission_amount']
    }
    pdf.bordered_section("FINANCIAL INFORMATION", financial_data)
    pdf.ln(8)
    
    # PART 5: CONTRACT DETAILS
    pdf.section_title("PART 5 - CONTRACT DETAILS")
    
    contract_data = {
        "Contract Type": data['contract_type'],
        "Activity Reporting": data['activity_reporting']
    }
    pdf.bordered_section("CONTRACT INFORMATION", contract_data)
    pdf.ln(40)
    
    # PART 6: SIGNATURES
    pdf.section_title("PART 6 - SIGNATURES")
    
    # Broker Office Signature
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Broker Office:", ln=1)
    pdf.set_font("Arial", "", 10)
    
    broker_data = f"Name: {data['broker_office_name']}      Title: {data['broker_office_title']}        Dated: {data['broker_office_signature_date']}"
    
    # Broker signature and stamp
    start_y = pdf.get_y()
    
    pdf.multi_cell(120, 0, str(broker_data), 0, "L")
    pdf.image("uploads/stamp.png", x=30, y=start_y-12, w=40)
    pdf.ln(25)
    
    # Owner Signature
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Owner:", ln=1)
    pdf.set_font("Arial", "", 10)
    
    owner_sig_data = f"Name: {data['owner_name']}       Dated: {data['broker_office_signature_date']}"
    
    start_y = pdf.get_y()
    pdf.multi_cell(120, 6, str(owner_sig_data), 0, "L")
    pdf.ln(25)
    
    # Legal Representative (if exists)
    if data['legal_representative']:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "Legal Representative:", ln=1)
        pdf.set_font("Arial", "", 10)
        
        legal_data = f"Name: {data['legal_representative']}     Attorney Number: {data['attorney_number']}      Dated: {data['broker_office_signature_date']}"
        
        start_y = pdf.get_y()
        pdf.multi_cell(150, 6, str(legal_data), 0, "L")
    
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
        "mortgage_amount": mortgage_amount,
        "pre_closure_charges": pre_closure_charges,
        "payment_schedule": payment_schedule,
        "payment_date": payment_date,
        "amount_aed": amount_aed,
        "is_property_rented":is_property_rented.lower() == "yes",
        "contract_start_date":contract_start_date,
        "contract_end_date":contract_end_date,
        "commission_amount":commission_amount,
        "contract_type":contract_type,
        "activity_reporting": activity_reporting,
        "broker_office_name": broker_office_name,
        "broker_office_title": broker_office_title,
        "broker_office_signature_date": broker_office_signature_date,
        "broker_office_signature": broker_office_signature,
        "owner_name": owner_name,
        "owner_signature": owner_signature,
        "legal_representative":legal_representative,
        "attorney_number": attorney_number,
        "legal_representative_signature": legal_representative_signature
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