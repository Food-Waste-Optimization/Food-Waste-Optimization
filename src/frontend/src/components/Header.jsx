

import logopeople from '../img/logo_untanglingpeopleflow.png';
import logofood from '../img/logo_foodwaste.png';


const Header = () => {
    return (
  
    <div className="header">
        
        <img src={logopeople} width={200}></img>
        <img src={logofood} width={120}></img>
        <div class="title">
            <h2>Unicafe food waste optimization</h2>
            <h3>AI assisted model to forecast food consumption in YLVA restaurants</h3>
        </div>
        <hr class="line" />

    </div>
      
    );
  };

  export default Header;

