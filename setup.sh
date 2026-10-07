#!/bin/bash
set -e

echo "🚀 VoiceFlow AI — Setup"
echo "========================"
echo ""

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.12+ required. Install from python.org"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js 18+ required. Install from nodejs.org"; exit 1; }

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
NODE_VERSION=$(node -v)

echo "✅ Python $PYTHON_VERSION"
echo "✅ Node.js $NODE_VERSION"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend
pip install -r requirements.txt -q
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env from template"
fi
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install --silent
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the app:"
echo "   Terminal 1: cd backend && uvicorn app.main:app --reload"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "🌐 Open: http://localhost:5173"
echo "📧 Login: admin@voiceflow.ai / admin123"
echo ""
