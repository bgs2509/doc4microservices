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

### 📋 Task Management System
**Location**: [task_management/](task_management/)
**Domain**: Personal Productivity
**Best for**: Learning service coordination, bot integration, background processing
**🚀 Quick Start**: See [task_management/README.md](task_management/README.md)

---

## 🔍 Use Case Selection Guide

### For Learning Architecture
- **Browse available use cases** to find ones covering the patterns you want to learn
- **Focus on**: Service separation, HTTP-only data access, event-driven communication
- **Start simple**: Choose use cases in familiar business domains

### For Business Stakeholders
- **Demo use cases** in domains similar to your business needs
- **Understand**: How microservices solve real business problems
- **Evaluate**: Technical feasibility and implementation approaches

### For Developers
- **Study**: Complete implementations to understand production patterns
- **Copy**: Code patterns and architectural decisions
- **Extend**: Add features or create similar applications

### For QA Teams
- **Test**: Real applications with complete functionality
- **Validate**: Integration testing patterns and approaches
- **Learn**: How to test microservices architectures

## 🏗️ Architecture Patterns Demonstrated

### ✅ Service Separation
Each use case shows how different service types work together:
- **Data Services**: Centralized database access (PostgreSQL + MongoDB)
- **Business Services**: HTTP-only data access with business logic
- **Event-Driven Communication**: RabbitMQ for service coordination

### ✅ Production Practices
- Containerized deployment with Docker Compose
- Complete observability stack (monitoring, logging, tracing)
- Real database integration with proper schemas
- Error handling and resilience patterns
- Security best practices (authentication, authorization)

### ✅ Real-World Complexity
- User authentication and session management
- File upload and processing
- Natural language processing
- Background job processing
- Analytics and reporting
- Real-time notifications

## 📋 Use Case Structure Template

> **⚠️ IMPORTANT**: The structure of use cases in this directory may use a simplified flat layout for demonstration purposes. For all new projects, it is **mandatory** to follow the canonical project structure.

For the complete and mandatory project structure, see the [Project Structure Guide](LINKS_REFERENCE.md#developer-guides).

## 🚀 Quick Start Any Use Case

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)
- Check individual use case README for specific requirements (API keys, tokens, etc.)

### General Steps
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

## 🔧 Development Guidelines

### Adding New Use Cases

1. **Choose Domain**: Select a clear business domain.
2. **Define Services**: Map business functions to service types (API, Bot, Worker).
3. **Follow Structure**: Use the canonical project structure referenced in the template section above.
4. **Implement Patterns**: Follow patterns from the [Examples and Templates](LINKS_REFERENCE.md#examples-and-templates).
5. **Add Documentation**: Include a comprehensive README.
6. **Test Thoroughly**: Include unit, integration, and E2E tests.

### Naming Conventions
For all naming standards, refer to the single source of truth: the [Naming Conventions Guide](LINKS_REFERENCE.md#ide-rules-and-patterns).

## 🔗 Related Documentation

### For Implementation Guidance
- **[Implementation Patterns](LINKS_REFERENCE.md#examples-and-templates)**: Learn how to implement services correctly.
- **[Architecture Guide](LINKS_REFERENCE.md#core-documentation)**: Understand architectural constraints.
- **[Development Commands](LINKS_REFERENCE.md#developer-guides)**: Commands for development and deployment.

### For AI Generation
- **[AI Agents Framework](LINKS_REFERENCE.md#ai-agents)**: Generate new use cases automatically.
- **[Feasibility Checker](LINKS_REFERENCE.md#ai-agents)**: Validate new use case ideas.

### For Project Understanding
- **[Main Guide](LINKS_REFERENCE.md#core-documentation)**: Complete project overview and navigation.
- **[Technology Stack](LINKS_REFERENCE.md#core-documentation)**: Technical specifications and versions.

---

## 💡 Next Steps

### For Business Users
1. **Explore**: Browse existing use cases to understand capabilities
2. **Deploy**: Run use cases locally to see them in action
3. **Envision**: Consider how patterns apply to your business needs

### For Developers
1. **Study**: Examine complete implementations and patterns
2. **Experiment**: Modify existing use cases to understand the architecture
3. **Create**: Build new use cases following the established patterns

### For AI Development
1. **Reference**: Use as examples of what AI should generate
2. **Validate**: Ensure AI-generated code follows these patterns
3. **Extend**: Add new use cases to expand the reference library

**🎯 Each use case is a complete, working example of the Improved Hybrid Approach in action!**