# Frontend Setup

This React app uses Vite and Tailwind CSS.

```bash
cd frontend
npm install
npm run dev
```

The development server proxies API requests starting with `/projects`, `/materials`,
`/nodes`, `/relations`, `/score` and `/ws` to `http://localhost:8000`. Make sure
the backend is running on that port before starting the frontend. On start it
connects to the backend at the same host and loads project 1.
