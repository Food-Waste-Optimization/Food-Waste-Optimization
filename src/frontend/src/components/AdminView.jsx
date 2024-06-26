import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
import Unauthorized from './Unauthorized'

// Template to construct view for Admins. Possible user management system would go here.

const AdminView = () => {

    return (
        <div>
            <AuthenticatedTemplate>
                <p>Admin view</p>
            </AuthenticatedTemplate>
            <UnauthenticatedTemplate>
                <Unauthorized></Unauthorized>
            </UnauthenticatedTemplate>
        </div>
    )
}

export default AdminView