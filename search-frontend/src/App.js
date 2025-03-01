import TextField from '@mui/material/TextField';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import SearchIcon from '@mui/icons-material/Search';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { alpha } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import Collapse from '@mui/material/Collapse';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [queryTime, setQueryTime] = useState(null);
  const [totalResults, setTotalResults] = useState(0);
  const [expandedResults, setExpandedResults] = useState({});
  const [hasSearched, setHasSearched] = useState(false);
  const [lastSearchedQuery, setLastSearchedQuery] = useState('');

  const toggleExpand = (index) => {
    setExpandedResults(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleSearch = async () => {
    if (!query) {
      return;
    }
    setLoading(true);
    setExpandedResults({});
    setHasSearched(true);
    setLastSearchedQuery(query);

    try {
      const response = await fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data.results || []);
      setQueryTime(data.query_time);
      setTotalResults(data.total);
    } catch (error) {
      console.error('Error searching:', error);
    }

    setLoading(false);
  };
  
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };
  
  return (
    <ThemeProvider theme={createTheme({ palette: { mode: 'dark' } })}>
      <CssBaseline />
      <Box sx={(theme) => ({
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        width: '100%',
        minHeight: '100vh',
        backgroundImage: `linear-gradient(#02294F, ${alpha('#090E10', 0.0)})`,
        backgroundSize: '100% 200px',
        backgroundRepeat: 'no-repeat',
        textAlign: 'center',
        p: 2,
        position: 'relative',
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
      })
      }>
        <Box 
          sx={{ 
            position: 'relative', // Changed from absolute to relative
            top: 0,
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginTop: hasSearched ? '20px' : '30vh', // Using margin instead for smoother document flow
            transition: 'all 0.6s cubic-bezier(0.33, 1, 0.68, 1)',
            zIndex: 10,
          }}
        >
          <Box 
            component={'img'} 
            src="anteaterfind.png" 
            alt="Anteater Find" 
            sx={{ 
              width: hasSearched ? '20%' : '30%', 
              marginBottom: '20px',
              transition: 'all 0.6s cubic-bezier(0.33, 1, 0.68, 1)',
            }} 
          />
          <Stack 
            direction="row" 
            spacing={2} 
            sx={{ 
              width: '50%',
              transition: 'all 0.6s cubic-bezier(0.33, 1, 0.68, 1)',
            }}
          >
            <TextField 
              fullWidth
              id="outlined-basic"
              label="Search"
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              sx={{ 
                '& .MuiOutlinedInput-root': {
                  borderRadius: '20px'
                }
              }}
              slotProps={{
                input: {
                  startAdornment: (<SearchIcon sx={{marginRight: '10px'}} />)
                }
              }} 
            />
            <Button 
              variant="contained" 
              sx={{ 
                borderRadius: '20px',
                width: '150px',
              }}
              onClick={handleSearch}
            >
              Search
            </Button>
          </Stack>
        </Box>
        
        {/* Content container that appears below the search bar */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginTop: '30px', // Fixed spacing after the search bar
            opacity: hasSearched ? 1 : 0,
            transition: 'opacity 0.3s ease',
            transitionDelay: hasSearched ? '0.3s' : '0s', // Delay appearance until search bar moves
            zIndex: 5,
          }}
        >
          {loading && <CircularProgress />}
          
          {!loading && hasSearched && results.length === 0 && (
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
                No results found for "{lastSearchedQuery}"
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try using different keywords or simplifying your search query
              </Typography>
            </Box>
          )}
          
          {!loading && results.length > 0 && (
            <>
              <Box sx={{ width: '60%', textAlign: 'left', marginBottom: '20px' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Found {totalResults} documents in {queryTime ? queryTime.toFixed(4) : '0'} seconds
                </Typography>
              </Box>
              
              {results.map((result, index) => (
                <Box key={index} sx={{ 
                  width: '60%', 
                  marginBottom: 2, 
                  padding: 2, 
                  backgroundColor: '#222', 
                  borderRadius: '10px',
                  transition: 'all 0.3s ease'
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
                      onClick={() => toggleExpand(index)} 
                      size="small" 
                      sx={{ 
                        minWidth: '32px', 
                        height: '32px', 
                        p: 0,
                        transition: 'transform 0.3s ease', 
                        transform: expandedResults[index] ? 'rotate(180deg)' : 'rotate(0deg)', // Animate the rotation
                      }}
                    >
                      <ExpandMoreIcon />
                    </Button>
                  </Box>
                  <Typography color="text.secondary">
                    Relevance Score: {result.score.toFixed(4)}
                  </Typography>
                  
                  <Collapse in={expandedResults[index]} timeout={400}>
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
                          animation: expandedResults[index] ? 'fadeIn 0.5s ease' : 'none',
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
                                  animationDelay: `${i * 0.05}s`, // Staggered animation for each chip
                                  animationFillMode: 'both',
                                }}
                              />
                            ))}
                        </Box>
                      </Box>
                    )}
                  </Collapse>
                </Box>
              ))}
            </>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
