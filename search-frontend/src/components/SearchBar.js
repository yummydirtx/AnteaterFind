import React from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import SearchIcon from '@mui/icons-material/Search';

/**
 * SearchBar component - Displays the search logo and input field
 * 
 * @param {Object} props - Component props
 * @param {string} props.query - Current search query value
 * @param {Function} props.setQuery - Function to update search query
 * @param {Function} props.handleSearch - Function to trigger search
 * @param {boolean} props.hasSearched - Whether a search has been performed
 */
const SearchBar = ({ query, setQuery, handleSearch, hasSearched }) => {
  /**
   * Handles Enter key press to trigger search
   * @param {Object} event - Keyboard event
   */
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box 
      sx={{ 
        position: 'relative',
        top: 0,
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        // Adjust position based on search state
        marginTop: hasSearched ? '20px' : '30vh',
        transition: 'all 0.6s cubic-bezier(0.33, 1, 0.68, 1)',
        zIndex: 10,
      }}
    >
      {/* Logo - resizes when search is performed */}
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

      {/* Search input and button container */}
      <Stack 
        direction="row" 
        spacing={2} 
        sx={{ 
          width: '50%',
          transition: 'all 0.6s cubic-bezier(0.33, 1, 0.68, 1)',
        }}
      >
        {/* Search input field */}
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

        {/* Search button */}
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
  );
};

export default SearchBar;
