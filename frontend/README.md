# Nirvami Frontend

React + TypeScript frontend application for the Nirvami mental wellness platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:5173`

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── Dashboard.tsx   # Main dashboard
│   │   ├── ChatbotPage.tsx # AI chatbot interface
│   │   └── ...             # Feature pages
│   ├── services/
│   │   └── api.ts          # API client
│   ├── contexts/
│   │   └── AuthContext.tsx # Authentication context
│   ├── types/
│   │   └── api.types.ts    # TypeScript types
│   ├── styles/             # Global styles
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── index.html              # HTML template
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
└── vite.config.ts          # Vite configuration
```

## 🛠️ Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icons

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### API Configuration

The API client is configured in `src/services/api.ts`. Base URL defaults to `http://localhost:8000/api/v1`.

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎨 Key Features

- **Dashboard** - Unified health overview
- **AI Chatbot** - Conversational wellness assistant
- **Aura Visualization** - 3D emotional energy display
- **Emotion Tracking** - Timeline and analytics
- **Dosha Assessment** - Ayurvedic constitution quiz
- **Wellness Scoring** - Comprehensive health metrics
- **Yoga & Sound Therapy** - Personalized recommendations
- **Meal Tracking** - Diet-emotion correlations
- **Daily Routines** - Ayurvedic dinacharya tracking
- **Wearable Integration** - Health data management

## 🔗 API Integration

All API calls go through the centralized `api.ts` service:

```typescript
import api from '@/services/api';

// Example: Fetch today's wellness score
const wellness = await api.getTodayWellness();
```

## 📦 Dependencies

Key packages:
- `react` & `react-dom` - React framework
- `typescript` - Type checking
- `axios` - HTTP requests
- `framer-motion` - Animations
- `tailwindcss` - Utility-first CSS
- `lucide-react` - Icon library
- `@radix-ui/*` - Headless UI components

## 🐛 Troubleshooting

### Port Already in Use
If port 5173 is in use:
```bash
npm run dev -- --port 3000
```

### API Connection Issues
Check that backend is running on `http://localhost:8000`

### Build Errors
Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```
