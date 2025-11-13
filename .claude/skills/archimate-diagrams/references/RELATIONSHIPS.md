# ArchiMate 3.2 Relationship Reference

Complete guide to all 12 ArchiMate relationship types with validation rules and examples.

## Relationship Types Overview

| Category | Relationship | Symbol | Meaning | Example |
|----------|-------------|--------|---------|---------|
| **Structural** | Composition | ◆—— | Strong "part of" | Server *contains* CPU |
| | Aggregation | ◇—— | Weak "part of" | Department *groups* Employees |
| | Assignment | ——⊕ | Allocation | Actor *performs* Process |
| | Realization | ---▷ | Implementation | Component *realizes* Service |
| **Dependency** | Serving | --▷ | Provides functionality | Service *serves* Actor |
| | Access | --→ | Read/write/access | Process *accesses* Data |
| | Influence | ---→ | Modifies | Driver *influences* Goal |
| | Association | —— | Unspecified relationship | Element *relates to* Element |
| **Dynamic** | Flow | --▷ | Transfer | Process1 *flows to* Process2 |
| | Triggering | --▷◁ | Initiates | Event *triggers* Process |
| **Other** | Specialization | --|▷ | Is a kind of | Mobile App *specializes* App |
| | Junction | • | AND/OR split/join | Multiple paths |

## Structural Relationships

### Composition
**Strong ownership - child cannot exist without parent**

```json
{
  "relationship_type": "Composition",
  "from_element": "server",  // Parent (container)
  "to_element": "cpu"         // Child (component)
}
```

**Valid patterns:**
- Node *composes* Device
- Application_Component *composes* Application_Component
- Business_Actor *composes* Business_Actor

**Examples:**
- Server → CPU, Memory, Disk
- Enterprise → Division → Department
- Application Suite → Modules

### Aggregation
**Weak grouping - child can exist independently**

```json
{
  "relationship_type": "Aggregation",
  "from_element": "project_team",  // Container
  "to_element": "developer"         // Member
}
```

**Valid patterns:**
- Business_Collaboration *aggregates* Business_Actor
- Application_Collaboration *aggregates* Application_Component

**Examples:**
- Project Team → Team Members
- Portfolio → Products
- Network → Nodes

### Assignment
**Resource allocated to behavior or structure**

```json
{
  "relationship_type": "Assignment",
  "from_element": "developer",     // Resource
  "to_element": "coding_process"   // Behavior
}
```

**Valid patterns:**
- Business_Actor *assigned to* Business_Process
- Application_Component *assigned to* Application_Function
- Node *assigned to* Artifact

**Examples:**
- Developer → Development Task
- Server → Application Component
- Role → Responsibility

### Realization
**Implementation or fulfillment**

```json
{
  "relationship_type": "Realization",
  "from_element": "web_component",  // Implementer
  "to_element": "web_service"       // Interface/Service
}
```

**Valid patterns:**
- Application_Component *realizes* Application_Service
- Business_Process *realizes* Business_Service
- Node *realizes* Device

**Examples:**
- Payment Component → Payment Service
- Hiring Process → Recruitment Service
- Virtual Machine → Physical Server

## Dependency Relationships

### Serving
**Provides functionality to another element**

```json
{
  "relationship_type": "Serving",
  "from_element": "api_service",  // Provider
  "to_element": "mobile_app",     // Consumer
  "label": "provides data"
}
```

**Valid patterns:**
- Application_Service *serves* Business_Process
- Business_Service *serves* Business_Actor
- Technology_Service *serves* Application_Component

**Examples:**
- API → Mobile App
- Customer Service → Customer
- Database Service → Application

### Access
**Read, write, or access data/information**

```json
{
  "relationship_type": "Access",
  "from_element": "order_process",  // Accessor
  "to_element": "order_database",   // Data
  "label": "reads/writes"
}
```

**Access modifiers:**
- Read (default)
- Write
- Read/Write

**Valid patterns:**
- Business_Process *accesses* Business_Object
- Application_Component *accesses* Data_Object
- Business_Actor *accesses* Representation

**Examples:**
- Process → Database
- User → Document
- Service → Configuration

### Influence
**Affects or modifies (typically in motivation)**

```json
{
  "relationship_type": "Influence",
  "from_element": "market_pressure",  // Influencer
  "to_element": "digital_goal",       // Influenced
  "label": "drives"
}
```

**Influence strength:**
- ++ (very positive)
- + (positive)
- neutral
- - (negative)
- -- (very negative)

**Valid patterns:**
- Driver *influences* Goal
- Goal *influences* Requirement
- Assessment *influences* Goal

**Examples:**
- Market Competition → Innovation Goal
- Customer Feedback → Product Requirements
- Risk Assessment → Security Principle

### Association
**General unspecified relationship**

```json
{
  "relationship_type": "Association",
  "from_element": "element1",
  "to_element": "element2"
}
```

**Use when:**
- Relationship exists but type is unclear
- Documenting informal connections
- Temporary modeling before refinement

**Note:** Prefer specific relationships when possible for better semantic clarity.

## Dynamic Relationships

### Flow
**Transfer of information, goods, or control**

