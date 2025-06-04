# Frontend Documentation

## Overview

The LexiReport frontend is a cross-platform mobile and web application built with React Native and Expo. It provides a modern, user-friendly interface for authentication, report management, and AI-powered insights.

## Tech Stack
- React Native (Expo)
- TypeScript
- Zustand (State Management)
- Expo Router (Navigation)
- Axios (API communication)

## Project Structure
```
frontend/
├── app/
│   ├── (auth)/         # Authentication screens (login, register)
│   ├── (tabs)/         # Main app screens (profile, reports, upload, dashboard)
│   ├── user-management.tsx # User management screen
│   └── _layout.tsx     # Root layout
├── components/         # Reusable UI components (Header, PermissionGate, ChangePasswordModal, ui/)
├── hooks/              # Custom React hooks (useAuth, useTheme, usePermissions)
├── services/           # API and business logic (auth, user, report, api)
├── store/              # Zustand stores (themeStore)
├── models/             # TypeScript models/types (auth, user, report)
├── utils/              # Utility functions (storage)
├── config/             # App configuration (config.ts)
├── assets/             # Images and static assets
├── app.json            # Expo configuration
├── tsconfig.json       # TypeScript configuration
├── package.json        # NPM dependencies
└── README.md
```

## Setup

### Prerequisites
- Node.js 16+
- npm or yarn
- Expo CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

### Installation
1. Install dependencies:
```bash
npm install
```
2. Start the development server:
```bash
npx expo start
```
3. Run on specific platform:
```bash
npx expo run:ios      # iOS
npx expo run:android  # Android
npx expo start:web    # Web
```

### Environment Variables
Create a `.env` file in the root of the frontend directory:
```
API_URL=http://localhost:8000/api/v1
APP_ENV=development
```

## Main Features
- Secure authentication (JWT)
- User registration and login
- Report upload, listing, and detail view
- AI-powered insights and summaries
- Profile and account management
- User management (admin)
- Dark/Light mode support
- Responsive, modern UI

## Architecture
- **Component-based:** Reusable, themed UI components in `components/`
- **State management:** Global state with Zustand (`store/`), local state with React hooks (`hooks/`)
- **Navigation:** Expo Router for tabs, stacks, and deep linking (`app/`)
- **API communication:** Axios for REST API calls (`services/`), with error and loading state handling
- **Theming:** Custom hook for dark/light mode (`useTheme`), consistent color palette

## State Management
- **Zustand** is used for global state (e.g., theme in `store/themeStore.ts`)
- **React hooks** manage local state (e.g., form fields, loading states)

## Navigation
- **Expo Router** provides tab and stack navigation
- Auth flow (`(auth)/`) and main app flow (`(tabs)/`) are separated
- Deep linking is supported

## Authentication
- JWT tokens are stored securely (see `utils/storage.ts`)
- Auth context/hook (`hooks/useAuth.ts`) provides login, logout, and user info
- Protected routes/components use `PermissionGate` (`components/PermissionGate.tsx`)

## Theming
- Dark and light mode support via `hooks/useTheme.ts` and `store/themeStore.ts`
- All components use themed colors for consistency

## API Communication
- **Axios** is used for all API requests (`services/api.ts`)
- API base URL is set from environment variables (`config/config.ts`)
- Error and loading states are handled in hooks/components

## Testing
- Use `npm test` to run tests
- Coverage reports available with `npm test -- --coverage`
- Test files are colocated with components or in a `__tests__` directory

## Contribution Guidelines
1. Create a feature branch
2. Make your changes
3. Run tests and ensure all pass
4. Submit a pull request

## Further Reading
- [features.md](features.md) — Full feature list
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [technical-implementation.md](technical-implementation.md) — Technical details 