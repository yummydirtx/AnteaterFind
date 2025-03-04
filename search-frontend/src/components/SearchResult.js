import React, { useState, useEffect, useCallback } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Chip from '@mui/material/Chip';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

/**
 * SearchResult component - Displays a single search result with expandable details
 * 
 * @param {Object} props - Component props
 * @param {Object} props.result - The search result data object
 * @param {number} props.index - The index of this result in the results array
 * @param {boolean} props.isExpanded - Whether the result details are expanded
 * @param {Function} props.onToggleExpand - Function to toggle expanded state
 */
const SearchResult = ({ result, index, isExpanded, onToggleExpand }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [summary, setSummary] = useState('');
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState(null);

  // Function to fetch summary from backend wrapped in useCallback
  const fetchSummary = useCallback(async () => {
    setIsLoadingSummary(true);
    setSummaryError(null);
    
    try {
      const response = await fetch(`http://127.0.0.1:5000/summary?id=${encodeURIComponent(result.doc_id)}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching summary: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSummary(data.summary || "No summary available");
    } catch (error) {
      console.error("Failed to fetch summary:", error);
      setSummaryError(error.message);
    } finally {
      setIsLoadingSummary(false);
    }
  }, [result.doc_id]);

  // Fetch summary from backend when component is expanded
  useEffect(() => {
    if (isExpanded && result.doc_id && !summary && !isLoadingSummary) {
      fetchSummary();
    }
  }, [isExpanded, result.doc_id, summary, isLoadingSummary, fetchSummary]);

  return (
    <Box sx={{ 
      width: isMobile ? '90%' : '60%', 
      marginBottom: 2, 
      padding: 2, 
      backgroundColor: '#222', 
      borderRadius: '10px',
      transition: 'all 0.3s ease',
      // Staggered animation for results list
      animation: 'slideUp 0.6s ease',
      animationFillMode: 'both',
      animationDelay: `${index * 0.12}s`,
      opacity: 0,
      transform: 'translateY(50px)',
    }}>
      {/* URL and expand button header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {/* Result URL as a link with mobile-responsive truncation */}
        <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ 
          color: '#4fc3f7', 
          textDecoration: 'none',
          flex: 1,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {result.url}
        </a>
        
        {/* Expand/collapse toggle button */}
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
      
      {/* Relevance score display */}
      <Typography color="text.secondary">
        Relevance Score: {result.score.toFixed(4)}
      </Typography>
      
      {/* Expandable section with TF-IDF details */}
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
            {/* Section header */}
            <Typography variant="subtitle2" gutterBottom sx={{
              animation: isExpanded ? 'fadeIn 0.5s ease' : 'none',
            }}>
              TF-IDF Information:
            </Typography>
            
            {/* Container for TF-IDF term chips */}
            <Box sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 1,
              '@keyframes slideIn': {
                from: { opacity: 0, transform: 'translateY(-10px)' },
                to: { opacity: 1, transform: 'translateY(0)' }
              }
            }}>
              {/* Sort terms by value and display as chips */}
              {Object.entries(result.tf_idf_info)
                .sort((a, b) => b[1] - a[1])
                .map(([term, value], i) => (
                  <Chip 
                    key={i} 
                    label={`${term}: ${value.toFixed(4)}`} 
                    size="small" 
                    sx={{ 
                      // Color intensity based on TF-IDF value
                      backgroundColor: `rgba(79, 195, 247, ${Math.min(value * 0.5, 0.8)})`,
                      '& .MuiChip-label': { fontSize: '0.7rem' },
                      // Staggered animation for chips
                      animation: 'slideIn 0.4s ease',
                      animationDelay: `${i * 0.05}s`,
                      animationFillMode: 'both',
                    }}
                  />
                ))}
            </Box>
          </Box>
        )}
        
        {/* Summary Section */}
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
            Summary:
          </Typography>
          
          {isLoadingSummary ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} sx={{ color: '#4fc3f7' }} />
            </Box>
          ) : summaryError ? (
            <Alert severity="error" sx={{ mt: 1, backgroundColor: 'rgba(211, 47, 47, 0.1)' }}>
              {summaryError}
            </Alert>
          ) : (
            <Typography variant="body2" sx={{ 
              color: '#ddd',
              lineHeight: 1.5,
              animation: 'fadeIn 0.5s ease',
            }}>
              {summary}
            </Typography>
          )}
        </Box>
      </Collapse>
    </Box>
  );
};

export default SearchResult;
