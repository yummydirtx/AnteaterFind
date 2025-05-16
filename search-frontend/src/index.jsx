import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// console.log("index.js: Script loaded");

const root = ReactDOM.createRoot(document.getElementById('root'));
// console.log("index.js: Root created, attempting to render App");
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
// console.log("index.js: App render call complete");

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(// console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
