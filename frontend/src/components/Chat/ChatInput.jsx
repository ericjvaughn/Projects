import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  InputAdornment,
  Tooltip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import AlternateEmailIcon from '@mui/icons-material/AlternateEmail';

const InputContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(3),
  },
}));

let typingTimeout = null;

const ChatInput = ({ onSendMessage, onTyping, disabled }) => {
  const [message, setMessage] = useState('');
  const [mentionMode, setMentionMode] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (typingTimeout) {
        clearTimeout(typingTimeout);
      }
    };
  }, []);

  const handleTyping = () => {
    onTyping(true);
    
    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }
    
    typingTimeout = setTimeout(() => {
      onTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === '@') {
      setMentionMode(true);
    } else if (mentionMode && e.key === ' ') {
      setMentionMode(false);
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
      setMentionMode(false);
      if (typingTimeout) {
        clearTimeout(typingTimeout);
        onTyping(false);
      }
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
    handleTyping();
  };

  return (
    <InputContainer>
      <StyledTextField
        ref={inputRef}
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        disabled={disabled}
        placeholder="Type your message... Use @ to mention specific agents"
        variant="outlined"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <Tooltip title="Mention agent (@)">
                <IconButton
                  onClick={() => {
                    setMentionMode(true);
                    inputRef.current?.focus();
                    setMessage(prev => prev + '@');
                  }}
                  edge="end"
                >
                  <AlternateEmailIcon />
                </IconButton>
              </Tooltip>
              <IconButton
                onClick={handleSend}
                disabled={!message.trim() || disabled}
                color="primary"
                edge="end"
              >
                <SendIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          backgroundColor: mentionMode ? 'action.hover' : 'transparent',
        }}
      />
    </InputContainer>
  );
};

export default ChatInput;
