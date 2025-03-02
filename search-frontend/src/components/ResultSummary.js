import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

/**
 * ResultSummary component - Displays metrics about search results
 * Shows total number of results found and time taken to perform the search
 * 
 * @param {Object} props - Component props
 * @param {number} props.totalResults - Total number of search results
 * @param {number} props.queryTime - Time taken to execute the search query in seconds
 */
const ResultSummary = ({ totalResults, queryTime }) => {
  return (
    <Box sx={{ 
      width: '60%', 
      textAlign: 'left', 
      marginBottom: '20px',
      // Animation for smooth entry
      animation: 'slideUp 0.5s ease',
      animationFillMode: 'both',
    }}>
      <Typography variant="subtitle2" color="text.secondary">
        Found {totalResults} documents in {queryTime ? queryTime.toFixed(4) : '0'} seconds
      </Typography>
    </Box>
  );
};

export default ResultSummary;
