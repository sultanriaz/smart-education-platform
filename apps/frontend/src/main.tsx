import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./app/App";
import "./index.css";

try {
  document.documentElement.dataset.theme = localStorage.getItem("sep-theme") ?? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
} catch { document.documentElement.dataset.theme = "light"; }

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
