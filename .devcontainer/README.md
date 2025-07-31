# Monkey Coder Dev Container

This dev container provides a complete development environment for Monkey Coder with:

## 🚀 Features

- **Multi-language support**: Python 3.11 + Node.js 18
- **Database services**: PostgreSQL 15 + Redis 7
- **Development tools**: Pre-configured VS Code, linting, formatting
- **Monitoring**: Prometheus metrics collection
- **Auto-setup**: Dependencies and services configured automatically

## 🛠️ Quick Start

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for setup to complete (~3-5 minutes)
4. Start developing! 🎉

## 📝 Available Commands

```bash
# Development
yarn dev              # Start all dev servers
yarn build            # Build all packages
yarn test             # Run all tests
yarn lint             # Run linting

# Python specific
python -m monkey_coder.app.main  # Start API server
pytest                           # Run Python tests

# Database
psql -h postgres -U postgres monkey_coder_dev  # Connect to DB
redis-cli -h redis                             # Connect to Redis
```

## 🌐 Service URLs

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs**: http://localhost:3001  
- **Metrics**: http://localhost:9090

## 🔧 Customization

Edit `.devcontainer/devcontainer.json` to modify:
- VS Code extensions
- Port forwarding
- Environment variables
- Container features

## 🐛 Troubleshooting

**Container won't start?**
- Check Docker is running
- Ensure ports 3000, 8000, 5432, 6379 are available

**Database connection issues?**
- Wait for PostgreSQL to fully initialize (~30 seconds)
- Check logs: `docker-compose logs postgres`

**Python import errors?**
- Ensure packages are installed: `pip install -e packages/core`
- Check PYTHONPATH: `echo $PYTHONPATH`
