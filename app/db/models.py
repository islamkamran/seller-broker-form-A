from sqlalchemy import Column, Integer, String, Boolean, Date, Text, DateTime, func
from app.db.db_setup import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)


class AgentAgreement(TimestampMixin, Base):
    __tablename__ = "rera_form_a"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # The parties
    contract_number = Column(String(50))

    # Part 1 The parties
    office_name = Column(String(255))
    license_authority = Column(String(255))
    agent_orn = Column(String(50))
    agent_license_no = Column(String(50))
    agent_fax = Column(String(100))
    agent_phone = Column(String(50))
    agent_address = Column(String(50))
    agent_email = Column(String(50))
    agent_name = Column(String(100))
    agent_brn = Column(String(50))
    agent_mobile = Column(String(20))
    agent_email_personal = Column(String(100))
    
    # Owner Details
    name_of_owner = Column(String(255))
    id_card_number = Column(String(255))
    nationality = Column(String(50))
    passport_number = Column(String(50))
    expiry_date = Column(Date)
    owner_mobile = Column(String(50))
    po_box = Column(String(50))
    owner_phone = Column(String(50))
    owner_fax = Column(String(100))
    owner_address = Column(String(50))
    owner_email = Column(String(20))

    # Property Details
    property_status = Column(String(255))
    plot_number = Column(String(100))
    type_of_area = Column(String(100))
    title_deed_number = Column(String(100))
    property_location = Column(String(50))
    property_number = Column(String(50))
    type_of_property = Column(String(50))
    project_name = Column(String(50))
    property_area = Column(String(50))
    owners_association_no = Column(String(100))
    present_use = Column(String(100))
    community_number = Column(String(100))
    property_approx_age = Column(String(100))
    no_of_car_parks = Column(String(100))
    no_of_bedrooms = Column(String(100))
    no_of_bathrooms = Column(String(100))
    no_of_kitchens = Column(String(100))
    no_of_units = Column(String(100))
    floor_no = Column(String(100))
    no_of_floors = Column(String(100))
    no_of_shops = Column(String(100))
    facilities = Column(String(100))
    extra_facilities = Column(String(100))
    additional_information = Column(String(100))

    # Property Financials
    listed_price = Column(String(50))
    orignal_price = Column(String(50))
    paid_amount = Column(String(50))
    balance_amount = Column(String(50))
    service_charge = Column(String(50))
    mortgage_status = Column(String(50))
    mortgage_registeration_no = Column(String(50))
    bank = Column(String(50))
    mortgage_amount = Column(String(50))
    pre_closure_charges = Column(String(50))
    payment_schedule = Column(String(50))
    payment_date = Column(Date)
    amount_aed = Column(String(50))

    # Tenancy Contract Details
    is_property_rented = Column(Boolean)

    # Commission
    contract_start_date = Column(Date)
    contract_end_date = Column(Date)
    commission_amount = Column(String(10))
    contract_type = Column(String(100))
    activity_reporting = Column(String(100))

    # Broker Office Signature
    broker_office_name = Column(String(255))
    broker_office_title = Column(String(255))
    broker_office_signature_date = Column(String(255))
    broker_office_signature = Column(String(255))

    # Owner Signature
    owner_name = Column(String(255))
    owner_signature = Column(String(255))
    legal_representative = Column(String(255))
    attorney_number = Column(String(255))
    legal_representative_signature = Column(String(255))
