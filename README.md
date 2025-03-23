# DBT Metadata Explorer with AI Descriptions

A unified UI for exploring multiple DBT projects with AI-generated descriptions for models and columns.

## Features

- **Multi-Project Aggregation**: Combines multiple DBT projects into a unified schema
- **AI-Generated Descriptions**: Automatically generates human-readable descriptions for columns and models
- **Interactive UI**: Browse, search, and visualize the data schema
- **Lineage Visualization**: View dependencies between models across projects
- **User Corrections**: Edit AI-generated descriptions with domain knowledge
- **Dynamic Documentation**: Automatic updates when DBT projects change
- **Export Capability**: Export documentation in JSON and YAML formats
- **Advanced Search & Filtering**: Search and filter models across projects by name, tags, and materialization
- **Cross-Project Relationships**: Visual indicators for models with dependencies in other projects

## System Architecture

The system consists of three main components:

1. **dbt Projects**: Standard dbt projects with models, seeds, and configurations
2. **Backend Server**: FastAPI service that processes dbt metadata and provides API endpoints
3. **Frontend UI**: React application that visualizes the unified schema

### Data Flow

1. dbt generates `manifest.json` and `catalog.json` files
2. Backend scans these files and combines them into `uni_metadata.json`
3. AI generates descriptions for models and columns
4. Frontend fetches and displays this unified metadata
5. FileWatcher service monitors for changes and triggers refresh

## Setup and Installation

### Prerequisites

- Python 3.7+
- Node.js and npm
- dbt-core installed
- Google Gemini API key (for AI descriptions)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key:
   ```
   export GEMINI_API_KEY='your-api-key'
   ```
   Or edit the `.env` file.

4. Start the backend server:
   ```
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the frontend development server:
   ```
   npm start
   ```

### dbt Projects Setup

1. Navigate to the dbt_projects_2 directory
   ```
   cd dbt_projects_2
   ```

2. Generate documentation for projects:
   ```
   ./run_dbt.sh claims_processing docs generate
   ./run_dbt.sh policy_management docs generate
   ./run_dbt.sh customer_risk docs generate
   ```

## Testing the Complete System

Follow these steps to test the full functionality:

### 1. Testing Multi-Project Aggregation

1. Start the backend and frontend servers
2. Navigate to the Models page in the UI
3. Verify that models from all three projects (claims_processing, policy_management, customer_risk) appear in the list
4. Check that each model displays its project name correctly

### 2. Testing AI-Generated Descriptions

1. Open a model detail page for any model
2. Look for the "AI Generated" badge next to descriptions
3. Verify that columns have meaningful descriptions

If descriptions aren't appearing:
- Check that your Gemini API key is correctly set in `backend/.env`
- Ensure the backend can access the Gemini API
- Check backend logs for any API errors

### 3. Testing Lineage Visualization

1. Navigate to the Lineage page
2. Click on any model to see its connections
3. Verify that cross-project connections are displayed correctly
4. Open a model's detail page and check the Lineage tab

### 4. Testing User Corrections

1. Open a model with an AI-generated description
2. Click the "Edit" button next to the description
3. Make changes and save
4. Verify that the description updates and shows a "User Edited" badge

### 5. Testing Dynamic Documentation

1. Make a change to a dbt model's SQL file
2. Re-run `dbt compile` or `dbt docs generate` for that project
3. Wait 30 seconds for the File Watcher to detect the change, or click the "Refresh" button
4. Verify that the UI updates with the new information

### 6. Testing Export Functionality

1. Click the "Export" button in the header
2. Select "Export as JSON" or "Export as YAML"
3. Verify that the file downloads correctly and contains all project metadata

### 7. Testing Advanced Search and Filtering

1. Navigate to the Models page in the UI
2. Use the search box to find models by name or description
3. Click the "Advanced Search" button to reveal additional filters
4. Try filtering by:
   - Project: Select a specific project to view only its models
   - Tag: Filter models with specific tags
   - Materialization Type: View only models with specific materializations
5. Observe the filter tags that appear showing active filters
6. Clear filters to return to the full list

### 8. Testing Cross-Project Relationship Visualization

1. On the Models page, look for models with the "Cross-Project" indicator
2. Click on one of these models to view its details
3. On the model details page, see the "Related Models" section
4. Verify that models from different projects are clearly highlighted
5. Click on related models to navigate between projects

## Troubleshooting

### Backend Issues

- **Missing Metadata**: Run `dbt docs generate` for each project to ensure manifest and catalog files exist
- **AI Description Errors**: Check Gemini API key and backend logs
- **FileWatcher Not Working**: Verify the watcher status indicator in the UI, toggle if needed

### Frontend Issues

- **Connection Errors**: Ensure backend is running and CORS is properly configured
- **Missing Data**: Check network requests in browser DevTools
- **Visualization Problems**: Clear browser cache and refresh

## Project Structure

```
/dbt/
├── backend/                 # FastAPI backend server
│   ├── services/            # Core services
│   │   ├── metadata_service.py    # Processes dbt metadata
│   │   ├── ai_description_service.py  # Generates descriptions with AI
│   │   └── file_watcher_service.py    # Monitors for changes
│   ├── main.py              # API endpoints
│   └── run.py               # Server entry point
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Main application pages
│   │   └── services/        # API client services
│   └── public/              # Static assets
└── dbt_projects_2/          # Sample dbt projects
    ├── claims_processing/   # Claims processing project
    ├── policy_management/   # Policy management project
    ├── customer_risk/       # Customer risk project
    └── profiles.yml         # dbt connection profiles
```

## API Endpoints

The backend provides the following key endpoints:

- `GET /api/projects` - List all dbt projects
- `GET /api/models` - List all models with optional filtering
- `GET /api/models/{model_id}` - Get details for a specific model
- `GET /api/models/{model_id}/lineage` - Get lineage information for a model
- `POST /api/models/{model_id}/description` - Update a model's description
- `POST /api/columns/{model_id}/{column_name}/description` - Update a column's description
- `POST /api/refresh` - Trigger metadata refresh
- `GET /api/export/json` - Export metadata as JSON
- `GET /api/export/yaml` - Export metadata as YAML
- `GET /api/watcher/status` - Get file watcher status
- `POST /api/watcher/toggle` - Enable/disable file watcher

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
