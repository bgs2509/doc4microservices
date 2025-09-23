# Working Use Case Demonstrations

> **📋 DOCUMENTATION TYPE**: Working Demonstrations - Complete functional applications
> **👥 TARGET USERS**: Business stakeholders, developers, QA teams, product managers
> **🔗 RELATED**: [Learning Patterns](../examples/) *(or [.framework/examples/](.framework/examples/) when used as submodule)* | [AI Generation](../ai_agents/) *(or [.framework/ai_agents/](.framework/ai_agents/) when used as submodule)* | **[Complete Comparison Guide](../CLAUDE.md#documentation-types-guide)**

This folder contains complete, working applications that demonstrate the **Improved Hybrid Approach** architecture in real-world scenarios. Each use case is a fully functional, production-ready implementation that you can deploy, use, and learn from.

## 🎯 Purpose

**Working use cases serve to:**
- **Prove the architecture works** in real business scenarios
- **Provide complete reference implementations** for specific domains
- **Demonstrate service coordination** and data flow patterns
- **Show production practices** in action
- **Inspire new applications** by showing what's possible

## 📚 Available Use Cases

### 📋 **Task Management System**
**Location**: [task_management/](task_management/)
**Domain**: Personal Productivity
**Best for**: Learning service coordination, bot integration, background processing
**🚀 Quick Start**: See [task_management/README.md](task_management/README.md)

---

## 🔍 **Use Case Selection Guide**

### **For Learning Architecture:**
- **Browse available use cases** to find ones covering the patterns you want to learn
- **Focus on**: Service separation, HTTP-only data access, event-driven communication
- **Start simple**: Choose use cases in familiar business domains

### **For Business Stakeholders:**
- **Demo use cases** in domains similar to your business needs
- **Understand**: How microservices solve real business problems
- **Evaluate**: Technical feasibility and implementation approaches

### **For Developers:**
- **Study**: Complete implementations to understand production patterns
- **Copy**: Code patterns and architectural decisions
- **Extend**: Add features or create similar applications

### **For QA Teams:**
- **Test**: Real applications with complete functionality
- **Validate**: Integration testing patterns and approaches
- **Learn**: How to test microservices architectures

## 🏗️ **Architecture Patterns Demonstrated**

### **✅ Service Separation**
Each use case shows how different service types work together:
- **Data Services**: Centralized database access (PostgreSQL + MongoDB)
- **Business Services**: HTTP-only data access with business logic
- **Event-Driven Communication**: RabbitMQ for service coordination

### **✅ Production Practices**
- Containerized deployment with Docker Compose
- Complete observability stack (monitoring, logging, tracing)
- Real database integration with proper schemas
- Error handling and resilience patterns
- Security best practices (authentication, authorization)

### **✅ Real-World Complexity**
- User authentication and session management
- File upload and processing
- Natural language processing
- Background job processing
- Analytics and reporting
- Real-time notifications

## 📋 **Use Case Structure Template**

When adding new use cases, follow this structure:

```
use_cases/your_use_case/
├── README.md                    # Complete use case documentation
├── docker-compose.yml          # Service orchestration
├── docker-compose.override.yml # Development overrides (optional)
├── .env.example                # Environment template
├── services/                   # Business logic services
│   ├── api_service.py          # FastAPI REST API
│   ├── bot_service.py          # Bot interface (optional)
│   ├── worker_service.py       # Background workers (optional)
│   └── shared_dtos.py          # Common data transfer objects
├── tests/                      # Use case specific tests
│   ├── test_integration.py     # Cross-service integration tests
│   └── test_*.py               # Service-specific tests
└── docs/                       # Use case documentation
    ├── api_reference.md        # API endpoint documentation
    ├── deployment.md           # Deployment instructions
    └── architecture.md         # Use case specific architecture
```

## 🚀 **Quick Start Any Use Case**

### **Prerequisites**
- Docker & Docker Compose
- Python 3.12+ (for local development)
- Check individual use case README for specific requirements (API keys, tokens, etc.)

### **General Steps**
```bash
# 1. Navigate to use case
cd use_cases/[use_case_name]

# 2. Copy environment template
cp .env.example .env

# 3. Edit configuration
nano .env

# 4. Start services
docker-compose up -d

# 5. Verify health
curl http://localhost:8000/health
```

## 📊 **Monitoring & Observability**

Each use case includes complete observability:

### **Built-in Monitoring**
- **Grafana Dashboards**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

### **Logging & Tracing**
- **Structured Logging**: All services use structured logging with correlation IDs
- **Distributed Tracing**: Jaeger integration for request tracking
- **Error Tracking**: Centralized error handling and reporting

## 🧪 **Testing Examples**

Use cases demonstrate testing at all levels:

### **Unit Testing**
- Service logic testing with mocking
- HTTP client testing patterns
- Database interaction testing

### **Integration Testing**
- Real database testing with testcontainers
- Service-to-service communication testing
- Event-driven workflow testing

### **End-to-End Testing**
- Complete user workflow testing
- Cross-service integration validation
- Performance and load testing

## 🔧 **Development Guidelines**

### **Adding New Use Cases**

1. **Choose Domain**: Select a clear business domain (e-commerce, content management, etc.)
2. **Define Services**: Map business functions to service types (API, Bot, Worker)
3. **Follow Template**: Use the structure template above
4. **Implement Patterns**: Follow patterns from [examples/](../examples/) *(or [.framework/examples/](.framework/examples/) when used as submodule)*
5. **Add Documentation**: Include comprehensive README and API docs
6. **Test Thoroughly**: Include unit, integration, and E2E tests

### **Naming Conventions**
- **Folder Names**: `snake_case` (e.g., `task_management`, `e_commerce_platform`)
- **Service Names**: `{domain}_{type}_service` (e.g., `task_api_service`, `ecommerce_bot_service`)
- **Follow**: [Naming conventions guide](../docs/architecture/naming_conventions.mdc) *(or [.framework/docs/architecture/naming_conventions.mdc](.framework/docs/architecture/naming_conventions.mdc) when used as submodule)*

## 🔗 **Related Documentation**

### **For Implementation Guidance**
- **[Implementation Patterns](../examples/)** *(or [.framework/examples/](.framework/examples/) when used as submodule)*: Learn how to implement services correctly
- **[Architecture Guide](../docs/guides/ARCHITECTURE_GUIDE.md)** *(or [.framework/docs/guides/ARCHITECTURE_GUIDE.md](.framework/docs/guides/ARCHITECTURE_GUIDE.md) when used as submodule)*: Understand architectural constraints
- **[Development Commands](../docs/guides/DEVELOPMENT_COMMANDS.md)** *(or [.framework/docs/guides/DEVELOPMENT_COMMANDS.md](.framework/docs/guides/DEVELOPMENT_COMMANDS.md) when used as submodule)*: Commands for development and deployment

### **For AI Generation**
- **[AI Agents Framework](../ai_agents/)** *(or [.framework/ai_agents/](.framework/ai_agents/) when used as submodule)*: Generate new use cases automatically
- **[Feasibility Checker](../ai_agents/business_validation/feasibility_checker.yml)**: Validate new use case ideas

### **For Project Understanding**
- **[Main Guide](../CLAUDE.md)**: Complete project overview and navigation
- **[Technology Stack](../docs/reference/tech_stack.md)**: Technical specifications and versions

---

## 💡 **Next Steps**

### **For Business Users**
1. **Explore**: Browse existing use cases to understand capabilities
2. **Deploy**: Run use cases locally to see them in action
3. **Envision**: Consider how patterns apply to your business needs

### **For Developers**
1. **Study**: Examine complete implementations and patterns
2. **Experiment**: Modify existing use cases to understand the architecture
3. **Create**: Build new use cases following the established patterns

### **For AI Development**
1. **Reference**: Use as examples of what AI should generate
2. **Validate**: Ensure AI-generated code follows these patterns
3. **Extend**: Add new use cases to expand the reference library

**🎯 Each use case is a complete, working example of the Improved Hybrid Approach in action!**