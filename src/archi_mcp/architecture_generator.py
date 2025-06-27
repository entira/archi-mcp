"""Full architecture generator following ArchiMate methodology."""

from typing import Dict, List, Any, Optional
from .archimate.elements import (
    BusinessElement,
    ApplicationElement,
    TechnologyElement,
    MotivationElement,
    StrategyElement,
    ImplementationElement,
)
from .archimate.relationships import create_relationship
from .archimate.generator import ArchiMateGenerator, DiagramLayout


class FullArchitectureGenerator:
    """Generator for complete layered enterprise architectures following ArchiMate methodology."""
    
    def __init__(self):
        """Initialize the full architecture generator."""
        self.generators = {}  # Dict of view_name -> ArchiMateGenerator
        self.element_registry = {}  # Global registry of all elements across views
        
    def generate_architecture(
        self,
        system_description: str,
        business_domain: str = "general",
        architecture_scope: str = "system",
        include_views: List[str] = None,
        implementation_phases: int = 3
    ) -> Dict[str, str]:
        """Generate complete architecture with multiple coordinated views.
        
        Args:
            system_description: Description of the target system
            business_domain: Business domain context
            architecture_scope: Scope of architecture 
            include_views: List of views to include
            implementation_phases: Number of implementation phases
            
        Returns:
            Dictionary mapping view names to PlantUML code
        """
        if include_views is None:
            include_views = ["motivation", "layered_view", "application_structure", "implementation_roadmap"]
        
        results = {}
        
        # Generate each requested view
        for view_name in include_views:
            if view_name == "motivation":
                results[view_name] = self._generate_motivation_view(system_description, business_domain)
            elif view_name == "business_model_canvas":
                results[view_name] = self._generate_business_model_canvas(system_description, business_domain)
            elif view_name == "value_stream":
                results[view_name] = self._generate_value_stream_view(system_description, business_domain)
            elif view_name == "strategy_capability":
                results[view_name] = self._generate_strategy_capability_view(system_description, business_domain)
            elif view_name == "layered_view":
                results[view_name] = self._generate_layered_view(system_description, business_domain, architecture_scope)
            elif view_name == "interaction_view":
                results[view_name] = self._generate_interaction_view(system_description, business_domain)
            elif view_name == "application_structure":
                results[view_name] = self._generate_application_structure_view(system_description, business_domain)
            elif view_name == "technology_structure":
                results[view_name] = self._generate_technology_structure_view(system_description, business_domain)
            elif view_name == "implementation_roadmap":
                results[view_name] = self._generate_implementation_roadmap(system_description, implementation_phases)
        
        return results
    
    def _generate_motivation_view(self, system_description: str, business_domain: str) -> str:
        """Generate motivation view showing goals, stakeholders, drivers and requirements."""
        generator = ArchiMateGenerator()
        
        # Determine domain-specific stakeholders and drivers
        domain_context = self._get_domain_context(business_domain)
        
        # Create stakeholders
        business_stakeholder = MotivationElement.create_stakeholder(
            id="business_stakeholder",
            name=domain_context["primary_stakeholder"],
            description=f"Primary business stakeholder for {system_description}"
        )
        
        customer_stakeholder = MotivationElement.create_stakeholder(
            id="customer_stakeholder", 
            name="Customer",
            description="End user of the system"
        )
        
        it_stakeholder = MotivationElement.create_stakeholder(
            id="it_stakeholder",
            name="IT Department",
            description="Technical implementation team"
        )
        
        # Create drivers
        business_driver = MotivationElement.create_driver(
            id="business_driver",
            name=domain_context["primary_driver"],
            description=f"Key business driver for {system_description}"
        )
        
        efficiency_driver = MotivationElement.create_driver(
            id="efficiency_driver",
            name="Operational Efficiency",
            description="Need to improve operational efficiency and reduce costs"
        )
        
        # Create goals
        primary_goal = MotivationElement.create_goal(
            id="primary_goal",
            name=f"Deliver {system_description}",
            description=f"Successfully implement and operate {system_description}"
        )
        
        user_satisfaction_goal = MotivationElement.create_goal(
            id="user_satisfaction_goal",
            name="Improve User Satisfaction",
            description="Enhance user experience and satisfaction"
        )
        
        # Create requirements
        functional_requirement = MotivationElement.create_requirement(
            id="functional_requirement",
            name="Functional Requirements",
            description=f"Core functional requirements for {system_description}"
        )
        
        performance_requirement = MotivationElement.create_requirement(
            id="performance_requirement",
            name="Performance Requirements", 
            description="System performance and scalability requirements"
        )
        
        security_requirement = MotivationElement.create_requirement(
            id="security_requirement",
            name="Security Requirements",
            description="Data protection and security compliance requirements"
        )
        
        # Create principle
        architecture_principle = MotivationElement.create_principle(
            id="architecture_principle",
            name="Architecture Principles",
            description="Key architectural principles and design guidelines"
        )
        
        # Add elements
        elements = [
            business_stakeholder, customer_stakeholder, it_stakeholder,
            business_driver, efficiency_driver,
            primary_goal, user_satisfaction_goal,
            functional_requirement, performance_requirement, security_requirement,
            architecture_principle
        ]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        # Add relationships
        relationships = [
            create_relationship("business_has_driver", "business_stakeholder", "business_driver", "Association"),
            create_relationship("customer_influences_satisfaction", "customer_stakeholder", "user_satisfaction_goal", "Influence"),
            create_relationship("driver_motivates_goal", "business_driver", "primary_goal", "Influence"),
            create_relationship("efficiency_motivates_goal", "efficiency_driver", "primary_goal", "Influence"),
            create_relationship("goal_realizes_requirement", "primary_goal", "functional_requirement", "Realization"),
            create_relationship("satisfaction_realizes_performance", "user_satisfaction_goal", "performance_requirement", "Realization"),
            create_relationship("principle_influences_security", "architecture_principle", "security_requirement", "Influence"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        # Set layout
        layout = DiagramLayout(direction="vertical", group_by_layer=True, show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Motivation View",
            description=f"Stakeholders, drivers, goals and requirements for {system_description}"
        )
    
    def _generate_layered_view(self, system_description: str, business_domain: str, scope: str) -> str:
        """Generate layered view showing business, application and technology architecture."""
        generator = ArchiMateGenerator()
        
        domain_context = self._get_domain_context(business_domain)
        
        # Business Layer
        business_actor = BusinessElement.create_business_actor(
            id="primary_user",
            name=domain_context["primary_user"],
            description=f"Primary user of {system_description}"
        )
        
        business_service = BusinessElement.create_business_service(
            id="core_business_service",
            name=f"{domain_context['core_service']} Service",
            description=f"Core business service provided by {system_description}"
        )
        
        business_process = BusinessElement.create_business_process(
            id="core_business_process",
            name=f"{domain_context['core_process']} Process",
            description=f"Key business process for {system_description}"
        )
        
        business_object = BusinessElement.create_business_object(
            id="business_data",
            name=f"{domain_context['core_data']} Data",
            description="Core business data and information"
        )
        
        # Application Layer
        user_interface = ApplicationElement.create_application_component(
            id="user_interface",
            name="User Interface",
            description="User-facing application interface"
        )
        
        api_gateway = ApplicationElement.create_application_component(
            id="api_gateway",
            name="API Gateway",
            description="API management and routing"
        )
        
        core_application = ApplicationElement.create_application_component(
            id="core_application",
            name="Core Application",
            description=f"Main application logic for {system_description}"
        )
        
        data_service = ApplicationElement.create_application_component(
            id="data_service",
            name="Data Service",
            description="Data access and management services"
        )
        
        application_data = ApplicationElement.create_data_object(
            id="application_database",
            name="Application Database",
            description="Primary application data storage"
        )
        
        # Technology Layer
        web_server = TechnologyElement.create_node(
            id="web_server",
            name="Web Server",
            description="Web application hosting server"
        )
        
        app_server = TechnologyElement.create_node(
            id="app_server",
            name="Application Server",
            description="Application logic hosting server"
        )
        
        database_server = TechnologyElement.create_node(
            id="database_server",
            name="Database Server",
            description="Database hosting infrastructure"
        )
        
        load_balancer = TechnologyElement.create_device(
            id="load_balancer",
            name="Load Balancer",
            description="Traffic distribution and load balancing"
        )
        
        # Add elements
        elements = [
            # Business
            business_actor, business_service, business_process, business_object,
            # Application  
            user_interface, api_gateway, core_application, data_service, application_data,
            # Technology
            web_server, app_server, database_server, load_balancer
        ]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        # Add relationships
        relationships = [
            # Business relationships
            create_relationship("user_uses_service", "primary_user", "core_business_service", "Serving"),
            create_relationship("service_realizes_process", "core_business_service", "core_business_process", "Realization"),
            create_relationship("process_uses_data", "core_business_process", "business_data", "Association"),
            
            # Application relationships
            create_relationship("ui_realizes_service", "user_interface", "core_business_service", "Realization"),
            create_relationship("ui_flows_gateway", "user_interface", "api_gateway", "Flow"),
            create_relationship("gateway_routes_core", "api_gateway", "core_application", "Flow"),
            create_relationship("core_uses_data_service", "core_application", "data_service", "Flow"),
            create_relationship("data_service_uses_db", "data_service", "application_database", "Association"),
            create_relationship("app_data_realizes_business", "application_database", "business_data", "Realization"),
            
            # Technology relationships
            create_relationship("web_hosts_ui", "web_server", "user_interface", "Assignment"),
            create_relationship("app_hosts_gateway", "app_server", "api_gateway", "Assignment"),
            create_relationship("app_hosts_core", "app_server", "core_application", "Assignment"),
            create_relationship("app_hosts_data_service", "app_server", "data_service", "Assignment"),
            create_relationship("db_hosts_data", "database_server", "application_database", "Assignment"),
            create_relationship("lb_distributes_web", "load_balancer", "web_server", "Serving"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        # Set layout
        layout = DiagramLayout(direction="vertical", group_by_layer=True, show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Layered Architecture View",
            description=f"Business, application and technology layers for {system_description}"
        )
    
    def _generate_application_structure_view(self, system_description: str, business_domain: str) -> str:
        """Generate application structure view showing detailed application components."""
        generator = ArchiMateGenerator()
        
        # Frontend components
        web_frontend = ApplicationElement.create_application_component(
            id="web_frontend",
            name="Web Frontend",
            description="Web-based user interface"
        )
        
        mobile_app = ApplicationElement.create_application_component(
            id="mobile_app",
            name="Mobile Application",
            description="Mobile native application"
        )
        
        # API and integration components
        rest_api = ApplicationElement.create_application_interface(
            id="rest_api",
            name="REST API",
            description="RESTful web services interface"
        )
        
        graphql_api = ApplicationElement.create_application_interface(
            id="graphql_api",
            name="GraphQL API",
            description="GraphQL query interface"
        )
        
        # Core business components
        user_service = ApplicationElement.create_application_component(
            id="user_service",
            name="User Management Service",
            description="User authentication and profile management"
        )
        
        business_logic_service = ApplicationElement.create_application_component(
            id="business_logic_service",
            name="Business Logic Service",
            description="Core business rules and processing"
        )
        
        notification_service = ApplicationElement.create_application_component(
            id="notification_service",
            name="Notification Service",
            description="Email, SMS, and push notifications"
        )
        
        # Data components
        user_data = ApplicationElement.create_data_object(
            id="user_data",
            name="User Data",
            description="User profiles and authentication data"
        )
        
        business_data = ApplicationElement.create_data_object(
            id="business_data_app",
            name="Business Data",
            description="Core business information and transactions"
        )
        
        audit_log = ApplicationElement.create_data_object(
            id="audit_log",
            name="Audit Log",
            description="System audit and activity logs"
        )
        
        # Add elements
        elements = [
            web_frontend, mobile_app,
            rest_api, graphql_api,
            user_service, business_logic_service, notification_service,
            user_data, business_data, audit_log
        ]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        # Add relationships
        relationships = [
            # Frontend to API
            create_relationship("web_uses_rest", "web_frontend", "rest_api", "Serving"),
            create_relationship("mobile_uses_graphql", "mobile_app", "graphql_api", "Serving"),
            
            # API to services
            create_relationship("rest_routes_user", "rest_api", "user_service", "Serving"),
            create_relationship("rest_routes_business", "rest_api", "business_logic_service", "Serving"),
            create_relationship("graphql_routes_user", "graphql_api", "user_service", "Serving"),
            create_relationship("graphql_routes_business", "graphql_api", "business_logic_service", "Serving"),
            
            # Service interactions
            create_relationship("business_uses_user", "business_logic_service", "user_service", "Flow"),
            create_relationship("business_uses_notification", "business_logic_service", "notification_service", "Triggering"),
            
            # Data access
            create_relationship("user_service_data", "user_service", "user_data", "Association"),
            create_relationship("business_service_data", "business_logic_service", "business_data_app", "Association"),
            create_relationship("services_log_audit", "user_service", "audit_log", "Association"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        # Set layout
        layout = DiagramLayout(direction="horizontal", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Application Structure View",
            description=f"Detailed application components and interfaces for {system_description}"
        )
    
    def _generate_implementation_roadmap(self, system_description: str, phases: int) -> str:
        """Generate implementation roadmap showing phased delivery."""
        generator = ArchiMateGenerator()
        
        # Create phases
        phase_elements = []
        deliverable_elements = []
        
        phase_names = ["MVP", "Integration", "Enhancement", "Optimization", "Scaling", "Innovation"]
        
        for i in range(min(phases, len(phase_names))):
            phase_name = phase_names[i]
            
            # Create work package for phase
            work_package = ImplementationElement.create_work_package(
                id=f"phase_{i+1}",
                name=f"Phase {i+1}: {phase_name}",
                description=f"{phase_name} phase of {system_description} implementation"
            )
            phase_elements.append(work_package)
            
            # Create deliverables for phase
            if i == 0:  # MVP
                deliverables = ["Core Functionality", "Basic UI", "Essential APIs"]
            elif i == 1:  # Integration
                deliverables = ["External Integrations", "Data Migration", "Testing Suite"]
            elif i == 2:  # Enhancement
                deliverables = ["Advanced Features", "Performance Optimization", "User Experience"]
            elif i == 3:  # Optimization
                deliverables = ["System Tuning", "Monitoring", "Documentation"]
            elif i == 4:  # Scaling
                deliverables = ["Load Balancing", "High Availability", "Disaster Recovery"]
            else:  # Innovation
                deliverables = ["AI/ML Features", "Analytics", "Future Capabilities"]
            
            for j, deliv_name in enumerate(deliverables):
                deliverable = ImplementationElement.create_deliverable(
                    id=f"deliverable_{i+1}_{j+1}",
                    name=f"{deliv_name}",
                    description=f"{deliv_name} deliverable for {phase_name} phase"
                )
                deliverable_elements.append(deliverable)
                
                # Add relationship from phase to deliverable
                phase_deliv_rel = create_relationship(
                    f"phase_{i+1}_delivers_{j+1}",
                    work_package.id,
                    deliverable.id,
                    "Flow"
                )
        
        # Add milestone events
        milestone_elements = []
        if phases >= 2:
            mvp_milestone = ImplementationElement.create_implementation_event(
                id="mvp_milestone",
                name="MVP Release",
                description="Minimum viable product release milestone"
            )
            milestone_elements.append(mvp_milestone)
        
        if phases >= 3:
            integration_milestone = ImplementationElement.create_implementation_event(
                id="integration_milestone", 
                name="Integration Complete",
                description="System integration completion milestone"
            )
            milestone_elements.append(integration_milestone)
        
        if phases >= 4:
            production_milestone = ImplementationElement.create_implementation_event(
                id="production_milestone",
                name="Production Ready",
                description="Production deployment milestone"
            )
            milestone_elements.append(production_milestone)
        
        # Add all elements
        all_elements = phase_elements + deliverable_elements + milestone_elements
        for element in all_elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        # Add phase sequence relationships
        relationships = []
        for i in range(len(phase_elements) - 1):
            seq_rel = create_relationship(
                f"phase_sequence_{i+1}",
                phase_elements[i].id,
                phase_elements[i+1].id,
                "Flow"
            )
            relationships.append(seq_rel)
        
        # Add milestone relationships
        if milestone_elements:
            for i, milestone in enumerate(milestone_elements):
                if i < len(phase_elements):
                    milestone_rel = create_relationship(
                        f"phase_milestone_{i+1}",
                        phase_elements[i].id,
                        milestone.id,
                        "Triggering"
                    )
                    relationships.append(milestone_rel)
        
        # Add deliverable relationships
        deliv_idx = 0
        for i, phase in enumerate(phase_elements):
            deliverables_per_phase = 3  # 3 deliverables per phase
            for j in range(deliverables_per_phase):
                if deliv_idx < len(deliverable_elements):
                    deliv_rel = create_relationship(
                        f"phase_deliverable_{i+1}_{j+1}",
                        phase.id,
                        deliverable_elements[deliv_idx].id,
                        "Flow"
                    )
                    relationships.append(deliv_rel)
                    deliv_idx += 1
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        # Set layout
        layout = DiagramLayout(direction="horizontal", show_legend=True, spacing="wide")
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Implementation Roadmap",
            description=f"Phased implementation plan for {system_description} with {phases} phases"
        )
    
    def _generate_business_model_canvas(self, system_description: str, business_domain: str) -> str:
        """Generate business model canvas view."""
        generator = ArchiMateGenerator()
        
        domain_context = self._get_domain_context(business_domain)
        
        # Key Partners
        key_partner = BusinessElement.create_business_actor(
            id="key_partner",
            name=domain_context["key_partner"],
            description="Strategic business partner"
        )
        
        # Value Propositions
        value_proposition = BusinessElement.create_business_service(
            id="value_proposition",
            name=f"{domain_context['value_prop']} Service",
            description=f"Core value proposition of {system_description}"
        )
        
        # Customer Segments
        customer_segment = BusinessElement.create_business_actor(
            id="customer_segment",
            name=domain_context["customer_segment"],
            description="Primary customer segment"
        )
        
        # Channels
        digital_channel = BusinessElement.create_business_interface(
            id="digital_channel",
            name="Digital Channel",
            description="Online digital channels"
        )
        
        # Revenue Streams
        revenue_stream = BusinessElement.create_business_object(
            id="revenue_stream",
            name=domain_context["revenue_stream"],
            description="Primary revenue generation method"
        )
        
        # Cost Structure
        operational_cost = BusinessElement.create_business_object(
            id="operational_cost",
            name="Operational Costs",
            description="Ongoing operational expenses"
        )
        
        elements = [key_partner, value_proposition, customer_segment, digital_channel, revenue_stream, operational_cost]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        relationships = [
            create_relationship("partner_supports_value", "key_partner", "value_proposition", "Serving"),
            create_relationship("value_reaches_customer", "value_proposition", "customer_segment", "Serving"),
            create_relationship("channel_reaches_customer", "digital_channel", "customer_segment", "Serving"),
            create_relationship("customer_generates_revenue", "customer_segment", "revenue_stream", "Flow"),
            create_relationship("value_incurs_cost", "value_proposition", "operational_cost", "Association"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        layout = DiagramLayout(direction="horizontal", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Business Model Canvas",
            description=f"Business model overview for {system_description}"
        )
    
    def _generate_value_stream_view(self, system_description: str, business_domain: str) -> str:
        """Generate value stream view."""
        generator = ArchiMateGenerator()
        
        # Create value stream
        primary_value_stream = StrategyElement.create_value_stream(
            id="primary_value_stream",
            name="Primary Value Stream",
            description=f"Main value creation process for {system_description}"
        )
        
        # Create capabilities
        capability_1 = StrategyElement.create_capability(
            id="capability_1",
            name="Customer Acquisition",
            description="Ability to attract and onboard customers"
        )
        
        capability_2 = StrategyElement.create_capability(
            id="capability_2", 
            name="Service Delivery",
            description="Core service delivery capability"
        )
        
        capability_3 = StrategyElement.create_capability(
            id="capability_3",
            name="Customer Support",
            description="Customer service and support capability"
        )
        
        elements = [primary_value_stream, capability_1, capability_2, capability_3]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        relationships = [
            create_relationship("vs_uses_acquisition", "primary_value_stream", "capability_1", "Aggregation"),
            create_relationship("vs_uses_delivery", "primary_value_stream", "capability_2", "Aggregation"),
            create_relationship("vs_uses_support", "primary_value_stream", "capability_3", "Aggregation"),
            create_relationship("acquisition_to_delivery", "capability_1", "capability_2", "Flow"),
            create_relationship("delivery_to_support", "capability_2", "capability_3", "Flow"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        layout = DiagramLayout(direction="horizontal", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Value Stream View",
            description=f"Value creation flow for {system_description}"
        )
    
    def _generate_strategy_capability_view(self, system_description: str, business_domain: str) -> str:
        """Generate strategy and capability view."""
        generator = ArchiMateGenerator()
        
        # Strategic goal
        strategic_goal = MotivationElement.create_goal(
            id="strategic_goal",
            name=f"Strategic Goal for {system_description}",
            description="Primary strategic objective"
        )
        
        # Capabilities
        digital_capability = StrategyElement.create_capability(
            id="digital_capability",
            name="Digital Transformation",
            description="Digital technology adoption capability"
        )
        
        innovation_capability = StrategyElement.create_capability(
            id="innovation_capability",
            name="Innovation",
            description="Continuous innovation and improvement"
        )
        
        # Resources
        human_resource = StrategyElement.create_resource(
            id="human_resource",
            name="Skilled Workforce",
            description="Technical and business expertise"
        )
        
        technology_resource = StrategyElement.create_resource(
            id="technology_resource",
            name="Technology Platform",
            description="Technology infrastructure and tools"
        )
        
        elements = [strategic_goal, digital_capability, innovation_capability, human_resource, technology_resource]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        relationships = [
            create_relationship("goal_realizes_digital", "strategic_goal", "digital_capability", "Realization"),
            create_relationship("goal_realizes_innovation", "strategic_goal", "innovation_capability", "Realization"),
            create_relationship("human_enables_digital", "human_resource", "digital_capability", "Assignment"),
            create_relationship("tech_enables_digital", "technology_resource", "digital_capability", "Assignment"),
            create_relationship("human_enables_innovation", "human_resource", "innovation_capability", "Assignment"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        layout = DiagramLayout(direction="vertical", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Strategy & Capability View",
            description=f"Strategic capabilities for {system_description}"
        )
    
    def _generate_interaction_view(self, system_description: str, business_domain: str) -> str:
        """Generate interaction view showing process and application interactions."""
        generator = ArchiMateGenerator()
        
        # Business actors and processes
        user_actor = BusinessElement.create_business_actor(
            id="system_user",
            name="System User",
            description="End user interacting with the system"
        )
        
        admin_actor = BusinessElement.create_business_actor(
            id="system_admin",
            name="System Administrator", 
            description="Administrative user managing the system"
        )
        
        user_process = BusinessElement.create_business_process(
            id="user_interaction_process",
            name="User Interaction Process",
            description="Primary user interaction workflow"
        )
        
        admin_process = BusinessElement.create_business_process(
            id="admin_process",
            name="Administration Process",
            description="System administration workflow"
        )
        
        # Application components
        frontend_app = ApplicationElement.create_application_component(
            id="frontend_interaction",
            name="Frontend Application",
            description="User interface application"
        )
        
        backend_service = ApplicationElement.create_application_component(
            id="backend_interaction",
            name="Backend Service",
            description="Business logic processing service"
        )
        
        admin_panel = ApplicationElement.create_application_component(
            id="admin_panel",
            name="Admin Panel",
            description="Administrative interface"
        )
        
        elements = [user_actor, admin_actor, user_process, admin_process, frontend_app, backend_service, admin_panel]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        relationships = [
            create_relationship("user_performs_process", "system_user", "user_interaction_process", "Assignment"),
            create_relationship("admin_performs_process", "system_admin", "admin_process", "Assignment"),
            create_relationship("user_process_uses_frontend", "user_interaction_process", "frontend_interaction", "Triggering"),
            create_relationship("frontend_calls_backend", "frontend_interaction", "backend_interaction", "Flow"),
            create_relationship("admin_uses_panel", "admin_process", "admin_panel", "Triggering"),
            create_relationship("admin_panel_calls_backend", "admin_panel", "backend_interaction", "Flow"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        layout = DiagramLayout(direction="horizontal", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Interaction View",
            description=f"Actor and process interactions for {system_description}"
        )
    
    def _generate_technology_structure_view(self, system_description: str, business_domain: str) -> str:
        """Generate technology structure view showing infrastructure details."""
        generator = ArchiMateGenerator()
        
        # Infrastructure nodes
        web_cluster = TechnologyElement.create_node(
            id="web_cluster",
            name="Web Server Cluster",
            description="Load-balanced web server cluster"
        )
        
        app_cluster = TechnologyElement.create_node(
            id="app_cluster",
            name="Application Server Cluster",
            description="Scalable application server cluster"
        )
        
        database_cluster = TechnologyElement.create_node(
            id="database_cluster",
            name="Database Cluster",
            description="High-availability database cluster"
        )
        
        # Networking
        cdn = TechnologyElement.create_communication_network(
            id="cdn_network",
            name="Content Delivery Network",
            description="Global content distribution network"
        )
        
        internal_network = TechnologyElement.create_communication_network(
            id="internal_network",
            name="Internal Network",
            description="Private internal network"
        )
        
        # System software
        container_platform = TechnologyElement.create_system_software(
            id="container_platform",
            name="Container Platform",
            description="Container orchestration platform"
        )
        
        monitoring_system = TechnologyElement.create_system_software(
            id="monitoring_system",
            name="Monitoring System",
            description="System monitoring and alerting"
        )
        
        elements = [web_cluster, app_cluster, database_cluster, cdn, internal_network, container_platform, monitoring_system]
        
        for element in elements:
            generator.add_element(element)
            self.element_registry[element.id] = element
        
        relationships = [
            create_relationship("cdn_distributes_web", "cdn_network", "web_cluster", "Serving"),
            create_relationship("web_connects_app", "web_cluster", "app_cluster", "Flow"),
            create_relationship("app_connects_db", "app_cluster", "database_cluster", "Flow"),
            create_relationship("internal_connects_app", "internal_network", "app_cluster", "Association"),
            create_relationship("internal_connects_db", "internal_network", "database_cluster", "Association"),
            create_relationship("container_hosts_app", "container_platform", "app_cluster", "Assignment"),
            create_relationship("monitoring_watches_web", "monitoring_system", "web_cluster", "Serving"),
            create_relationship("monitoring_watches_app", "monitoring_system", "app_cluster", "Serving"),
        ]
        
        for relationship in relationships:
            generator.add_relationship(relationship)
        
        layout = DiagramLayout(direction="horizontal", show_legend=True)
        generator.set_layout(layout)
        
        return generator.generate_plantuml(
            title="Technology Structure View",
            description=f"Detailed technology infrastructure for {system_description}"
        )
    
    def _get_domain_context(self, business_domain: str) -> Dict[str, str]:
        """Get domain-specific context for element naming and relationships."""
        domain_contexts = {
            "banking": {
                "primary_stakeholder": "Bank Management",
                "primary_user": "Bank Customer",
                "primary_driver": "Regulatory Compliance",
                "core_service": "Banking",
                "core_process": "Account Management",
                "core_data": "Financial",
                "key_partner": "Payment Processor",
                "value_prop": "Secure Financial",
                "customer_segment": "Retail Banking Customers",
                "revenue_stream": "Transaction Fees"
            },
            "healthcare": {
                "primary_stakeholder": "Healthcare Administration",
                "primary_user": "Healthcare Provider",
                "primary_driver": "Patient Care Quality",
                "core_service": "Patient Care",
                "core_process": "Patient Treatment",
                "core_data": "Medical Records",
                "key_partner": "Medical Equipment Supplier",
                "value_prop": "Quality Healthcare",
                "customer_segment": "Patients and Providers",
                "revenue_stream": "Service Fees"
            },
            "e-commerce": {
                "primary_stakeholder": "Business Owner",
                "primary_user": "Online Shopper",
                "primary_driver": "Market Competition",
                "core_service": "Online Shopping",
                "core_process": "Order Fulfillment",
                "core_data": "Product Catalog",
                "key_partner": "Logistics Provider",
                "value_prop": "Convenient Shopping",
                "customer_segment": "Online Consumers",
                "revenue_stream": "Product Sales"
            },
            "manufacturing": {
                "primary_stakeholder": "Plant Manager",
                "primary_user": "Production Operator",
                "primary_driver": "Operational Efficiency",
                "core_service": "Manufacturing",
                "core_process": "Production",
                "core_data": "Production",
                "key_partner": "Supplier",
                "value_prop": "Quality Manufacturing",
                "customer_segment": "Industrial Customers",
                "revenue_stream": "Product Sales"
            },
            "general": {
                "primary_stakeholder": "Business Stakeholder",
                "primary_user": "End User",
                "primary_driver": "Business Growth",
                "core_service": "Core Business",
                "core_process": "Business",
                "core_data": "Business",
                "key_partner": "Strategic Partner",
                "value_prop": "Business Value",
                "customer_segment": "Target Customers",
                "revenue_stream": "Revenue"
            }
        }
        
        return domain_contexts.get(business_domain, domain_contexts["general"])