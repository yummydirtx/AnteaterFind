import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';

const NoResults = ({ query }) => {
  return (
    <Box sx={{ 
      width: '60%', 
      padding: 3,
      borderRadius: '10px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 2
    }}>
      <SentimentDissatisfiedIcon sx={{ fontSize: 48, color: '#888' }} />
      <Typography variant="h6" color="text.secondary">
        No results found for "{query}"
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Try using different keywords or simplifying your search query
      </Typography>
    </Box>
  );
};

export default NoResults;