```json
{
  "relationship_type": "Flow",
  "from_element": "receive_order",    // Source
  "to_element": "validate_order",     // Target
  "label": "order data"
}
```

**Valid patterns:**
- Business_Process *flows to* Business_Process
- Application_Function *flows to* Application_Function
- Business_Object *flows through* Process

**Examples:**
- Order Process → Fulfillment Process
- Input Data → Transformation → Output Data
- Information Flow between Steps

### Triggering
**Temporal or causal relationship (initiates)**

```json
{
  "relationship_type": "Triggering",
  "from_element": "order_received",   // Trigger
  "to_element": "process_order",      // Triggered
  "label": "starts"
}
```

**Valid patterns:**
- Business_Event *triggers* Business_Process
- Application_Event *triggers* Application_Function
- Implementation_Event *triggers* Work_Package

**Examples:**
- Payment Received → Ship Order
- User Login → Load Dashboard
- Deadline → Notification

## Other Relationships

### Specialization
**"Is a kind of" - inheritance/subtyping**

```json
{
  "relationship_type": "Specialization",
  "from_element": "premium_customer",  // Specialized
  "to_element": "customer"              // General
}
```

**Valid patterns:**
- Business_Actor *specializes* Business_Actor
- Business_Process *specializes* Business_Process
- Application_Service *specializes* Application_Service

**Examples:**
- Mobile App → Generic App
- Express Delivery → Delivery Service
- Admin Role → User Role

## Common Patterns

### Service Pattern
```json
{
  "elements": [
    {"id": "actor", "element_type": "Business_Actor"},
    {"id": "service", "element_type": "Business_Service"},
    {"id": "process", "element_type": "Business_Process"}
  ],
  "relationships": [
    {"from_element": "service", "to_element": "actor", "relationship_type": "Serving"},
    {"from_element": "process", "to_element": "service", "relationship_type": "Realization"}
  ]
}
```
Pattern: Process *realizes* Service, Service *serves* Actor

### Data Access Pattern
```json
{
  "elements": [
    {"id": "app", "element_type": "Application_Component"},
    {"id": "data", "element_type": "Data_Object"}
  ],
  "relationships": [
    {"from_element": "app", "to_element": "data", "relationship_type": "Access"}
  ]
}
```
Pattern: Component *accesses* Data

### Assignment Pattern
```json
{
  "elements": [
    {"id": "actor", "element_type": "Business_Actor"},
    {"id": "role", "element_type": "Business_Role"},
    {"id": "process", "element_type": "Business_Process"}
  ],
  "relationships": [
    {"from_element": "actor", "to_element": "role", "relationship_type": "Assignment"},
    {"from_element": "role", "to_element": "process", "relationship_type": "Assignment"}
  ]
}
```
Pattern: Actor → Role → Process

### Layered Pattern
```json
{
  "elements": [
    {"id": "biz_service", "element_type": "Business_Service"},
    {"id": "app_service", "element_type": "Application_Service"},
    {"id": "tech_service", "element_type": "Technology_Service"}
  ],
  "relationships": [
    {"from_element": "app_service", "to_element": "biz_service", "relationship_type": "Serving"},
    {"from_element": "tech_service", "to_element": "app_service", "relationship_type": "Serving"}
  ]
}
```
Pattern: Technology *serves* Application *serves* Business

## Validation Rules

### ✅ Valid Combinations

**Cross-layer Serving:**
- Technology_Service → Application_Component ✓
- Application_Service → Business_Process ✓

**Same-layer Assignment:**
- Business_Actor → Business_Process ✓
- Application_Component → Application_Function ✓

**Realization:**
- Application_Component → Application_Service ✓
- Business_Process → Business_Service ✓

### ❌ Invalid Combinations

**Wrong direction:**
- Business_Actor → Technology_Service ✗ (layers too far apart)

**Wrong relationship:**
- Business_Process → Business_Actor with "Realization" ✗ (processes don't realize actors)

**Structural violations:**
- Business_Object → Business_Process with "Composition" ✗ (passive can't contain active)

## Troubleshooting

### Error: "Invalid relationship type"
**Solution:** Check spelling and case
- Use: `Serving` not `serving` or `SERVING`

### Error: "Relationship not allowed between X and Y"
**Solution:** Consult ArchiMate specification
- Some cross-layer relationships are restricted
- Check element aspects (active/behavior/passive)

### Error: "Wrong relationship direction"
**Solution:** Swap from/to elements
- Assignment: active → behavior
- Serving: provider → consumer
- Realization: implementer → interface

## Quick Reference Table

| From Element Type | To Element Type | Valid Relationships |
|-------------------|-----------------|---------------------|
| Business_Actor | Business_Process | Assignment |
| Business_Process | Business_Service | Realization |
| Business_Service | Business_Actor | Serving |
| Application_Component | Application_Service | Realization |
| Application_Service | Business_Process | Serving |
| Application_Component | Data_Object | Access |
| Node | Application_Component | Assignment |
| Technology_Service | Application_Component | Serving |
| Business_Process | Business_Object | Access, Flow |
| Business_Event | Business_Process | Triggering |
| Goal | Requirement | Realization |
| Driver | Goal | Influence |

---

**For element definitions and layer rules, see ELEMENTS.md**
