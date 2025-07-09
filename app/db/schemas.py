from pydantic import BaseModel
from datetime import date
from typing import Optional
from typing import List, Optional

class AgentAgreementBase(BaseModel):
    contract_number: str
    office_name: str
    license_authority: str
    agent_orn:str
    agent_license_no:str
    agent_fax:str
    agent_phone:str
    agent_address:str
    agent_emai:str
    agent_name:str
    agent_brn:str
    agent_mobile:str
    agent_email_personal:str
    name_of_owner:str
    id_card_number:str
    nationality:str
    passport_number:str
    expiry_date:date
    owner_mobile:str
    po_box:str
    owner_phone:str
    owner_fax:str
    owner_address:str
    owner_email:str
    property_status:str
    plot_number:str
    type_of_area:str
    title_deed_number:str
    property_location:str
    property_number:str
    type_of_property:str
    project_name:str
    property_area:str
    owners_association_no:str
    present_use:str
    community_number:str
    property_approx_age:str
    no_of_car_parks:str
    no_of_bedrooms:str
    no_of_bathrooms:str
    no_of_kitchens:str
    no_of_units:str
    floor_no:str
    no_of_floors:str
    no_of_shops:str
    facilities:str
    extra_facilities:str
    additional_information:str
    listed_price:str
    orignal_price:str
    paid_amount:str
    balance_amount:str
    service_charge:str
    mortgage_status:str
    mortgage_registeration_no:str
    bank:str
    mortgage_amount: str
    pre_closure_charges: str
    payment_schedule: str
    payment_date: str
    amount_aed: str
    is_property_rented:bool
    contract_start_date:date
    contract_end_date:date
    commission_amount:str
    contract_type:str
    activity_reporting: str
    broker_office_name: str
    broker_office_title: str
    broker_office_signature_date: date
    broker_office_signature: str
    owner_name: str
    owner_signature: str
    legal_representative:str
    attorney_number: str
    legal_representative_signature: str

class AgentAgreementCreate(AgentAgreementBase):
    pass

class AgentAgreement(AgentAgreementBase):
    id: int
    created_at: date
    
    class Config:
        orm_mode = True