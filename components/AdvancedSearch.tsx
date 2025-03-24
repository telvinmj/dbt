          <Form.Item name="search" style={{ marginBottom: expandedSearch ? 24 : 0 }}>
            <Tooltip title="Only models with EXACTLY matching name will be shown - no description searching">
              <Input 
                placeholder="Type EXACT model name to search..." 
                prefix={<SearchOutlined />}
                onChange={handleQuickSearch}
                allowClear
                addonAfter={<span style={{ fontSize: '11px', color: '#888' }}>Exact Name Only</span>}
              />
            </Tooltip>
          </Form.Item> 