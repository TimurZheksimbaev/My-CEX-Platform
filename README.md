# This is my CEX platform, where you can exchange crypto and create wallets. Also you can see order book and create a new order, and then execute.

### To test the project, firstly clone repository
### Frontend launch
```bash
cd frontend
npm install
npm run dev
```

### Backend
#### Firstly create `.env` file with `DATABASE_URL` and `SECRET_KEY` variables, you can see `.env.example` in `backend` folder

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
