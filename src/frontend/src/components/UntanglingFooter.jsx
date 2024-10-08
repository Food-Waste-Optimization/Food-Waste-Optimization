       


import logopeople from '../img/logo_untanglingpeopleflow.png';
import logofood from '../img/logo_foodwaste.png';


const UntanglingFooter = () => {
    return (
        
    
<div className="flex flex-col md:flex-row items-center justify-center md:justify-start p-10 w-full"> {/* Center items on smaller screens */}
    <div className="flex items-center mb-4 md:mb-0"> {/* Group logos with margin below on mobile */}
    <img src={logopeople} width={120} alt="People Logo" className="mr-4" /> {/* Original size, add right margin */}
    </div>
    <div className="text-center md:text-right md:ml-4 flex flex-col justify-center"> {/* Center text on mobile, left-align on desktop */}
        <h3 className="text-lg text-gray-600 mt-2">Untangling People Flow Consortium</h3> {/* Margin top to separate from h1 */}
    </div>
</div>





        
    );
    };

    export default UntanglingFooter;

       