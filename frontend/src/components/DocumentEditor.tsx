import React, { useState, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import { Alert, Button, Space, Spin } from 'antd';

interface DocumentEditorProps {
  documentId: string;
  initialContent: string;
  onSave: (content: string) => Promise<void>;
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({
  documentId,
  initialContent,
  onSave,
}) => {
  const [content, setContent] = useState(initialContent);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    try {
      setSaving(true);
      await onSave(content);
      setError(null);
    } catch (err) {
      setError('Failed to save document');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="document-editor">
      {error && <Alert type="error" message={error} closable />}
      
      <Editor
        height="70vh"
        defaultLanguage="markdown"
        value={content}
        onChange={(value) => setContent(value || '')}
        options={{
          minimap: { enabled: false },
          lineNumbers: 'on',
          wordWrap: 'on',
          contextmenu: true,
        }}
      />
      
      <Space className="editor-actions">
        <Button
          type="primary"
          onClick={handleSave}
          loading={saving}
        >
          Save Document
        </Button>
      </Space>
    </div>
  );
};

export default DocumentEditor; 