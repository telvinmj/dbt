import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Tabs, Spin, Alert, Layout, Menu, Space, Button } from 'antd';
import { 
  TableOutlined, 
  ApartmentOutlined, 
  ProjectOutlined, 
  DashboardOutlined,
  DatabaseOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import LineageGraph from './components/LineageGraph';
import { Model, Project, LineageLink } from './types';
import { getModels, getProjects, getModelWithLineage, initializeDatabase, refreshMetadata } from './services/api';
import ModelDetail from './pages/ModelDetail';
import ExportButton from './components/ExportButton';
import WatcherStatusIndicator from './components/WatcherStatusIndicator';

const { Header, Content, Footer } = Layout;
const { TabPane } = Tabs;

function App() {
  const [models, setModels] = useState<Model[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [lineage, setLineage] = useState<LineageLink[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [hasAIDescriptions, setHasAIDescriptions] = useState<boolean>(false);
  
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    console.log("App component mounted");
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Check if backend is available
        try {
          await axios.get('http://localhost:8000/api/health');
        } catch (e) {
          // If backend is not available, try to initialize the database
          try {
            await initializeDatabase();
          } catch (initError) {
            console.error("Failed to initialize database:", initError);
          }
        }
        
        // Fetch projects
        const projectsData = await getProjects();
        setProjects(projectsData);
        
        // Fetch models
        const modelsData = await getModels();
        setModels(modelsData);
        
        // Check if any models have AI descriptions
        const hasAI = modelsData.some(model => 
          model.ai_description || 
          model.columns?.some(column => column.ai_description)
        );
        setHasAIDescriptions(hasAI);
        
        // Create lineage data
        const lineageLinks: LineageLink[] = [];
        for (const model of modelsData) {
          if (model.id) {
            try {
              const modelWithLineage = await getModelWithLineage(model.id);
              
              // Add upstream links
              if (modelWithLineage.upstream) {
                for (const upstream of modelWithLineage.upstream) {
                  lineageLinks.push({
                    source: upstream.id.toString(),
                    target: model.id.toString()
                  });
                }
              }
            } catch (e) {
              console.error(`Error fetching lineage for model ${model.id}:`, e);
            }
          }
        }
        
        setLineage(lineageLinks);
        setLoading(false);
      } catch (e) {
        console.error("Error fetching data:", e);
        setError("Failed to load data from the backend. Please make sure the backend server is running.");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Update active tab based on URL path
  useEffect(() => {
    if (location.pathname === '/') {
      setActiveTab('dashboard');
    } else if (location.pathname.startsWith('/models') && !location.pathname.includes('/models/')) {
      setActiveTab('models');
    } else if (location.pathname.startsWith('/projects')) {
      setActiveTab('projects');
    } else if (location.pathname.startsWith('/lineage')) {
      setActiveTab('lineage');
    }
  }, [location.pathname]);

  if (loading) {
    return (
      <div className="app-loading">
        <Spin size="large" tip="Loading data from backend..." />
        <p>Please make sure the backend server is running at http://localhost:8000</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-error">
        <Alert
          type="error"
          message="Error Loading Data"
          description={
            <>
              <p>{error}</p>
              <p>
                Please ensure the backend server is running at http://localhost:8000.
                You can start it by running:
              </p>
              <pre>cd backend && python run.py</pre>
            </>
          }
        />
      </div>
    );
  }

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    
    // Navigate to appropriate URL based on tab
    switch (key) {
      case 'dashboard':
        navigate('/');
        break;
      case 'models':
        navigate('/models');
        break;
      case 'projects':
        navigate('/projects');
        break;
      case 'lineage':
        navigate('/lineage');
        break;
    }
  };

  const renderDashboard = () => (
    <div className="dashboard-section">
      <h2>dbt Metadata Explorer</h2>
      <p>Explore your dbt projects, models, and lineage with AI-generated descriptions</p>
      
      <div className="stats-row">
        <div className="stat-card">
          <h3>Projects</h3>
          <div className="stat-value">{projects.length}</div>
        </div>
        <div className="stat-card">
          <h3>Models</h3>
          <div className="stat-value">{models.length}</div>
        </div>
        <div className="stat-card">
          <h3>Lineage Connections</h3>
          <div className="stat-value">{lineage.length}</div>
        </div>
      </div>
      
      <h3>Key Features</h3>
      <div className="feature-grid">
        <div className="feature-card">
          <h4>Dynamic Documentation</h4>
          <p>Documentation updates automatically as dbt models change</p>
        </div>
        <div className="feature-card">
          <h4>AI-Generated Descriptions</h4>
          <p>Smart descriptions generated from model code</p>
        </div>
        <div className="feature-card">
          <h4>User Corrections</h4>
          <p>Edit AI descriptions with your domain knowledge</p>
        </div>
        <div className="feature-card">
          <h4>Export Metadata</h4>
          <p>Download documentation in JSON or YAML format</p>
        </div>
      </div>
      
      <h3>Projects</h3>
      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card">
            <h4>{project.name}</h4>
            <p className="project-path">{project.path}</p>
            <p className="project-models">
              {models.filter(model => model.project === project.name).length} models
            </p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderModels = () => (
    <div className="models-section">
      <h2>Models ({models.length})</h2>
      <table className="models-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Project</th>
            <th>Description</th>
            <th>Schema</th>
            <th>Materialized</th>
          </tr>
        </thead>
        <tbody>
          {models.map(model => {
            return (
              <tr key={model.id} className="model-row">
                <td>{model.id}</td>
                <td>
                  <Link to={`/models/${model.id}`} className="model-link">
                    {model.name}
                  </Link>
                </td>
                <td>{model.project}</td>
                <td className="description-cell">
                  {model.description || <span className="no-description">No description</span>}
                </td>
                <td>{model.schema || 'N/A'}</td>
                <td>{model.materialized || 'N/A'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );

  const renderProjects = () => (
    <div className="projects-section">
      <h2>Projects ({projects.length})</h2>
      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card">
            <h3>{project.name}</h3>
            <p className="project-path">{project.path}</p>
            <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
            <p>Updated: {new Date(project.updated_at).toLocaleDateString()}</p>
            <h4>Models</h4>
            <ul className="project-models-list">
              {models
                .filter(model => model.project === project.name)
                .slice(0, 5)
                .map(model => (
                  <li key={model.id}>
                    <Link to={`/models/${model.id}`}>{model.name}</Link>
                  </li>
                ))}
              {models.filter(model => model.project === project.name).length > 5 && (
                <li>
                  <Link to={`/projects/${project.id}`}>
                    +{models.filter(model => model.project === project.name).length - 5} more...
                  </Link>
                </li>
              )}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );

  const renderLineage = () => (
    <div className="lineage-section">
      <h2>Model Lineage</h2>
      <p>Visualize the relationships between your dbt models</p>
      <div className="deduplication-notice">
        <strong>Note:</strong> Models with the same name across different projects have been combined to simplify the visualization.
      </div>
      <div className="lineage-container">
        <LineageGraph models={models} lineage={lineage} />
      </div>
      <div className="lineage-legend">
        <div className="lineage-legend-item">
          <div className="lineage-legend-color legend-selected"></div>
          <span>Selected Model</span>
        </div>
        <div className="lineage-legend-item">
          <div className="lineage-legend-color legend-connected"></div>
          <span>Connected Model</span>
        </div>
        <div className="lineage-legend-item">
          <div className="lineage-legend-color legend-regular"></div>
          <span>Unrelated Model</span>
        </div>
      </div>
      <p className="lineage-hint">Click on a model to highlight its connections. Click again to reset.</p>
    </div>
  );

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="logo">
          <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
            <DatabaseOutlined /> DBT Metadata Explorer
          </Link>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[activeTab]}
          onSelect={({ key }) => handleTabChange(key as string)}
        >
          <Menu.Item key="dashboard" icon={<DashboardOutlined />}>Dashboard</Menu.Item>
          <Menu.Item key="models" icon={<TableOutlined />}>Models</Menu.Item>
          <Menu.Item key="projects" icon={<ProjectOutlined />}>Projects</Menu.Item>
          <Menu.Item key="lineage" icon={<ApartmentOutlined />}>Lineage</Menu.Item>
        </Menu>
        <Space className="header-buttons">
          <WatcherStatusIndicator />
          <Button 
            icon={<SyncOutlined />} 
            onClick={async () => {
              try {
                await refreshMetadata();
                window.location.reload();
              } catch (error) {
                console.error('Error refreshing metadata:', error);
              }
            }}
          >
            Refresh
          </Button>
          <ExportButton />
        </Space>
      </Header>
      
      <Content className="app-content">
        {hasAIDescriptions && (
          <Alert
            type="info"
            message="AI-Generated Descriptions Available"
            description="This metadata includes AI-generated descriptions for models and columns. Look for the AI badge next to descriptions. You can edit any description to improve it."
            showIcon
            closable
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Routes>
          <Route path="/" element={renderDashboard()} />
          <Route path="/models" element={renderModels()} />
          <Route path="/models/:id" element={<ModelDetail />} />
          <Route path="/projects" element={renderProjects()} />
          <Route path="/projects/:id" element={<ModelDetail />} />
          <Route path="/lineage" element={renderLineage()} />
        </Routes>
      </Content>
      
      <Footer className="app-footer">
        <p>DBT Metadata Explorer &copy; 2023</p>
      </Footer>
    </Layout>
  );
}

export default App; 