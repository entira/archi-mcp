"""Industry-specific ArchiMate templates."""

from typing import Dict, List, Any, Optional
from .viewpoints import ViewpointTemplate


class IndustryTemplate:
    """Template for industry-specific architectures."""
    
    def __init__(
        self,
        name: str,
        description: str,
        industry: str,
        elements: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        layout: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.industry = industry
        self.elements = elements
        self.relationships = relationships
        self.layout = layout or {}


# Industry-specific templates
INDUSTRY_TEMPLATES = {
    "banking": IndustryTemplate(
        name="Core Banking System",
        description="Core banking system architecture for financial institutions",
        industry="banking",
        elements=[
            {
                "id": "customer",
                "name": "Customer",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Bank customer"
            },
            {
                "id": "teller",
                "name": "Bank Teller", 
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Bank employee"
            },
            {
                "id": "account_service",
                "name": "Account Management",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Account management services"
            },
            {
                "id": "core_banking_app",
                "name": "Core Banking System",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Main banking application"
            },
            {
                "id": "customer_database",
                "name": "Customer Database",
                "element_type": "Technology_Node",
                "layer": "Technology",
                "description": "Customer data storage"
            }
        ],
        relationships=[
            {
                "id": "customer_uses_service",
                "from_element": "customer",
                "to_element": "account_service",
                "relationship_type": "Serving"
            },
            {
                "id": "teller_provides_service",
                "from_element": "teller",
                "to_element": "account_service",
                "relationship_type": "Assignment"
            },
            {
                "id": "app_realizes_service",
                "from_element": "core_banking_app",
                "to_element": "account_service",
                "relationship_type": "Realization"
            },
            {
                "id": "app_accesses_db",
                "from_element": "core_banking_app",
                "to_element": "customer_database",
                "relationship_type": "Access"
            }
        ],
        layout={"direction": "vertical", "group_by_layer": True}
    ),
    
    "banking_core": IndustryTemplate(
        name="Core Banking System",
        description="Core banking system architecture for financial institutions",
        industry="banking",
        elements=[
            {
                "id": "customer",
                "name": "Customer",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Bank customer"
            },
            {
                "id": "teller",
                "name": "Bank Teller",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Bank employee"
            },
            {
                "id": "account_service",
                "name": "Account Management",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Account management services"
            },
            {
                "id": "transaction_service",
                "name": "Transaction Processing",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Transaction processing services"
            },
            {
                "id": "core_banking_app",
                "name": "Core Banking Application",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Main banking application"
            },
            {
                "id": "customer_portal",
                "name": "Customer Portal",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Online banking portal"
            },
            {
                "id": "account_data",
                "name": "Account Database",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Customer account data"
            }
        ],
        relationships=[
            {
                "id": "customer_account",
                "from_element": "customer",
                "to_element": "account_service",
                "relationship_type": "Serving"
            },
            {
                "id": "teller_transaction",
                "from_element": "teller",
                "to_element": "transaction_service",
                "relationship_type": "Serving"
            },
            {
                "id": "portal_account",
                "from_element": "customer_portal",
                "to_element": "account_service",
                "relationship_type": "Realization"
            },
            {
                "id": "core_transaction",
                "from_element": "core_banking_app",
                "to_element": "transaction_service",
                "relationship_type": "Realization"
            },
            {
                "id": "core_data_access",
                "from_element": "core_banking_app",
                "to_element": "account_data",
                "relationship_type": "Access"
            }
        ]
    ),
    
    "ecommerce_platform": IndustryTemplate(
        name="E-commerce Platform",
        description="E-commerce platform architecture for retail businesses",
        industry="retail",
        elements=[
            {
                "id": "customer_ecom",
                "name": "Online Customer",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "E-commerce customer"
            },
            {
                "id": "product_catalog_service",
                "name": "Product Catalog",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Product browsing and search"
            },
            {
                "id": "order_service_ecom",
                "name": "Order Management",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Order processing and fulfillment"
            },
            {
                "id": "payment_service_ecom",
                "name": "Payment Processing",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Payment processing services"
            },
            {
                "id": "web_frontend",
                "name": "Web Frontend",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Customer-facing web application"
            },
            {
                "id": "catalog_service_app",
                "name": "Catalog Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Product catalog management"
            },
            {
                "id": "order_service_app",
                "name": "Order Service",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Order processing application"
            },
            {
                "id": "payment_gateway",
                "name": "Payment Gateway",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Payment processing integration"
            },
            {
                "id": "product_database",
                "name": "Product Database",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Product information storage"
            }
        ],
        relationships=[
            {
                "id": "customer_catalog",
                "from_element": "customer_ecom",
                "to_element": "product_catalog_service",
                "relationship_type": "Serving"
            },
            {
                "id": "customer_order",
                "from_element": "customer_ecom",
                "to_element": "order_service_ecom",
                "relationship_type": "Serving"
            },
            {
                "id": "frontend_catalog",
                "from_element": "web_frontend",
                "to_element": "product_catalog_service",
                "relationship_type": "Realization"
            },
            {
                "id": "catalog_app_service",
                "from_element": "catalog_service_app",
                "to_element": "product_catalog_service",
                "relationship_type": "Realization"
            },
            {
                "id": "order_app_service",
                "from_element": "order_service_app",
                "to_element": "order_service_ecom",
                "relationship_type": "Realization"
            },
            {
                "id": "payment_app_service",
                "from_element": "payment_gateway",
                "to_element": "payment_service_ecom",
                "relationship_type": "Realization"
            },
            {
                "id": "catalog_data",
                "from_element": "catalog_service_app",
                "to_element": "product_database",
                "relationship_type": "Access"
            }
        ]
    ),
    
    "healthcare_his": IndustryTemplate(
        name="Hospital Information System",
        description="Hospital information system architecture for healthcare",
        industry="healthcare",
        elements=[
            {
                "id": "patient",
                "name": "Patient",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Hospital patient"
            },
            {
                "id": "doctor",
                "name": "Doctor",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Medical practitioner"
            },
            {
                "id": "nurse",
                "name": "Nurse",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Nursing staff"
            },
            {
                "id": "patient_care",
                "name": "Patient Care",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Patient care services"
            },
            {
                "id": "medical_records",
                "name": "Medical Records",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Medical record management"
            },
            {
                "id": "his_application",
                "name": "HIS Application",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Hospital information system"
            },
            {
                "id": "emr_system",
                "name": "EMR System",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Electronic medical records"
            },
            {
                "id": "patient_data",
                "name": "Patient Database",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Patient information storage"
            }
        ],
        relationships=[
            {
                "id": "doctor_care",
                "from_element": "doctor",
                "to_element": "patient_care",
                "relationship_type": "Assignment"
            },
            {
                "id": "nurse_care",
                "from_element": "nurse",
                "to_element": "patient_care",
                "relationship_type": "Assignment"
            },
            {
                "id": "doctor_records",
                "from_element": "doctor",
                "to_element": "medical_records",
                "relationship_type": "Serving"
            },
            {
                "id": "his_care",
                "from_element": "his_application",
                "to_element": "patient_care",
                "relationship_type": "Realization"
            },
            {
                "id": "emr_records",
                "from_element": "emr_system",
                "to_element": "medical_records",
                "relationship_type": "Realization"
            },
            {
                "id": "emr_data",
                "from_element": "emr_system",
                "to_element": "patient_data",
                "relationship_type": "Access"
            }
        ]
    ),
    
    "manufacturing_mes": IndustryTemplate(
        name="Manufacturing Execution System",
        description="MES architecture for manufacturing operations",
        industry="manufacturing",
        elements=[
            {
                "id": "operator",
                "name": "Production Operator",
                "element_type": "Business_Actor",
                "layer": "Business",
                "description": "Manufacturing operator"
            },
            {
                "id": "production_planning",
                "name": "Production Planning",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Production planning and scheduling"
            },
            {
                "id": "quality_control",
                "name": "Quality Control",
                "element_type": "Business_Service",
                "layer": "Business",
                "description": "Quality assurance processes"
            },
            {
                "id": "mes_system",
                "name": "MES System",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Manufacturing execution system"
            },
            {
                "id": "scada_system",
                "name": "SCADA System",
                "element_type": "Application_Component",
                "layer": "Application",
                "description": "Supervisory control and data acquisition"
            },
            {
                "id": "plc_controller",
                "name": "PLC Controller",
                "element_type": "Device",
                "layer": "Technology",
                "description": "Programmable logic controller"
            },
            {
                "id": "production_data",
                "name": "Production Database",
                "element_type": "Data_Object",
                "layer": "Application",
                "description": "Manufacturing data storage"
            }
        ],
        relationships=[
            {
                "id": "operator_planning",
                "from_element": "operator",
                "to_element": "production_planning",
                "relationship_type": "Serving"
            },
            {
                "id": "mes_planning",
                "from_element": "mes_system",
                "to_element": "production_planning",
                "relationship_type": "Realization"
            },
            {
                "id": "mes_quality",
                "from_element": "mes_system",
                "to_element": "quality_control",
                "relationship_type": "Realization"
            },
            {
                "id": "scada_mes",
                "from_element": "scada_system",
                "to_element": "mes_system",
                "relationship_type": "Serving"
            },
            {
                "id": "plc_scada",
                "from_element": "plc_controller",
                "to_element": "scada_system",
                "relationship_type": "Serving"
            },
            {
                "id": "mes_data",
                "from_element": "mes_system",
                "to_element": "production_data",
                "relationship_type": "Access"
            }
        ]
    )
}


def get_industry_template(template_name: str) -> Optional[IndustryTemplate]:
    """Get industry template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        IndustryTemplate if found, None otherwise
    """
    return INDUSTRY_TEMPLATES.get(template_name)


def list_available_industry_templates() -> List[str]:
    """Get list of available industry template names.
    
    Returns:
        List of template names
    """
    return list(INDUSTRY_TEMPLATES.keys())


def get_templates_by_industry(industry: str) -> List[str]:
    """Get templates by industry.
    
    Args:
        industry: Industry to filter by
        
    Returns:
        List of template names for the industry
    """
    return [
        name for name, template in INDUSTRY_TEMPLATES.items()
        if template.industry == industry
    ]