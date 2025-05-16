/**
 * Components barrel file
 * 
 * This file exports all component modules from a single location,
 * allowing for cleaner imports in other files.
 * 
 * Example: import { SearchBar, NoResults } from './components';
 * Instead of: import SearchBar from './components/SearchBar';
 *            import NoResults from './components/NoResults';
 */

export { default as SearchBar } from './SearchBar';
export { default as ResultSummary } from './ResultSummary';
export { default as NoResults } from './NoResults';
export { default as SearchResult } from './SearchResult';
