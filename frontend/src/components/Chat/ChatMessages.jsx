import React, { useEffect, useRef } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import { formatDistanceToNow } from 'date-fns';

const MessagesContainer = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  overflowY: 'auto',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.grey[50],
}));

const MessageBubble = styled(Box)(({ theme, type }) => ({
  maxWidth: '70%',
  padding: theme.spacing(1.5),
  borderRadius: theme.spacing(2),
  marginBottom: theme.spacing(1),
  wordBreak: 'break-word',
  ...(type === 'user' ? {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    marginLeft: 'auto',
    borderBottomRightRadius: theme.spacing(0.5),
  } : {
    backgroundColor: theme.palette.background.paper,
    color: theme.palette.text.primary,
    marginRight: 'auto',
    borderBottomLeftRadius: theme.spacing(0.5),
    boxShadow: theme.shadows[1],
  }),
}));

const AgentLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.75rem',
  color: theme.palette.primary.main,
  fontWeight: 'bold',
  marginBottom: theme.spacing(0.5),
}));

const TimeStamp = styled(Typography)(({ theme }) => ({
  fontSize: '0.7rem',
  color: theme.palette.text.secondary,
  marginTop: theme.spacing(0.5),
  textAlign: 'right',
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  color: theme.palette.text.secondary,
}));

const ChatMessages = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <MessagesContainer>
      {messages.map((message) => (
        <MessageBubble key={message.id} type={message.type}>
          {message.type === 'agent' && (
            <AgentLabel variant="caption">
              {message.sender}
            </AgentLabel>
          )}
          
          <Typography variant="body1">
            {message.content}
          </Typography>
          
          <TimeStamp variant="caption">
            {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
          </TimeStamp>
        </MessageBubble>
      ))}

      {isTyping && (
        <TypingIndicator>
          <CircularProgress size={20} />
          <Typography variant="caption">Agent is typing...</Typography>
        </TypingIndicator>
      )}
      
      <div ref={messagesEndRef} />
    </MessagesContainer>
  );
};

export default ChatMessages;
