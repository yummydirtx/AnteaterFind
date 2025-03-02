import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Chip from '@mui/material/Chip';

const SearchResult = ({ result, index, isExpanded, onToggleExpand }) => {
  return (
    <Box sx={{ 
      width: '60%', 
      marginBottom: 2, 
      padding: 2, 
      backgroundColor: '#222', 
      borderRadius: '10px',
      transition: 'all 0.3s ease',
      animation: 'slideUp 0.6s ease',
      animationFillMode: 'both',
      animationDelay: `${index * 0.12}s`,
      opacity: 0,
      transform: 'translateY(50px)',
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ 
          color: '#4fc3f7', 
          textDecoration: 'none',
          flex: 1
        }}>
          {result.url}
        </a>
        <Button 
          onClick={onToggleExpand} 
          size="small" 
          sx={{ 
            minWidth: '32px', 
            height: '32px', 
            p: 0,
            transition: 'transform 0.3s ease', 
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          <ExpandMoreIcon />
        </Button>
      </Box>
      <Typography color="text.secondary">
        Relevance Score: {result.score.toFixed(4)}
      </Typography>
      
      <Collapse in={isExpanded} timeout={400}>
        {result.tf_idf_info && (
          <Box 
            sx={{ 
              mt: 2, 
              backgroundColor: 'rgba(0,0,0,0.2)', 
              p: 1.5, 
              borderRadius: '8px',
              overflow: 'hidden',
            }}
          >
            <Typography variant="subtitle2" gutterBottom sx={{
              animation: isExpanded ? 'fadeIn 0.5s ease' : 'none',
            }}>
              TF-IDF Information:
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 1,
              '@keyframes slideIn': {
                from: { opacity: 0, transform: 'translateY(-10px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
              }
            }}>
              {Object.entries(result.tf_idf_info)
                .sort((a, b) => b[1] - a[1])
                .map(([term, value], i) => (
                  <Chip 
                    key={i} 
                    label={`${term}: ${value.toFixed(4)}`} 
                    size="small" 
                    sx={{ 
                      backgroundColor: `rgba(79, 195, 247, ${Math.min(value * 0.5, 0.8)})`,
                      '& .MuiChip-label': { fontSize: '0.7rem' },
                      animation: 'slideIn 0.4s ease',
                      animationDelay: `${i * 0.05}s`,
                      animationFillMode: 'both',
                    }}
                  />
                ))}
            </Box>
          </Box>
        )}
      </Collapse>
    </Box>
  );
};

export default SearchResult;
