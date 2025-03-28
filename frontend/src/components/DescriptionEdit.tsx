import React, { useState } from 'react';
import { Typography, Button, Input, Form, Tag, Space, Tooltip, Modal } from 'antd';
import { EditOutlined, SaveOutlined, CloseOutlined, RobotOutlined, UserOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { createUserCorrection } from '../services/api';

const { Paragraph, Text } = Typography;
const { TextArea } = Input;

interface DescriptionEditProps {
  entityType: 'model' | 'column';
  entityId: string;
  description: string | null;
  aiDescription: string | null;
  userEdited?: boolean;
  onDescriptionUpdated: () => void;
}

const DescriptionEdit: React.FC<DescriptionEditProps> = ({
  entityType,
  entityId,
  description,
  aiDescription,
  userEdited = false,
  onDescriptionUpdated,
}) => {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [showAIInfo, setShowAIInfo] = useState<boolean>(false);
  const [form] = Form.useForm();

  const handleEdit = () => {
    form.setFieldsValue({ description: description || aiDescription || '' });
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await createUserCorrection(
        entityType,
        entityId,
        values.description
      );
      setIsEditing(false);
      onDescriptionUpdated();
    } catch (error) {
      console.error('Error saving description:', error);
    }
  };

  // Determine what description to show and its source
  const isAI = !userEdited && aiDescription;
  const isUserEdited = userEdited;
  const displayDescription = (description && description !== "") ? description : (aiDescription || 'No description available');

  // Information modal about AI-generated descriptions
  const showAIInfoModal = () => {
    setShowAIInfo(true);
  };

  const handleAIInfoClose = () => {
    setShowAIInfo(false);
  };

  const useAIDescription = () => {
    if (aiDescription) {
      form.setFieldsValue({ description: aiDescription });
      setIsEditing(true);
    }
  };

  return (
    <div className="description-block">
      <div className="description-header">
        <Text strong>Description:</Text>
        {isAI && (
          <Tooltip title="This description was generated by AI">
            <Tag color="blue" icon={<RobotOutlined />} onClick={showAIInfoModal} style={{ cursor: 'pointer' }}>
              AI Generated
            </Tag>
          </Tooltip>
        )}
        {isUserEdited && (
          <Tag color="green" icon={<UserOutlined />}>
            User Edited
          </Tag>
        )}
        <Space>
          {!isEditing && (
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={handleEdit}
              size="small"
            >
              Edit
            </Button>
          )}
          {aiDescription && !isEditing && description !== aiDescription && (
            <Button
              type="link"
              icon={<RobotOutlined />}
              onClick={useAIDescription}
              size="small"
            >
              Use AI Version
            </Button>
          )}
          {isAI && (
            <Button
              type="text"
              icon={<QuestionCircleOutlined />} 
              size="small"
              onClick={showAIInfoModal}
            />
          )}
        </Space>
      </div>

      {!isEditing ? (
        <Paragraph>{displayDescription}</Paragraph>
      ) : (
        <Form form={form} layout="vertical" className="description-edit-form">
          <Form.Item
            name="description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSave}
              >
                Save
              </Button>
              <Button icon={<CloseOutlined />} onClick={handleCancel}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      )}
      
      {/* AI Information Modal */}
      <Modal
        title="AI-Generated Description"
        open={showAIInfo}
        onCancel={handleAIInfoClose}
        footer={[
          <Button key="close" onClick={handleAIInfoClose}>
            Close
          </Button>
        ]}
      >
        <p>This description was automatically generated by AI based on:</p>
        <ul>
          <li>Column/model name</li>
          <li>Data type information</li>
          <li>SQL code used in the model</li>
          <li>Context from related models</li>
        </ul>
        <p>
          You can edit this description to improve it. Your edits will be saved and will replace the AI-generated description.
        </p>
      </Modal>
    </div>
  );
};

export default DescriptionEdit; 