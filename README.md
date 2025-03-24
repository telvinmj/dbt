# DBT Metadata Explorer

A comprehensive web application for exploring, visualizing, and documenting your dbt projects' metadata with AI-enhanced descriptions.

## Project Overview

DBT Metadata Explorer scans your dbt projects, extracts metadata from manifest and catalog files, and provides a user-friendly interface to:

- Browse models across multiple dbt projects
- Visualize model lineage and dependencies
- Search and filter models by name, project, tags, and materialization type
- View and edit model descriptions
- Export metadata to JSON or YAML formats

## System Requirements

### Backend (Python)

- Python 3.9+
- FastAPI
- SQLAlchemy
- Other dependencies in `backend/requirements.txt`

### Frontend (React)

- Node.js 16+
- React 18
- Ant Design
- Dependencies in `frontend/package.json`

### dbt Projects

- dbt Core 1.0+
- Projects with generated manifest.json files (in target/ directory)

## Installation

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# Copy .env.example to .env and edit as needed
cp .env.example .env
```

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create a .env file with the backend URL if needed
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

## Running the Application

### Start the Backend

```bash
# From the backend directory with virtual environment activated
python run.py
# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend

```bash
# From the frontend directory
npm start
```

The application will be available at http://localhost:3000

## Features

- **Project Explorer**: Navigate through all your dbt projects
- **Model Details**: View model schemas, lineage, descriptions, and SQL code
- **Search & Filter**: Find models by name, project, tags, or materialization type
- **Lineage Visualization**: Visual representation of model dependencies
- **Auto-Refresh**: Automatically detect changes to dbt projects (can be toggled on/off)
- **Export Functionality**: Export metadata to JSON or YAML
- **AI-Generated Descriptions**: Optional AI-generated descriptions for models and columns

## Project Structure

```
dbt-metadata-explorer/
├── backend/                     # Backend API built with FastAPI
│   ├── api/                     # API endpoints
│   ├── models/                  # SQLAlchemy models
│   ├── routes/                  # API routes
│   ├── services/                # Business logic services
│   │   ├── metadata_service.py  # Main metadata processing service
│   │   ├── file_watcher_service.py  # File watcher for auto-refresh
│   │   └── ai_description_service.py  # AI description generation service
│   ├── exports/                 # Output directory for metadata exports
│   ├── main.py                  # Main application entry point
│   └── requirements.txt         # Python dependencies
│
├── frontend/                    # React frontend
│   ├── public/                  # Static assets
│   ├── src/                     # React source code
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service connectors
│   │   └── App.tsx              # Main React application
│   ├── package.json             # npm dependencies and scripts
│   └── .env                     # Environment variables
│
└── dbt_projects_2/              # Directory containing dbt projects
    ├── claims_processing/       # Sample dbt project
    ├── customer_risk/           # Sample dbt project
    └── policy_management/       # Sample dbt project
```

## Development

### Running in Development Mode

Both the frontend and backend include development servers that automatically reload when changes are detected:

- Backend: `python run.py` or `uvicorn backend.main:app --reload`
- Frontend: `npm start`

### Adding New dbt Projects

Add new dbt projects to the `dbt_projects_2/` directory, then:

1. Ensure they have been compiled with `dbt compile` or `dbt run` to generate manifest.json
2. Click "Refresh" in the web UI or restart the backend server
3. The new project should automatically appear in the UI

## Troubleshooting

Common issues and their solutions:

- **Backend not starting**: Check Python version and dependencies
- **Models not showing up**: Ensure manifest.json exists in the project's target/ directory
- **Lineage not displaying**: Check that model references use the ref() function correctly
- **Frontend not connecting**: Verify the API URL in .env or proxy setting in package.json
- **FileWatcher Not Working**: Verify the watcher status indicator in the UI, toggle if needed

## License

MIT License

## Contributors

Your Name and contributors

---

For more information, visit [github.com/yourusername/dbt-metadata-explorer](https://github.com/yourusername/dbt-metadata-explorer)
