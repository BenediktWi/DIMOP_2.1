# Frontend Setup

This React app uses Vite and Tailwind CSS.
It renders flows using **ReactFlow v11**.
Remember to import `reactflow/dist/style.css` in components that use ReactFlow.

```bash
cd frontend
npm install
npm run dev
```

### Tailwind CSS

The `postcss.config.cjs` file configures PostCSS with the
`tailwindcss` and `autoprefixer` plugins. After running `npm install`
you can start the development server with `npm run dev`; Vite will
compile the Tailwind styles automatically using this configuration.
Production builds created via `npm run build` also compile the CSS so
no additional steps are required. Ensure you have Node.js 18 or newer
installed.

### WebSocket host

The app connects to `localhost:8000` for WebSocket updates by default. Set the
`VITE_WS_HOST` environment variable to change this when running the dev server or
building for production.

```bash
# Example for a remote backend
VITE_WS_HOST=api.example.com:8000 npm run dev
```

The development server proxies API requests starting with `/projects`, `/materials`,
`/nodes`, `/relations`, `/score` and `/socket` to `http://localhost:8000`. Make sure
the backend is running on that port before starting the frontend. By default the
client loads project `1`. You can open a different project by adding
`?project=<id>` to the URL or by setting the `projectId` value in your browser's
local storage. If the initial request fails, the app displays an error message to
help with troubleshooting.
