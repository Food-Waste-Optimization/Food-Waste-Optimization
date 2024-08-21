import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
import { loginRequest } from '../utils/authConfig.js'
import { Link } from 'react-router-dom'
import 'bulma/css/bulma.min.css'

// The Menu bar for the App. Different content for unauthenticated and authenticated users.

const Menu = ({ instance }) => {

  // The MS - logout function. Must have the instance as a prop to function properly
    const handleLogoutRedirect = () => {
        instance.logoutRedirect().catch((error) => console.log(error))
    }

  // The MS - login function
    const handleLoginRedirect = () => {
      instance.loginRedirect(loginRequest).catch((error) => console.log(error))
  }

  // helper variable to define the URL in Link-tag:
  const MODE = import.meta.env.MODE

  console.log('mode from menu: ', MODE)

  // Returns the menu bar. The authenticated version contains URL:s defined in the App.jsx to switch between views.
    return (
      <>
      <UnauthenticatedTemplate>
        <nav className="navbar" role="navigation" aria-label="main navigation">
            <div className="navbar-brand">
                <div className="p-5">
                    <h2 className="title is-2">Food Waste Optimization</h2>
                    <h4 className="subtitle is-4">AI assisted model to forecast food consumption in YLVA restaurants</h4>             
                </div>
              </div>
            <div className="navbar-start is-right">
                  <div className="navbar-item is-right"></div>
            </div>           
              <div className="navbar-end is-right">
                <div className="navbar-item is-right">
                  <div className="buttons">

                    <button className="button is-light" onClick={handleLoginRedirect}>
                      Log in for YLVA staff members
                   </button>
                  </div>
                </div>
              </div>
        </nav>
      </UnauthenticatedTemplate>
      <AuthenticatedTemplate>
        <nav className="navbar" role="navigation" aria-label="main navigation">
            <div className="navbar-brand">
                <div className="p-5">
                    <h2 className="title is-2">Food Waste Optimization</h2>
                    <h4 className="subtitle is-4">AI assisted model to forecast food consumption in YLVA restaurants</h4>             
                </div>
              </div>
              <div className="navbar-start is-right">
                  <div className="navbar-item is-right"></div>
            </div>           
              <div className="navbar-end is-right">
                <div className="navbar-item is-right">
                  <div className="buttons">
                    <button className="signInButton" onClick={handleLogoutRedirect}>
                    <Link to={ MODE == 'development' ? "/" : "/fwowebserver"} className="button is-light">
                      Sign out
                    </Link>
                   </button>

                  </div>
                </div>
              </div>        
            
        </nav>
        <div className="tabs">
        <ul>
          <li><Link to={ MODE == 'development' ? '/' : '/fwowebserver'}>Front Page</Link></li>
          <li><Link to={ MODE == 'development' ? '/sales' : '/fwowebserver/sales'}>Manager View</Link></li>
          <li><Link to={ MODE == 'development' ? '/menus' : '/fwowebserver/menus'}> Menu Creators View</Link></li>
          <li><Link to={ MODE == 'development' ? '/upload' : '/fwowebserver/upload' }>Data upload</Link></li>
        </ul>
      </div>
    </AuthenticatedTemplate>
    </>
    )
}

export default Menu