# ArchiMate 3.2 Element Reference

Complete reference of all 55+ ArchiMate element types across 7 layers.

## Quick Reference Table

| Layer | Element Type | Usage | Example |
|-------|-------------|--------|---------|
| **BUSINESS** | Business_Actor | Person, organization, or system that performs behavior | Customer, Department |
| | Business_Role | Responsibility assigned to actor | Account Manager, Administrator |
| | Business_Collaboration | Multiple actors working together | Project Team, Partnership |
| | Business_Interface | Point of access for business services | Customer Service Desk |
| | Business_Process | Sequence of business behaviors | Order Processing, Hiring |
| | Business_Function | Collection of business behavior | Sales, Marketing |
| | Business_Interaction | Behavior performed by collaboration | Contract Negotiation |
| | Business_Event | Something that happens | Order Received, Deadline |
| | Business_Service | Explicitly defined behavior exposed to environment | Customer Support, Delivery |
| | Business_Object | Passive element with business relevance | Invoice, Contract, Policy |
| | Contract | Formal agreement between parties | Service Agreement, Purchase Order |
| | Representation | Perceptible form of information | Report, Dashboard |
| | Product | Coherent collection of services and/or assets | Banking Package, Insurance Policy |
| **APPLICATION** | Application_Component | Modular, deployable software system | CRM System, Payment Gateway |
| | Application_Collaboration | Multiple components working together | Integrated Suite |
| | Application_Interface | Point of access for application services | REST API, Web Interface |
| | Application_Function | Automated behavior | Calculate, Validate |
| | Application_Interaction | Behavior of collaboration | Data Synchronization |
| | Application_Process | Sequence of application behaviors | Batch Processing |
| | Application_Event | Application state change | Transaction Complete, Error Occurred |
| | Application_Service | Explicitly defined application behavior | Authentication Service, Search |
| | Data_Object | Data structured for automated processing | Customer Record, Transaction Log |
| **TECHNOLOGY** | Node | Computational or physical resource | Server, Container, VM |
| | Device | Physical IT resource | Laptop, Router, Smartphone |
| | System_Software | Software environment | Operating System, Database Engine |
| | Technology_Collaboration | Multiple tech components working together | Cluster, Grid |
| | Technology_Interface | Point of access for technology services | Network Interface, API Gateway |
| | Path | Communication channel | Network Connection, Bus |
| | Communication_Network | Physical communication medium | LAN, WAN, Internet |
| | Technology_Function | Collection of technology behavior | Backup, Monitoring |
| | Technology_Process | Sequence of technology behaviors | Deployment Pipeline |
| | Technology_Interaction | Behavior of technology collaboration | Load Balancing |
| | Technology_Event | Technology state change | Server Start, Failure |
| | Technology_Service | Explicitly defined technology capability | Storage Service, Compute Service |
| | Artifact | Physical piece of data | File, Database, Package |
| **PHYSICAL** | Equipment | Physical machine, tool, or instrument | Generator, Conveyor Belt |
| | Facility | Physical location or environment | Data Center, Office Building |
| | Distribution_Network | Physical network for materials | Pipeline, Railway |
| | Material | Tangible physical element | Raw Materials, Products |
| **STRATEGY** | Resource | Asset owned or controlled | Brand, Patent, Human Resources |
| | Capability | Ability to employ resources | Manufacturing Capability, Data Analytics |
| | Value_Stream | Sequence of activities creating value | Order-to-Cash, Hire-to-Retire |
| | Course_of_Action | Strategic approach or plan | Digital Transformation, Market Expansion |
| **MOTIVATION** | Stakeholder | Role of individual, team, or organization | CEO, Customer, Regulator |
| | Driver | External or internal force | Market Pressure, Regulation |
| | Assessment | Result of analysis | SWOT Analysis, Risk Assessment |
| | Goal | High-level statement of intent | Increase Revenue, Reduce Costs |
| | Outcome | End result | Customer Satisfaction, Market Share |
| | Principle | Normative property of design | Security First, Privacy by Design |
| | Requirement | Statement of need | Must support 10K users, 99.9% uptime |
| | Constraint | Restriction on realization | Budget Limit, Timeline |
| | Meaning | Knowledge or expertise | Business Knowledge, Domain Expertise |
| | Value | Relative worth or importance | Cost Savings, Customer Loyalty |
| **IMPLEMENTATION** | Work_Package | Series of actions for change | Migration Project, Development Sprint |
| | Deliverable | Precisely-defined result | System Component, Documentation |
| | Implementation_Event | State change in implementation | Milestone, Go-Live |
| | Plateau | Relatively stable state | Release Version, Phase Completion |

