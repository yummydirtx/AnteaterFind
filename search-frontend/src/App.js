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
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [queryTime, setQueryTime] = useState(null);
  const [totalResults, setTotalResults] = useState(0);
  const [expandedResults, setExpandedResults] = useState({});

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
        backgroundImage: `linear-gradient(#02294F, ${alpha('#090E10', 0.0)})`,
        backgroundSize: '100% 200px',
        backgroundRepeat: 'no-repeat',
        textAlign: 'center',
        p: 2,
      })
      }>
        <Box component={'img'} src="anteaterfind.png" alt="Anteater Find" sx={{ width: '30%', 
          margin: '0 auto', 
          marginBottom: '10px',
          marginTop: '50px' }} />
        <Stack direction="row" spacing={2} sx={{ width: '60%', margin: '0 auto' }}>
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
          }} />
          <Button variant="contained" sx={{ 
            borderRadius: '20px',
            width: '150px',
          }}
          onClick={handleSearch}>
            Search
          </Button>
        </Stack>
        {loading && <CircularProgress sx={{ marginTop: 2 }} />}
        
        {!loading && results.length > 0 && (
          <Box sx={{ width: '60%', margin: '20px auto 0', textAlign: 'left' }}>
            <Typography variant="subtitle2" color="text.secondary">
              Found {totalResults} documents in {queryTime ? queryTime.toFixed(4) : '0'} seconds
            </Typography>
          </Box>
        )}
        
        <Box sx={{ marginTop: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {results.length > 0 && results.map((result, index) => (
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
                  sx={{ minWidth: '32px', height: '32px', p: 0 }}
                >
                  {expandedResults[index] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </Button>
              </Box>
              <Typography color="text.secondary">
                Relevance Score: {result.score.toFixed(4)}
              </Typography>
              
              {expandedResults[index] && result.tf_idf_info && (
                <Box sx={{ mt: 2, backgroundColor: 'rgba(0,0,0,0.2)', p: 1.5, borderRadius: '8px' }}>
                  <Typography variant="subtitle2" gutterBottom>TF-IDF Information:</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {Object.entries(result.tf_idf_info)
                      .sort((a, b) => b[1] - a[1])
                      .map(([term, value], i) => (
                        <Chip 
                          key={i} 
                          label={`${term}: ${value.toFixed(4)}`} 
                          size="small" 
                          sx={{ 
                            backgroundColor: `rgba(79, 195, 247, ${Math.min(value * 0.5, 0.8)})`,
                            '& .MuiChip-label': { fontSize: '0.7rem' }
                          }}
                        />
                      ))}
                  </Box>
                </Box>
              )}
            </Box>
          ))}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
