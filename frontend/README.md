# 🖥️ TruthLayer Frontend

The React-based web interface for **TruthLayer**, an AI-powered fact-checking engine. This application allows users to upload PDF documents and view real-time claim verification results streamed from the backend.

## 🚀 Features

- **Drag-and-Drop Upload**: Easy PDF uploading using a custom `UploadZone` component.
- **Real-time Streaming**: Uses Server-Sent Events (SSE) to display verification results as they arrive.
- **Interactive Claim Cards**: Displays claim status (Verified, Inaccurate, False, Unverifiable) with source links and confidence scores.
- **Dynamic Filtering**: Filter results by verdict type or search for specific keywords.
- **Progress Tracking**: Visual feedback during the parsing, extraction, and verification stages.
- **Responsive Design**: Modern UI built with Vanilla CSS and React.

## 🛠️ Tech Stack

- **Framework**: [React 18](https://reactjs.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **State Management**: React Hooks (useState, useCallback, useRef)
- **Styling**: Vanilla CSS (Custom design system)
- **Deployment**: [Vercel](https://vercel.com/)

## 📁 Structure

- `src/components/`: Reusable UI components.
  - `ClaimCard.jsx`: Individual result display.
  - `UploadZone.jsx`: File upload logic and UI.
  - `ProgressBar.jsx`: Multi-stage progress indicator.
  - `ResultsPanel.jsx`: Filtering and summary dashboard.
- `src/App.jsx`: Main application logic and SSE stream handling.
- `src/index.css`: Global styles and animations.

## 🔧 Local Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Environment Variables**:
   Create a `.env.local` file in the `frontend` directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Run Development Server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

## 🚢 Deployment

The frontend is configured for deployment on **Vercel**.
- `vercel.json`: Handles SPA routing to ensure `index.html` is served for all paths.
- Ensure `VITE_API_URL` is set to your production backend URL in the Vercel dashboard.
