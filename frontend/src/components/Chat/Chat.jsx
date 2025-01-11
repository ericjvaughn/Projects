import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import { v4 as uuidv4 } from 'uuid';

import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import { supabase, messageService, subscribeToMessages } from '../../lib/supabase';

const ChatContainer = styled(Paper)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '80vh',
  maxWidth: '800px',
  margin: '2rem auto',
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
}));

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const channelId = useRef(uuidv4());

  useEffect(() => {
    // Load initial messages
    loadMessages();

    // Subscribe to new messages
    const unsubscribe = subscribeToMessages(channelId.current, (payload) => {
      if (payload.new) {
        setMessages(prev => [...prev, transformMessage(payload.new)]);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const { data, error } = await messageService.getMessages(channelId.current);
      if (error) throw error;
      
      setMessages(data.map(transformMessage));
    } catch (err) {
      setError('Failed to load messages');
      console.error('Error loading messages:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const transformMessage = (message) => ({
    id: message.id,
    content: message.response_content || message.content,
    sender: message.response_agent || 'user',
    timestamp: new Date(message.created_at),
    type: message.response_agent ? 'agent' : 'user',
    metadata: message.metadata
  });

  const handleSendMessage = async (content) => {
    if (!content.trim()) return;

    try {
      const agentMention = content.match(/@(\w+)/)?.[1];
      
      const { error } = await messageService.sendMessage({
        content,
        channelId: channelId.current,
        agentMention,
        metadata: {
          timestamp: new Date().toISOString()
        }
      });

      if (error) throw error;
    } catch (err) {
      setError('Failed to send message');
      console.error('Error sending message:', err);
    }
  };

  return (
    <ChatContainer>
      <Box p={2} bgcolor="primary.main" color="primary.contrastText">
        <Typography variant="h6">
          Multi-Agent Chat
        </Typography>
      </Box>

      <ChatMessages 
        messages={messages}
        isLoading={isLoading}
        error={error}
      />

      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </ChatContainer>
  );
};

export default Chat;
