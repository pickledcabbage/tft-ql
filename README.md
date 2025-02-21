# Setup Instructions
## Backend
1. Install poetry off the website.
2. Switch and install env Python 3.12
3. Run poetry install

## Frontend
1. Go to frontend folder `frontend/tft-frontend`
2. install `npm`
3. Run `npm install`
4. Use `npm start` to start local server (use `--host` to specify ip address)
Note: don't forget to point `frontend/tft-frontend/src/Config.tsx` to your backend

## Database
1. Install docker here: https://docs.docker.com/engine/install/ubuntu/
2. Install mongoDB and CLI here: https://www.mongodb.com/docs/atlas/cli/current/install-atlas-cli/
3. Run `sudo atlas deployments setup myLocalRs1 --type local --force` to create local deployment