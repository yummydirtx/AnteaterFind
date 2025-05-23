import React, { useState, useCallback } from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { alpha } from '@mui/material';
import Button from '@mui/material/Button';

import { SearchBar, ResultSummary, NoResults, SearchResult, Footer } from './components';

/**
 * Main application component that manages the search interface
 * Handles state management and data fetching for the search functionality
 */
function App() {
  // console.log("App.js: App component function started");
  // State for search query and results
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false); // Added state for loading more results
  const [queryTime, setQueryTime] = useState(null);
  const [totalResults, setTotalResults] = useState(0);
  const [expandedResults, setExpandedResults] = useState({});
  const [hasSearched, setHasSearched] = useState(false);
  const [lastSearchedQuery, setLastSearchedQuery] = useState('');
  const [currentOffset, setCurrentOffset] = useState(0); // Added state for current offset
  const resultsPerPage = 5; // Define how many results to load each time

  /**
   * Toggles the expanded/collapsed state of a search result
   * @param {number} index - The index of the result to toggle
   */
  const toggleExpand = (index) => {
    setExpandedResults(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  /**
   * Performs search by calling the backend API
   * Updates results state with the search response data
   */
  const handleSearch = useCallback(async (isLoadMore = false) => { // Added isLoadMore parameter
    if (!query) {
      // console.log("App.js: handleSearch - query is empty, returning");
      return;
    }

    if (isLoadMore) {
      setLoadingMore(true);
    } else {
      setLoading(true);
      setResults([]); // Reset results for a new search
      setCurrentOffset(0); // Reset offset for a new search
      setExpandedResults({});
      setHasSearched(true);
      setLastSearchedQuery(query);
    }

    try {
      // Adjust API call to include offset and limit
      const response = await fetch(`https://api.anteaterfind.com/search?q=${encodeURIComponent(query)}&offset=${isLoadMore ? currentOffset + resultsPerPage : 0}&limit=${resultsPerPage}`);
      const data = await response.json();
      
      if (isLoadMore) {
        setResults(prevResults => [...prevResults, ...(data.results || [])]);
        setCurrentOffset(prevOffset => prevOffset + resultsPerPage);
      } else {
        setResults(data.results || []);
        setQueryTime(data.query_time);
        setTotalResults(data.total);
      }
    } catch (error) {
      console.error('Error searching:', error);
    }

    if (isLoadMore) {
      setLoadingMore(false);
    } else {
      setLoading(false);
    }
  }, [query, currentOffset]); // Added currentOffset to dependencies
  
  // console.log("App.js: Before return statement");
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
        '@keyframes slideUp': {
          from: { opacity: 0, transform: 'translateY(50px)' },
          to: { opacity: 1, transform: 'translateY(0)' }
        },
      })}
      >
        {/* Search interface component */}
        <SearchBar
          query={query} 
          setQuery={setQuery} 
          handleSearch={handleSearch} 
          hasSearched={hasSearched} 
        />
        
        {/* Results container - only visible after search */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginTop: '30px',
            opacity: hasSearched ? 1 : 0,
            transition: 'opacity 0.3s ease',
            transitionDelay: hasSearched ? '0.3s' : '0s',
            zIndex: 5,
          }}
        >
          {/* Loading indicator */}
          {loading && <CircularProgress />}
          
          {/* No results message */}
          {!loading && hasSearched && results.length === 0 && (
            <NoResults query={lastSearchedQuery} />
          )}
          
          {/* Search results section */}
          {!loading && results.length > 0 && (
            <>
              <ResultSummary totalResults={totalResults} queryTime={queryTime} />
              
              {/* Map through results array to display each result */}
              {results.map((result, index) => (
                <SearchResult 
                  key={`${result.doc_id}-${index}`}
                  result={result}
                  index={index}
                  isExpanded={!!expandedResults[index]}
                  onToggleExpand={() => toggleExpand(index)}
                />
              ))}

              {/* Load More Button */}
              {results.length < totalResults && (
                <Button 
                  onClick={() => handleSearch(true)} 
                  disabled={loadingMore} 
                  sx={{
                    marginTop: 2,
                    // Apply the same animation as search results
                    animation: 'slideUp 0.6s ease',
                    animationFillMode: 'both',
                    // Delay slightly more than the last result to appear after them
                    animationDelay: `${results.length * 0.12 + 0.1}s`,
                    opacity: 0, // Start with opacity 0 for the animation
                    transform: 'translateY(50px)', // Start transformed for the animation
                  }}
                >
                  {loadingMore ? <CircularProgress size={24} /> : 'Load More'}
                </Button>
              )}
            </>
          )}
        </Box>
      </Box>
      <Footer />
    </ThemeProvider>
  );
}

export default App;
