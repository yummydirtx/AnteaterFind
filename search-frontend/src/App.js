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

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) {
      return;
    }
    setLoading(true);

    try {
      const response = await fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Error searching:', error);
    }

    setLoading(false);
  };
  return (
    <ThemeProvider theme={createTheme({ palette: { mode: 'dark' } })}>
      <CssBaseline />
      <Box sx={(theme) => ({
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        width: '100%',
        backgroundImage:
          theme.palette.mode === 'light'
            ? 'linear-gradient(180deg, #CEE5FD, #FFF)'
            : `linear-gradient(#02294F, ${alpha('#090E10', 0.0)})`,
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
        <Box sx={{ marginTop: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {results.length > 0 && results.map((result, index) => (
            <Box key={index} sx={{ width: '60%', marginBottom: 2, padding: 2, backgroundColor: '#222', borderRadius: '10px' }}>
              <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ color: '#4fc3f7', textDecoration: 'none' }}>
                {result.url}
              </a>
              <p style={{ color: '#aaa' }}>Relevance Score: {result.score.toFixed(4)}</p>
            </Box>
          ))}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
