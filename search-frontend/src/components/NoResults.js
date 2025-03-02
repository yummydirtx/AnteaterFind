import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

/**
 * NoResults component - Displayed when search yields no results
 * Shows a user-friendly message with the search query and suggestions
 * 
 * @param {Object} props - Component props
 * @param {string} props.query - The search query that yielded no results
 */
const NoResults = ({ query }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  return (
    <Box sx={{ 
      width: isMobile ? '90%' : '60%', 
      padding: 3,
      borderRadius: '10px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 2
    }}>
      {/* Sad face icon */}
      <SentimentDissatisfiedIcon sx={{ fontSize: 48, color: '#888' }} />
      
      {/* No results message with the search query */}
      <Typography variant="h6" color="text.secondary" align="center">
        No results found for "{query}"
      </Typography>
      
      {/* Helpful suggestion for the user */}
      <Typography variant="body2" color="text.secondary" align="center">
        Try using different keywords or simplifying your search query
      </Typography>
    </Box>
  );
};

export default NoResults;
