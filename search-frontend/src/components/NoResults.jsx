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
      {/* Sad face icon with bounce and head shake animation */}
      <SentimentDissatisfiedIcon sx={{ 
        fontSize: 48, 
        color: '#888',
        animation: 'bounceAndShake 2.5s ease-in-out',
        animationFillMode: 'forwards',
        '@keyframes bounceAndShake': {
          // Bounce down animation (0-20%)
          '0%': { transform: 'translateY(-20px)' },
          '10%': { transform: 'translateY(0)' },
          '15%': { transform: 'translateY(-5px)' },
          '20%': { transform: 'translateY(0)' },
          
          // Brief pause (20-30%)
          '30%': { transform: 'translateX(0)' },
          
          // Head shake animation (30-100%)
          '35%': { transform: 'translateX(-6px) rotateY(-9deg)' },
          '45%': { transform: 'translateX(5px) rotateY(7deg)' },
          '55%': { transform: 'translateX(-3px) rotateY(-5deg)' },
          '65%': { transform: 'translateX(2px) rotateY(3deg)' },
          '75%': { transform: 'translateX(-1px) rotateY(-1deg)' },
          '85%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(0)' }
        }
      }} />
      
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
