import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const ResultSummary = ({ totalResults, queryTime }) => {
  return (
    <Box sx={{ 
      width: '60%', 
      textAlign: 'left', 
      marginBottom: '20px',
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
