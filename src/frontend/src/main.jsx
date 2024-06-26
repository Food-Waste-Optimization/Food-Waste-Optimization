import React from 'react'
import ReactDOM from 'react-dom/client'
import { PublicClientApplication, EventType } from '@azure/msal-browser'
import { msalConfig } from './utils/authConfig'
import { BrowserRouter as Router } from "react-router-dom"
import App from './App.jsx'

/**
 * MSAL should be instantiated outside of the component tree to prevent it from being re-instantiated on re-renders.
 * For more, visit: https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-react/docs/getting-started.md
 */
export const msalInstance = new PublicClientApplication(msalConfig);

msalInstance.initialize().then(() => {
  // Default to using the first account if no account is active on page load
  if (!msalInstance.getActiveAccount() && msalInstance.getAllAccounts().length > 0) {
    // Account selection logic is app dependent. Adjust as needed for different use cases.
    msalInstance.setActiveAccount(msalInstance.getAllAccounts()[0]);
  }
})

  // Optional - This will update account state if a user signs in from another tab or window
  msalInstance.enableAccountStorageEvents()

// Listen for sign-in event and set active account
  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload.account) {
      const account = event.payload.account
      msalInstance.setActiveAccount(account)
    }
  })

// React root, starts the program. Note the Router - tags, they need to be initialized here to make urls defined in App.jsx to function.
// msalInstance has to be passed to App as a prop.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router>
        <App instance={msalInstance}/>   
    </Router> 
  </React.StrictMode>,
)
