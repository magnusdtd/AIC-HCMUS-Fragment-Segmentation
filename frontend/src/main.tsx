import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.js'
import { UserProvider } from './context/UserContext.js';

const rootElement = document.getElementById('root');
if (rootElement) {
    createRoot(rootElement).render(
        <StrictMode>
            <UserProvider>
                <App />
            </UserProvider>
        </StrictMode>
    );
} else {
    console.error("Root element not found");
}