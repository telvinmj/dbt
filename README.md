# DBT Metadata Explorer with AI Descriptions

This project creates a unified UI for exploring multiple DBT projects with AI-generated descriptions for tables and columns.

## Features

- **Multi-Project Aggregation**: Combines multiple DBT projects into a unified schema
- **AI-Generated Descriptions**: Automatically generates human-readable descriptions for columns and models
- **Interactive UI**: Browse, search, and visualize the data schema
- **Lineage Visualization**: View dependencies between models
- **User Corrections**: Edit AI-generated descriptions with your own corrections

## Setup

### Prerequisites

- Python 3.7+
- Node.js and npm
- DBT projects with manifest files

### Setting up the Gemini API Key

To enable AI-generated descriptions, you need to set up a Gemini API key:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:

```bash
export GEMINI_API_KEY='your-api-key'
```

You can also add this to your `.bashrc` or `.zshrc` for persistence.

### Running the Project

1. Start the backend:

```bash
cd backend
python run.py
```

2. Start the frontend:

```bash
cd frontend
npm install  # Only needed first time
npm start
```

3. Open your browser and navigate to http://localhost:3000

## Usage

### Refreshing Metadata

1. Navigate to your DBT projects
2. Run DBT commands to generate manifest files
3. In the UI, use the refresh button or API endpoint to reload metadata

### Viewing and Editing Descriptions

1. Browse to any model or column
2. AI-generated descriptions are marked with an "AI Generated" badge
3. Click "Edit" to modify the description
4. Your edits will be saved and marked as "User Edited"

## Architecture

- **Backend**: FastAPI Python server that extracts metadata from DBT projects
- **Frontend**: React application for visualizing the metadata
- **AI Integration**: Gemini API for generating descriptions based on context

## Troubleshooting

### AI Descriptions Not Appearing

- Check that your Gemini API key is properly set
- Ensure the backend has permissions to call external APIs
- Check the backend logs for any API errors

### Missing Models or Projects

- Verify that your DBT projects have generated manifest files
- Check the path to your DBT projects in the configuration
- Run a refresh to reload the metadata

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.# dbt
