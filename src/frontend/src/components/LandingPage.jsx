
import vegetables from '../img/vegetables.jpg';
import Button from '@mui/material/Button';

const LandingPage = ({ onSwitchTab }) => {
  return (
    <>
      <div className="flex flex-col md:flex-row container mx-auto p-3 mt-12">

        <div className="flex-1 md:mr-5 mb-10 max-w-lg">

          <h1 className="text-5xl font-bold text-[#155C2C] mb-4">
            Welcome to Unicafe Food Waste Optimization
          </h1>
          <p className="text-lg mb-4 py-3">
            Sustainable recommendation system designed to suggest optimal menus for any date and location at Kumpula campus. The system predicts sales, biowaste, and carbon emission levels. Leverage these insights to refine your meal plans and optimize your results for improved sustainability.
          </p>
  
          <Button 
            variant="contained" 
            sx={{
                bgcolor: '#155C2C',
                "&:hover": { bgcolor: '#1C1C1C', color: 'white' },
                width: '9.5em',
                height: '3.5em',
                fontSize: '18px'
              }}
            size="large"
            color="success" 
            onClick={onSwitchTab}
            className="mt-5"
          >
          Get started
          </Button>

        </div>

        <div className="flex-1 px-8">
          <img 
            src={vegetables} 
            className="w-full h-auto" 
          />
        </div>

      </div>
    </>
  );
};

export default LandingPage;
