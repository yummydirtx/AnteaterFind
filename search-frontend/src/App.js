import TextField from '@mui/material/TextField';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import SearchIcon from '@mui/icons-material/Search';

function App() {
  return (
    <ThemeProvider theme={createTheme({ palette: { mode: 'dark' } })}>
      <CssBaseline />
      <Box sx={(theme) => ({
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        textAlign: 'center',
        p: 2,
      })
      }>
        <Stack direction="row" spacing={2} sx={{ width: '80%', margin: '0 auto' }}>
          <TextField 
          fullWidth
          id="outlined-basic"
          label="Search"
          variant="outlined"
          sx={{ 
            '& .MuiOutlinedInput-root': {
              borderRadius: '20px'
            }
          }}
          slotProps={{
            input: {
              startAdornment: (<SearchIcon />)
            }
          }} />
        </Stack>
      </Box>
    </ThemeProvider>
  );
}

export default App;
