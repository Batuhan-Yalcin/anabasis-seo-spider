# AI Anabasis SEO Spider - Frontend

Enterprise-grade AI-powered website intelligence platform.

## Tech Stack

- **Framework:** React 18 + Vite
- **Language:** TypeScript
- **Styling:** TailwindCSS 3.4
- **Components:** ShadCN UI + Custom
- **Animations:** Framer Motion
- **Code Editor:** Monaco Editor
- **State Management:** Zustand
- **API Client:** Axios + React Query
- **Routing:** React Router v6
- **Icons:** Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Server

The app will be available at `http://localhost:5173`

API proxy is configured to forward `/api/*` requests to `http://localhost:8000`

## Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components (Sidebar, TopBar)
│   ├── ui/              # Base UI components (Button, Card, Badge)
│   └── domain/          # Business-specific components
├── pages/               # Page components
├── services/            # API service layer
├── stores/              # Zustand stores
├── types/               # TypeScript types
├── lib/                 # Utilities and helpers
└── App.tsx              # Main app component
```

## Design System

### Colors

- **Background:** Dark blue palette (#0A0E1A, #131825, #1C2333)
- **Accent:** Electric blue (#00D9FF) + Purple (#8B5CF6)
- **Severity:** Critical (red), High (amber), Medium (purple), Low (green)

### Typography

- **UI:** Inter
- **Code:** JetBrains Mono
- **Display:** Clash Display

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Environment Variables

Create a `.env` file in the root:

```env
VITE_API_URL=http://localhost:8000
```

## License

Proprietary - AI Anabasis

