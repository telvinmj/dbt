import React from 'react';
import { Typography, Tag, Tooltip, Empty, Card } from 'antd';
import { Link } from 'react-router-dom';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  LinkOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import { Model } from '../types';

const { Text, Title } = Typography;

interface RelatedModelsProps {
  model: Model;
  upstream: Model[];
  downstream: Model[];
}

const RelatedModels: React.FC<RelatedModelsProps> = ({ 
  model, 
  upstream, 
  downstream 
}) => {
  // Check if there are any cross-project relationships
  const hasCrossProjectUpstream = upstream.some(m => m.project !== model.project);
  const hasCrossProjectDownstream = downstream.some(m => m.project !== model.project);
  
  // Group related models by project
  const groupModelsByProject = (models: Model[]) => {
    const groups: { [key: string]: Model[] } = {};
    
    models.forEach(m => {
      if (!groups[m.project]) {
        groups[m.project] = [];
      }
      groups[m.project].push(m);
    });
    
    return groups;
  };
  
  const upstreamByProject = groupModelsByProject(upstream);
  const downstreamByProject = groupModelsByProject(downstream);
  
  // Get colors for project badges
  const getProjectColor = (projectName: string): string => {
    // Hash the project name to generate a consistent color
    const hash = projectName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      'magenta', 'red', 'volcano', 'orange', 'gold', 
      'lime', 'green', 'cyan', 'blue', 'geekblue', 'purple'
    ];
    return colors[hash % colors.length];
  };

  return (
    <div className="related-models-container">
      <Card title="Related Models" className="related-models-card">
        {/* Summary of cross-project relationships */}
        {(hasCrossProjectUpstream || hasCrossProjectDownstream) && (
          <div className="cross-project-summary">
            <Title level={5}>Cross-Project Relationships</Title>
            <div className="cross-project-tags">
              {hasCrossProjectUpstream && (
                <Tag color="blue" icon={<ArrowUpOutlined />}>
                  Upstream Dependencies from Other Projects
                </Tag>
              )}
              {hasCrossProjectDownstream && (
                <Tag color="green" icon={<ArrowDownOutlined />}>
                  Downstream Dependencies in Other Projects
                </Tag>
              )}
            </div>
          </div>
        )}
        
        {/* Upstream Models */}
        <div className="related-section">
          <Title level={5}>
            <ArrowUpOutlined /> Upstream Dependencies ({upstream.length})
          </Title>
          
          {upstream.length === 0 ? (
            <Empty 
              image={Empty.PRESENTED_IMAGE_SIMPLE} 
              description="No upstream dependencies" 
            />
          ) : (
            <div className="project-model-groups">
              {Object.entries(upstreamByProject).map(([projectName, models]) => (
                <div key={`upstream-${projectName}`} className="project-model-group">
                  {/* Show project badge if it's a different project */}
                  {projectName !== model.project && (
                    <div className="cross-project-header">
                      <Tag color={getProjectColor(projectName)} icon={<DatabaseOutlined />}>
                        {projectName}
                      </Tag>
                      <Text type="secondary">External Project</Text>
                    </div>
                  )}
                  
                  <div className="related-models-list">
                    {models.map(relatedModel => (
                      <Tooltip 
                        key={relatedModel.id} 
                        title={relatedModel.description || "No description available"}
                      >
                        <Link to={`/models/${relatedModel.id}`}>
                          <Tag 
                            className="related-model-tag"
                            icon={projectName !== model.project ? <LinkOutlined /> : null}
                            color={projectName !== model.project ? 'blue' : 'default'}
                          >
                            {relatedModel.name}
                          </Tag>
                        </Link>
                      </Tooltip>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Downstream Models */}
        <div className="related-section">
          <Title level={5}>
            <ArrowDownOutlined /> Downstream Dependencies ({downstream.length})
          </Title>
          
          {downstream.length === 0 ? (
            <Empty 
              image={Empty.PRESENTED_IMAGE_SIMPLE} 
              description="No downstream dependencies" 
            />
          ) : (
            <div className="project-model-groups">
              {Object.entries(downstreamByProject).map(([projectName, models]) => (
                <div key={`downstream-${projectName}`} className="project-model-group">
                  {/* Show project badge if it's a different project */}
                  {projectName !== model.project && (
                    <div className="cross-project-header">
                      <Tag color={getProjectColor(projectName)} icon={<DatabaseOutlined />}>
                        {projectName}
                      </Tag>
                      <Text type="secondary">External Project</Text>
                    </div>
                  )}
                  
                  <div className="related-models-list">
                    {models.map(relatedModel => (
                      <Tooltip 
                        key={relatedModel.id} 
                        title={relatedModel.description || "No description available"}
                      >
                        <Link to={`/models/${relatedModel.id}`}>
                          <Tag 
                            className="related-model-tag"
                            icon={projectName !== model.project ? <LinkOutlined /> : null}
                            color={projectName !== model.project ? 'green' : 'default'}
                          >
                            {relatedModel.name}
                          </Tag>
                        </Link>
                      </Tooltip>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default RelatedModels; 