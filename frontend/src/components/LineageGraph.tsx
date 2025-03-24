import React, { useEffect, useState, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  NodeMouseHandler,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useNavigate } from 'react-router-dom';

interface LineageLink {
  source: string;
  target: string;
}

interface Model {
  id: string;
  name: string;
  project: string;
  description?: string | null;
  originalModels?: Model[];
}

interface LineageGraphProps {
  models: Model[];
  lineage: LineageLink[];
}

const nodeWidth = 200;
const nodeHeight = 60;

const LineageGraph: React.FC<LineageGraphProps> = ({ models, lineage }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
  const navigate = useNavigate();

  // Create deduplicated models based on model name AND project
  const { deduplicatedModels, modelMap, deduplicatedLineage } = useMemo(() => {
    // First, let's create a map to group models by name AND project
    const modelsByNameAndProject: Record<string, Model[]> = {};
    
    // Group models by name and project
    models.forEach(model => {
      if (!model.name || !model.project) return;
      
      const key = `${model.name}_${model.project}`;
      if (!modelsByNameAndProject[key]) {
        modelsByNameAndProject[key] = [];
      }
      modelsByNameAndProject[key].push(model);
    });

    // Create deduplicated models list
    const dedupedModels: Model[] = [];
    const modelIdMap: Record<string, string> = {}; // Maps original IDs to new IDs
    
    // For each unique model name & project combo, create one consolidated model
    Object.entries(modelsByNameAndProject).forEach(([key, modelsWithNameAndProject], index) => {
      // Create a consolidated model from the first model with this name and project
      const baseModel = modelsWithNameAndProject[0];
      const deduplicatedId = `dedupe_${index}`;
      
      const consolidatedModel: Model = {
        ...baseModel,
        id: deduplicatedId,
        // Store original models for reference
        originalModels: modelsWithNameAndProject
      };
      
      dedupedModels.push(consolidatedModel);
      
      // Map all original IDs to the new consolidated ID
      modelsWithNameAndProject.forEach(model => {
        if (model.id) {
          modelIdMap[model.id] = deduplicatedId;
        }
      });
    });
    
    // Deduplicate lineage connections
    const seenConnections = new Set<string>();
    const dedupedLineage: LineageLink[] = [];
    
    lineage.forEach(link => {
      if (!link.source || !link.target) return;
      
      const sourceId = modelIdMap[link.source];
      const targetId = modelIdMap[link.target];
      
      if (!sourceId || !targetId) return;
      
      // Skip if sourceId and targetId are the same (self-reference after deduplication)
      if (sourceId === targetId) return;
      
      const connectionKey = `${sourceId}-${targetId}`;
      
      // Only add if we haven't seen this connection before
      if (!seenConnections.has(connectionKey)) {
        seenConnections.add(connectionKey);
        dedupedLineage.push({
          source: sourceId,
          target: targetId
        });
      }
    });
    
    return { 
      deduplicatedModels: dedupedModels, 
      modelMap: modelIdMap,
      deduplicatedLineage: dedupedLineage
    };
  }, [models, lineage]);

  // Function to highlight a model and its connections
  const highlightModelConnections = (modelId: string | null) => {
    if (!modelId) {
      // Reset all highlights if no model is selected
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          style: {
            ...node.style,
            background: '#fff',
            border: '1px solid #ddd',
            boxShadow: 'none',
          },
        }))
      );
      
      setEdges((eds) =>
        eds.map((edge) => ({
          ...edge,
          style: { stroke: '#aaa' },
          animated: false,
        }))
      );
      return;
    }

    // Find all connected edges (upstream and downstream)
    const connectedEdges = deduplicatedLineage.filter(
      (link) => link.source === modelId || link.target === modelId
    );
    
    const connectedNodeIds = new Set<string>();
    connectedNodeIds.add(modelId); // Add the selected node itself
    
    // Add all nodes connected by edges
    connectedEdges.forEach((edge) => {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    });

    // Update node styles
    setNodes((nds) =>
      nds.map((node) => {
        const isSelected = node.id === modelId;
        const isConnected = connectedNodeIds.has(node.id);
        
        return {
          ...node,
          style: {
            ...node.style,
            background: isSelected ? '#e6f7ff' : isConnected ? '#f0f9ff' : '#fff',
            border: isSelected ? '2px solid #1890ff' : isConnected ? '1px solid #69c0ff' : '1px solid #ddd',
            boxShadow: isSelected ? '0 0 10px #1890ff' : isConnected ? '0 0 5px rgba(24, 144, 255, 0.3)' : 'none',
            opacity: isConnected || isSelected ? 1 : 0.5,
          },
        };
      })
    );

    // Update edge styles
    setEdges((eds) =>
      eds.map((edge) => {
        const isConnected = 
          edge.source === modelId || 
          edge.target === modelId;
        
        return {
          ...edge,
          style: { 
            stroke: isConnected ? '#1890ff' : '#aaa',
            strokeWidth: isConnected ? 2 : 1,
          },
          animated: isConnected,
          opacity: isConnected ? 1 : 0.3,
        };
      })
    );
  };

  // Handle node click
  const onNodeClick: NodeMouseHandler = (_, node) => {
    // Find the original model for this deduplicated node
    const deduplicatedModel = deduplicatedModels.find(model => model.id === node.id);
    if (deduplicatedModel?.originalModels && deduplicatedModel.originalModels.length > 0) {
      // Navigate to the first original model's detail page
      const originalModelId = deduplicatedModel.originalModels[0].id;
      navigate(`/models/${originalModelId}`);
    }
  };

  // Handle node hover to highlight connections
  const onNodeMouseEnter: NodeMouseHandler = (_, node) => {
    setSelectedModelId(node.id);
    highlightModelConnections(node.id);
  };

  const onNodeMouseLeave: NodeMouseHandler = () => {
    setSelectedModelId(null);
    highlightModelConnections(null);
  };

  // Click on the background to clear selection
  const onPaneClick = () => {
    setSelectedModelId(null);
    highlightModelConnections(null);
  };

  useEffect(() => {
    if (!deduplicatedModels || deduplicatedModels.length === 0) {
      console.log("No deduplicated models available");
      return;
    }
    
    // Create nodes from the models
    const flowNodes: Node[] = [];
    const modelLevels: Record<string, number> = {};
    
    // Process lineage to create a directed graph and calculate levels
    if (deduplicatedLineage && deduplicatedLineage.length > 0) {
      // Initialize levels for all models
      deduplicatedModels.forEach(model => {
        modelLevels[model.id] = -1; // -1 means not assigned yet
      });
      
      // Find source models (no incoming edges)
      const incomingEdges: Record<string, number> = {};
    deduplicatedLineage.forEach(link => {
        if (!incomingEdges[link.target]) {
          incomingEdges[link.target] = 0;
        }
        incomingEdges[link.target]++;
      });
      
      // Source models are those with no incoming edges
      const sourceModelIds = deduplicatedModels
        .filter(model => !incomingEdges[model.id])
        .map(model => model.id);
      
      // Assign level 0 to source models
      sourceModelIds.forEach(id => {
        modelLevels[id] = 0;
      });
      
      // Breadth-first traversal to assign levels
      let frontier = [...sourceModelIds];
    let currentLevel = 0;
      
      while (frontier.length > 0) {
        const nextFrontier: string[] = [];
        
        frontier.forEach(sourceId => {
          // Find all targets from this source
          deduplicatedLineage
            .filter(link => link.source === sourceId)
            .forEach(link => {
              // Assign level to target if it's not assigned yet or if it's a higher level
              const targetLevel = modelLevels[link.target];
              if (targetLevel === -1 || targetLevel < currentLevel + 1) {
                modelLevels[link.target] = currentLevel + 1;
                nextFrontier.push(link.target);
              }
            });
        });
        
        frontier = nextFrontier;
        currentLevel++;
      }
      
      // Assign level 0 to any unassigned models (isolated nodes)
      deduplicatedModels.forEach(model => {
        if (modelLevels[model.id] === -1) {
          modelLevels[model.id] = 0;
        }
      });
    } else {
      // If no lineage, all models are on level 0
      deduplicatedModels.forEach(model => {
        modelLevels[model.id] = 0;
      });
    }
    
    // Count models per level for positioning
    const modelsPerLevel: Record<number, number> = {};
    const modelPositionInLevel: Record<string, number> = {};
    
    // Count how many models are in each level
    Object.entries(modelLevels).forEach(([modelId, level]) => {
      if (!modelsPerLevel[level]) {
        modelsPerLevel[level] = 0;
      }
      modelPositionInLevel[modelId] = modelsPerLevel[level];
      modelsPerLevel[level]++;
    });
    
    // Create nodes with positions
    deduplicatedModels.forEach(model => {
      const level = modelLevels[model.id];
      const positionInLevel = modelPositionInLevel[model.id];
      const maxInLevel = modelsPerLevel[level];
      
      // Position nodes in a grid layout
      const xGap = Math.max(nodeWidth + 50, 250);
      const yGap = Math.max(nodeHeight + 100, 150);
      
      // Calculate x based on level and maxInLevel to center nodes
      const levelWidth = maxInLevel * xGap;
      const startX = -(levelWidth / 2) + (xGap / 2);
      
      const x = startX + (positionInLevel * xGap);
      const y = level * yGap;
      
      flowNodes.push({
      id: model.id,
        position: { x, y },
      data: { 
        label: (
            <div style={{ padding: '5px' }}>
              <div style={{ fontWeight: 'bold', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {model.name}
              </div>
              <div style={{ fontSize: '0.8em', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {model.project}
              </div>
          </div>
          ),
          model
      },
      style: {
        background: '#fff',
        border: '1px solid #ddd',
        borderRadius: '5px',
          width: nodeWidth,
          cursor: 'pointer',
        },
      });
    });
    
    setNodes(flowNodes);
    
    // Create edges
    const flowEdges: Edge[] = deduplicatedLineage.map((link, index) => ({
      id: `${link.source}-${link.target}`,
        source: link.source,
        target: link.target,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#aaa' },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 15,
        height: 15,
        color: '#aaa',
      },
      label: 'references',
      labelStyle: { fill: '#888', fontSize: 12 },
      labelBgStyle: { fill: 'rgba(255, 255, 255, 0.7)' },
    }));
    
    setEdges(flowEdges);
  }, [deduplicatedModels, deduplicatedLineage, navigate]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onNodeMouseEnter={onNodeMouseEnter}
        onNodeMouseLeave={onNodeMouseLeave}
        onPaneClick={onPaneClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Controls />
        <MiniMap />
        <Background color="#f8f8f8" gap={16} />
      </ReactFlow>
    </div>
  );
};

export default LineageGraph; 