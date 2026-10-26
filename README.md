# NexusAI — Personal AI Health & Wellness Companion

NexusAI is an intelligent AI-powered application designed to assist users with health and wellness goals through conversational AI interactions.

---

## 🌟 Features

- **AI Chat Interface** - Interactive chat with AI assistant
- **User Authentication** - Secure signup and login with session management
- **Guest Mode** - Try the application without signing up
- **Conversation History** - Save and revisit past conversations
- **Profile Management** - Customize your profile with avatar and settings
- **Responsive Design** - Works on desktop and mobile devices

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15.5.24
- **UI Library**: React 19
- **Language**: TypeScript
- **Icons**: lucide-react
- **Styling**: CSS with CSS variables

### Backend
- **Framework**: Fastify 5
- **Language**: TypeScript
- **Authentication**: bcrypt for password hashing
- **Session Management**: HTTP-only cookies
- **CORS**: @fastify/cors

### Database
- **Provider**: PostgreSQL via Neon
- **Schema**: nexus (custom schema)
- **Connection**: PostgreSQL connection string

### AI Service
- **Type**: External Python FastAPI/ML service
- **URL**: http://127.0.0.1:8000 (configurable)

### Package Management
- **Manager**: pnpm 11.19.0
- **Node Version**: >=22 <25

---

## 📚 Documentation

Comprehensive technical documentation is available in the [`docs/`](./docs) directory:

- [Documentation Index](./docs/README.md) - Central documentation hub
- [Project Overview](./docs/01_PROJECT_OVERVIEW.md) - What NexusAI is and how it works
- [Codebase Structure](./docs/02_CODEBASE_STRUCTURE.md) - Folder and file organization
- [System Architecture](./docs/03_SYSTEM_ARCHITECTURE.md) - Architecture diagrams
- [Frontend Guide](./docs/04_FRONTEND_GUIDE.md) - Frontend implementation details
- [Backend API Reference](./docs/05_BACKEND_API_REFERENCE.md) - Complete API documentation
- [Database Guide](./docs/06_DATABASE_GUIDE.md) - Database schema and relationships
- [Authentication & Security](./docs/07_AUTHENTICATION_SECURITY.md) - Auth implementation
- [AI Brain Architecture](./docs/08_AI_BRAIN_ARCHITECTURE.md) - AI service integration
- [Storage & Media](./docs/09_STORAGE_AND_MEDIA.md) - File and image storage
- [Developer Setup](./docs/10_DEVELOPER_SETUP.md) - Setup guide for new developers

---

## 🚀 Quick Start

### Prerequisites
- Node.js >=22 <25
- pnpm 11.19.0
- PostgreSQL database (Neon recommended)
- Python AI service (for chat functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mrhasibuldev/ai-breand.git
   cd ai-breand
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the development servers**
   ```bash
   # Terminal 1: Backend API
   cd apps/api
   npm run dev

   # Terminal 2: Frontend Web
   cd apps/web
   npm run dev

   # Terminal 3: AI Service (if available)
   # Start your Python AI service at http://127.0.0.1:8000
   ```

5. **Open the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:4000

---

## 📖 Usage

### For New Developers

1. Read the [Developer Setup Guide](./docs/10_DEVELOPER_SETUP.md)
2. Review the [Project Overview](./docs/01_PROJECT_OVERVIEW.md)
3. Study the [System Architecture](./docs/03_SYSTEM_ARCHITECTURE.md)

### For Feature Development

1. Check the [Backend API Reference](./docs/05_BACKEND_API_REFERENCE.md)
2. Review the [Database Guide](./docs/06_DATABASE_GUIDE.md)
3. Study the [Frontend Guide](./docs/04_FRONTEND_GUIDE.md)

---

## 🔧 Available Scripts

- `pnpm dev` - Start all services in parallel
- `pnpm build` - Build all packages
- `pnpm typecheck` - Run TypeScript type checking
- `pnpm lint` - Run ESLint
- `pnpm test` - Run tests

---

## 🏗️ Project Structure

```
ai-breand/
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
├── docs/              # Technical documentation
└── package.json       # Root package.json (pnpm workspaces)
```

---

## 🔒 Security & Boundaries

- The web app calls the versioned API; it never accesses the database or provider secrets
- Domain services own business state, ownership, consent, lifecycle, and safety policy
- AI traffic goes through the backend API to an external AI service
- Session management uses HTTP-only cookies with bcrypt token hashing
- Rate limiting is implemented on authentication endpoints

---

## 📝 Development Guidelines

1. **Before making changes**, read the relevant documentation in the `docs/` directory
2. **Follow the existing code style** and architecture patterns
3. **Run type checking** before committing: `pnpm typecheck`
4. **Test your changes** manually before pushing
5. **Commit messages** should be clear and descriptive
6. **Never commit secrets** - use environment variables instead

---

## 🌐 Key Configuration

- **Web Origin**: http://localhost:3000
- **API Origin**: http://localhost:4000
- **AI Service URL**: http://127.0.0.1:8000
- **Database**: PostgreSQL via Neon (DATABASE_URL)

---

## 📄 License

This project is licensed under the terms specified in the repository.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Read the documentation first
2. Follow the coding standards
3. Test your changes thoroughly
4. Submit clear pull requests with descriptive messages

---

## 📞 Support

For detailed technical information, please refer to the [comprehensive documentation](./docs/README.md).

---

**Last Updated**: 2026-10-26