## Usage Guidelines

### Element Naming Format

**In JSON:**
```json
{
  "element_type": "Business_Actor"  // Use underscores, PascalCase
}
```

**Layer Assignment:**
```json
{
  "element_type": "Business_Actor",
  "layer": "BUSINESS"  // Must match element's layer (uppercase)
}
```

### Common Mistakes

❌ **Wrong:**
- `"element_type": "BusinessActor"` (no underscore)
- `"element_type": "business-actor"` (kebab-case)
- `"element_type": "business_actor"` (lowercase)
- `"layer": "Business"` (not uppercase)

✅ **Correct:**
- `"element_type": "Business_Actor"`
- `"layer": "BUSINESS"`

## Layer Descriptions

### BUSINESS Layer
**What the organization does to create value**
- Active structure: Actor, Role, Collaboration, Interface
- Behavior: Process, Function, Interaction, Event, Service
- Passive structure: Object, Contract, Representation, Product

### APPLICATION Layer
**Software applications and data used**
- Active structure: Component, Collaboration, Interface
- Behavior: Function, Interaction, Process, Event, Service
- Passive structure: Data_Object

### TECHNOLOGY Layer
**Technology infrastructure supporting applications**
- Active structure: Node, Device, System_Software, Collaboration, Interface, Path, Network
- Behavior: Function, Process, Interaction, Event, Service
- Passive structure: Artifact

### PHYSICAL Layer
**Physical world equipment and materials**
- Active structure: Equipment, Facility, Distribution_Network
- Passive structure: Material

### STRATEGY Layer
**Strategic direction and capabilities**
- Resource, Capability, Value_Stream, Course_of_Action

### MOTIVATION Layer
**Why things exist and what drives them**
- Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value

### IMPLEMENTATION Layer
**How change is realized**
- Work_Package, Deliverable, Implementation_Event, Plateau

## Selection Guide

**When modeling:**

**"Who does it?"** → Business_Actor, Business_Role
**"What does it do?"** → Business_Process, Business_Function
**"What service does it provide?"** → Business_Service, Application_Service
**"What software?"** → Application_Component
**"What data?"** → Data_Object, Business_Object
**"What infrastructure?"** → Node, Device, System_Software
**"What capability?"** → Capability (Strategy layer)
**"Why?"** → Goal, Driver, Requirement (Motivation layer)
**"How to implement?"** → Work_Package, Deliverable (Implementation layer)

## Examples by Use Case

### Service Architecture
```json
{
  "elements": [
    {"element_type": "Business_Actor", "name": "Customer"},
    {"element_type": "Application_Service", "name": "Order Service"},
    {"element_type": "Application_Component", "name": "Order System"}
  ]
}
```

### Infrastructure View
```json
{
  "elements": [
    {"element_type": "Application_Component", "name": "Web App"},
    {"element_type": "Node", "name": "Application Server"},
    {"element_type": "Device", "name": "Load Balancer"}
  ]
}
```

### Business Process
```json
{
  "elements": [
    {"element_type": "Business_Actor", "name": "Sales Rep"},
    {"element_type": "Business_Process", "name": "Create Quote"},
    {"element_type": "Business_Object", "name": "Quote"}
  ]
}
```

### Motivation View
```json
{
  "elements": [
    {"element_type": "Stakeholder", "name": "CEO"},
    {"element_type": "Goal", "name": "Increase Market Share"},
    {"element_type": "Requirement", "name": "Launch in Q2"}
  ]
}
```

---

**For relationship rules between these elements, see RELATIONSHIPS.md**
