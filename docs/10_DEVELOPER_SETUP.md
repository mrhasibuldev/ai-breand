# NexusAI Developer Setup Guide

## Overview

This guide helps new developers set up the NexusAI development environment on their local machine.

## Prerequisites

### Required Software

- **Node.js**: Version >=22 and <25
  - Download from: https://nodejs.org/
  - Verify: `node --version` (should show v22.x.x or v24.x.x)
  
- **pnpm**: Version 11.19.0
  - Install: `npm install -g pnpm@11.19.0`
  - Verify: `pnpm --version` (should show 11.19.0)

- **Git**: For version control
  - Download from: https://git-scm.com/
  - Verify: `git --version`

### Optional Software

- **VS Code**: Recommended IDE
  - Download from: https://code.visualstudio.com/
  - Extensions recommended (see .vscode/extensions.json)

- **PostgreSQL Client**: For direct database access
  - pgAdmin, DBeaver, or psql command-line tool

## Repository Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "C:\Users\Nusaiba\Desktop\Ai Breand"
```

### 2. Install Dependencies

```bash
pnpm install
```

This installs dependencies for all workspaces (apps and packages).

### 3. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the following variables:

```env
# Node Environment
NODE_ENV=development

# Ports
WEB_PORT=3000
API_PORT=4000
API_ORIGIN=http://localhost:4000
WEB_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_ORIGIN=http://localhost:4000

# Database (Required)
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql://[user].[project_id]:[password]@[neon-hostname]/[database]?sslmode=verify-full
DATABASE_POOL_SIZE=20

# Cookie Secret (Required for production)
COOKIE_SECRET=<generate-secure-random-string>

# AI Service (Required for chat)
AI_SERVICE_URL=http://127.0.0.1:8000

# Identity Provider (Optional)
IDENTITY_ISSUER_URL=
IDENTITY_AUDIENCE=

# AI Provider (Optional)
AI_PROVIDER_ALIAS=mock
AI_PROVIDER_BASE_URL=
AI_PROVIDER_API_KEY=

# Object Storage (Optional)
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_REGION=

# Observability (Optional)
OTEL_EXPORTER_OTLP_ENDPOINT=
```

### 4. Generate Cookie Secret

Generate a secure random string for COOKIE_SECRET:

```bash
openssl rand -base64 32
```

Use the output as the COOKIE_SECRET value in `.env`.

### 5. Database Setup

#### Neon PostgreSQL Setup

1. Create a Neon account at https://neon.tech
2. Create a new project
3. Get the connection string from the Neon dashboard
4. Set DATABASE_URL in `.env`

#### Apply Database Migrations

The database schema is created automatically on first run, or you can apply migrations manually:

```bash
cd packages/database-core
# Migrations are applied automatically by the backend
```

To verify the schema:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' 
ORDER BY table_name;
```

## Development Workflow

### Start All Services

Start all applications in parallel:

```bash
pnpm dev
```

This starts:
- Web app on http://localhost:3000
- API server on http://localhost:4000
- Worker (if configured)

### Start Individual Services

#### Web App Only

```bash
cd apps/web
pnpm dev
```

Access at: http://localhost:3000

#### API Server Only

```bash
cd apps/api
pnpm dev
```

Access at: http://localhost:4000

#### Worker Only

```bash
cd apps/worker
pnpm dev
```

### Start AI Service

The AI service is external and must be started separately:

```bash
# Navigate to AI service directory (if part of repo)
cd path/to/ai-service
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or if the AI service is a separate repository, follow its setup instructions.

Access at: http://127.0.0.1:8000

## Building

### Build All Packages and Apps

```bash
pnpm build
```

### Build Specific App

```bash
cd apps/web
pnpm build
```

```bash
cd apps/api
pnpm build
```

## Type Checking

### Type Check All

```bash
pnpm typecheck
```

### Type Check Specific App

```bash
cd apps/web
pnpm typecheck
```

```bash
cd apps/api
pnpm typecheck
```

## Linting

### Lint All

```bash
pnpm lint
```

### Lint Specific App

```bash
cd apps/web
pnpm lint
```

```bash
cd apps/api
pnpm lint
```

## Formatting

### Format All

```bash
pnpm format
```

### Check Formatting

```bash
pnpm format:check
```

## Testing

### Run All Tests

```bash
pnpm test
```

### Run Foundation Tests

```bash
pnpm test:foundation
```

### Run Keyboard Tests (Playwright)

```bash
pnpm test:keyboard
```

## Project Structure

```
C:\Users\Nusaiba\Desktop\Ai Breand\
├── apps/
│   ├── api/          # Fastify backend (port 4000)
│   ├── web/          # Next.js frontend (port 3000)
│   └── worker/       # Background worker
├── packages/
│   ├── database-core/    # PostgreSQL client
│   ├── auth-core/        # Auth utilities
│   ├── ai-core/          # AI integration
│   ├── repositories/     # Data access layer
│   └── ...
├── docs/              # Documentation
└── package.json       # Root package.json
```

## Common Tasks

### Add a New Dependency

#### Add to Root (Shared)

```bash
pnpm add <package-name>
```

#### Add to Specific App

```bash
cd apps/web
pnpm add <package-name>
```

```bash
cd apps/api
pnpm add <package-name>
```

#### Add to Specific Package

```bash
cd packages/database-core
pnpm add <package-name>
```

### Add a New Package

1. Create directory in `packages/`
2. Add `package.json`
3. Add to `pnpm-workspace.yaml` (if needed)
4. Install dependencies

### Create a New Migration

1. Create SQL file in `packages/database-core/migrations/`
2. Name it: `XXX_description.sql` (where XXX is next number)
3. Add migration to COMPLETE_SCHEMA.sql
4. Test migration

### Add a New API Endpoint

1. Create route file in `apps/api/src/routes/`
2. Register route in `apps/api/src/app.ts`
3. Add authentication middleware if needed
4. Test with cURL or Postman

### Add a New Frontend Component

1. Create component file in `apps/web/app/components/`
2. Export component
3. Import and use in parent component
4. Add styles if needed

## Troubleshooting

### Port Already in Use

If port 3000 or 4000 is already in use:

**Option 1**: Change port in `.env`:
```env
WEB_PORT=3001
API_PORT=4001
```

**Option 2**: Kill process using the port:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Database Connection Failed

1. Verify DATABASE_URL is correct
2. Check Neon dashboard for connection issues
3. Verify internet connection
4. Check firewall settings

### AI Service Unavailable

1. Verify AI_SERVICE_URL is correct
2. Start AI service (see above)
3. Check AI service logs
4. Verify AI service is responding:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

### Module Not Found Errors

1. Run `pnpm install` to ensure all dependencies are installed
2. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules apps/*/node_modules packages/*/node_modules
   pnpm install
   ```

### TypeScript Errors

1. Run `pnpm typecheck` to see all errors
2. Fix type errors in code
3. Ensure all dependencies are installed

### Build Failures

1. Run `pnpm typecheck` first
2. Fix any type errors
3. Run `pnpm build` again
4. Check build logs for specific errors

## IDE Setup

### VS Code

Recommended extensions (see `.vscode/extensions.json`):
- ESLint
- Prettier
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense (if using Tailwind)

Recommended settings (see `.vscode/settings.json`):
- Format on save
- ESLint on save
- TypeScript strict mode

## Git Workflow

### Branch Strategy

- `main`: Production branch
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Commit Convention

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add user profile editing"
git commit -m "fix: resolve session validation bug"
```

## Development Best Practices

### Code Style

- Use Prettier for formatting
- Run `pnpm format` before committing
- Follow existing code style
- Add comments for complex logic

### Type Safety

- Use TypeScript for all new code
- Avoid `any` type
- Define interfaces for data structures
- Run `pnpm typecheck` before committing

### Testing

- Write tests for new features
- Run `pnpm test` before committing
- Ensure all tests pass

### Documentation

- Update documentation when changing features
- Add comments for complex functions
- Keep README files up to date

## Useful Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start all services |
| `pnpm build` | Build all packages |
| `pnpm typecheck` | Type check all |
| `pnpm lint` | Lint all |
| `pnpm format` | Format all |
| `pnpm test` | Run tests |
| `pnpm check` | Run all checks (format, lint, typecheck, test, build) |

## Resources

### Documentation

- [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) - Project overview
- [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md) - Codebase structure
- [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) - Architecture
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema

### External Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Fastify Documentation](https://www.fastify.io/docs/latest/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neon Documentation](https://neon.tech/docs)
- [pnpm Documentation](https://pnpm.io)

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Check existing documentation in docs/
3. Check NEXUSAI_FULL_REPAIR_REPORT.md for known issues
4. Search GitHub issues
5. Ask in team communication channel

## Next Steps

After setup:

1. Read [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) to understand the project
2. Read [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) to learn the architecture
3. Explore the codebase using [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md)
4. Start making changes!
