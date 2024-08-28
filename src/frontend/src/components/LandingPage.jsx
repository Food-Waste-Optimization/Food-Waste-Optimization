
import vegetables from '../img/vegetables.jpg';


const LandingPage = () => {
    return (
  
    <div className="containergap">

        <div className="instructions">
        
            <h1>
            Welcome to Unicafe food waste optimization
            </h1>

            <h3>
            Our AI assisted forecasting tool helps with meal planning by predicting sales, occupancy, biowaste, and carbon emission levels based on your given data.
            </h3>

            <br></br>

            <h3>
            Enter the day, time, location, and ingredients to receive predictions in chart form.
            </h3>

            <br></br>

            <h3>
            You can use these insights to refine your parameters and optimize your results for better planning and sustainability.
            </h3>

        </div>

        <div className="instructionsimage">

        <img src={vegetables} style={{ width: '100%', height: 'auto' }}></img>

        </div>

    </div>
      
    );
  };

  export default LandingPage;