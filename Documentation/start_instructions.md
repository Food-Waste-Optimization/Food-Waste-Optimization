To start, first clone the project: git clone https://github.com/Food-Waste-Optimization/Food-Waste-Optimization.git

# To Start with Back End:

- Make sure you have python (3.9) and poetry installed
- Create folder for data: src/data/basic_mvp_data/
- Add data files from slack-channel #data (or channel: files) into data folder
- Copy the contents of .env - file from Slack channel # files and place it to the root folder
- Set up ssh-redirect for database connection. Currently our databases on the UH servers can only be accessed from the Megasense server, so you will need access to set this up:
`ssh -L 5433:possu-test.it.helsinki.fi:5432 username@megasense-server.cs.helsinki.fi`
- Go to root and run:
  
`poetry install`

- To start app in development mode:
  
`poetry run invoke start-development`

# To Start with Front End:

- If not installed yet, install npm  and run:

`npm install vite`
  
- Go to folder /frontend
- Initialize React project by running:
```
npm create vite@latest ReactFrontEnd -- --template react
cd ReactFrontEnd
npm install
```
-The command will create an extra file 'ReactFrontEnd'. You can cut the contents of it, paste them to /frontend folder and remove the empty folder.

-Check that the contents of your vite.config.js - file (located on front end root) matches the following, and if not, replace the contents:
```
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  preview:{
    port: 8080,
    strictPort: true,
  },

  server:{
    port: 8080,
    strictPort: true,
    host: true
  }
})
```
- Copy the contents of .env - file from slack #files - channel and place it to the front end root.

- Once React is initialized and .env and vite.config.js - files are in place, you can do
```
git pull
```
- If you have additional App.jsx and main.jsx files located on the root (the project files should be under /frontend/src), remove them. Also additional css-files should be removed.

- Currently, these additional libraries are installed into project: axios, react-router-dom, bulma, chart.js, react-chartjs-2, @azure/msal-browser, @azure/msal-react

- To install dependencies go to React root folder (src/frontend) and run:
  
`npm install`

- To run React in dev-mode:

`npm run dev`
