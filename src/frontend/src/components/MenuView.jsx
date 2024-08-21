import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
import { Doughnut as Doughnut1 } from 'react-chartjs-2'
import { Doughnut as Doughnut2 } from 'react-chartjs-2'
import { Doughnut as Doughnut3 } from 'react-chartjs-2'
import { Doughnut as Doughnut4 } from 'react-chartjs-2'
import { Chart as ChartMenus1, LinearScale, ArcElement, Title, Tooltip, Legend } from 'chart.js'
import { Chart as ChartMenus2 } from 'chart.js'
import { Chart as ChartMenus3 } from 'chart.js'
import { Chart as ChartMenus4 } from 'chart.js'
import MenuChart from './MenuChart'
import Unauthorized from './Unauthorized'
import 'bulma/css/bulma.min.css'

// Component returning sub components presenting views to compare menu items of lunches sold in different quartals. 
// Data comes from App.jsx as props and is passed to sub components.

const MenuView = ({ fetchedMenuData, isLoadingMenuData}) => {

    // Different charts are imported and registered here and passed to sub component MenuChart.jsx as props.
    // ChartMenus and Doughnuts must have different names to prevent conflicts.
    ChartMenus1.register(ArcElement, LinearScale, Title, Tooltip, Legend)
    ChartMenus2.register(ArcElement, LinearScale, Title, Tooltip, Legend)
    ChartMenus3.register(ArcElement, LinearScale, Title, Tooltip, Legend)
    ChartMenus4.register(ArcElement, LinearScale, Title, Tooltip, Legend)           


    // For authenticated users MenuCharts are returned. Unauthenticated users see the component Unauthorized.jsx.
    return (
        <div>
            <AuthenticatedTemplate>
                <div className="pt-3">
                    <div className="fixed-grid">
                        <div className="grid">
                            <MenuChart fetchedMenuData={fetchedMenuData} isLoadingMenuData={isLoadingMenuData} Chart={ChartMenus1} Doughnut={Doughnut1}></MenuChart>
                            <MenuChart fetchedMenuData={fetchedMenuData} isLoadingMenuData={isLoadingMenuData} Chart={ChartMenus2} Doughnut={Doughnut2}></MenuChart>
                            <MenuChart fetchedMenuData={fetchedMenuData} isLoadingMenuData={isLoadingMenuData} Chart={ChartMenus3} Doughnut={Doughnut3}></MenuChart>
                            <MenuChart fetchedMenuData={fetchedMenuData} isLoadingMenuData={isLoadingMenuData} Chart={ChartMenus4} Doughnut={Doughnut4}></MenuChart>
                        </div>
                    </div>
                </div>
            </AuthenticatedTemplate>
            <UnauthenticatedTemplate>
                <Unauthorized></Unauthorized>
            </UnauthenticatedTemplate>
        </div>
    )
}

export default MenuView