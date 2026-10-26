# NexusAI Technical Documentation

This directory contains comprehensive technical documentation for the NexusAI application.

## Documentation Index

### Core Documentation
1. **[01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md)** - What NexusAI is, capabilities, tech stack, and architecture overview
2. **[02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md)** - Folder/file structure with explanations
3. **[03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md)** - System architecture with Mermaid diagrams
4. **[04_FRONTEND_GUIDE.md](./04_FRONTEND_GUIDE.md)** - Frontend implementation details
5. **[05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md)** - Complete API endpoint documentation
6. **[06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md)** - Database schema, tables, and relationships
7. **[07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md)** - Authentication implementation and security
8. **[08_AI_BRAIN_ARCHITECTURE.md](./08_AI_BRAIN_ARCHITECTURE.md)** - AI service integration
9. **[09_STORAGE_AND_MEDIA.md](./09_STORAGE_AND_MEDIA.md)** - File and image storage
10. **[10_DEVELOPER_SETUP.md](./10_DEVELOPER_SETUP.md)** - Setup guide for new developers

### Advanced Documentation
11. **[11_DATA_FLOWS_AND_WORKFLOWS.md](./11_DATA_FLOWS_AND_WORKFLOWS.md)** - User workflow walkthroughs
12. **[12_TESTING_AND_QA.md](./12_TESTING_AND_QA.md)** - Testing coverage and verification
13. **[13_TECHNICAL_DEBT_AND_LIMITATIONS.md](./13_TECHNICAL_DEBT_AND_LIMITATIONS.md)** - Known issues and technical debt
14. **[14_FUTURE_ROADMAP.md](./14_FUTURE_ROADMAP.md)** - Development roadmap
15. **[15_ARCHITECTURE_DECISIONS.md](./15_ARCHITECTURE_DECISIONS.md)** - Architectural decision records (ADRs)

## Quick Start

For new developers, start with:
1. [10_DEVELOPER_SETUP.md](./10_DEVELOPER_SETUP.md) - Get the development environment running
2. [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) - Understand the project
3. [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) - Learn the architecture

For feature development:
1. [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API endpoints
2. [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema
3. [04_FRONTEND_GUIDE.md](./04_FRONTEND_GUIDE.md) - Frontend components

## Documentation Standards

- All documentation uses actual file paths from the repository
- Real function names, component names, and code references are used
- Mermaid diagrams are included for architecture visualization
- Tables are used for API endpoints, environment variables, and database schema
- Information is detailed enough for a junior developer
- Implemented vs planned features are clearly distinguished
- Uncertain information is marked as UNKNOWN or UNVERIFIED
- No secrets, passwords, or tokens are included

## Repository Structure

```
C:\Users\Nusaiba\Desktop\Ai Breand\
├── apps/
│   ├── api/          # Fastify backend (port 4000)
│   ├── web/          # Next.js frontend (port 3000)
│   └── worker/       # Background worker
├── packages/
│   ├── database-core/    # PostgreSQL client and migrations
│   ├── auth-core/        # Authentication utilities
│   ├── ai-core/          # AI service integration
│   ├── repositories/     # Data access layer
│   └── ...
├── docs/              # This directory
└── package.json       # Root package.json (pnpm workspaces)
```

## Technology Stack

- **Frontend**: Next.js 15.5.24, React 19, TypeScript, lucide-react
- **Backend**: Fastify 5, TypeScript, @fastify/cookie, @fastify/cors, bcrypt
- **Database**: PostgreSQL via Neon (nexus schema)
- **AI Service**: External Python service at http://127.0.0.1:8000
- **Package Manager**: pnpm 11.19.0
- **Node**: v22-v24

## Key Configuration

- **Web Origin**: http://localhost:3000
- **API Origin**: http://localhost:4000
- **AI Service URL**: http://127.0.0.1:8000
- **Database**: Neon PostgreSQL (DATABASE_URL)

## Documentation Maintenance

This documentation was created on 2026-10-26. When making changes to the codebase, update the relevant documentation files to keep them in sync.

## Additional Resources

- [NEXUSAI_FULL_REPAIR_REPORT.md](../NEXUSAI_FULL_REPAIR_REPORT.md) - Detailed repair report with bug fixes
- [README.md](../README.md) - Project README with phase information
- [.env.example](../.env.example) - Environment variable reference (names only)
