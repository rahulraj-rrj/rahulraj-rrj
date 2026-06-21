# Project Integration & Architecture Instructions

This document provides a guide on setting up a React + TypeScript + Tailwind v4 project with shadcn UI, along with an explanation of component paths and folder architecture.

---

## 1. Setup Instructions (Vite + TS + Tailwind v4 + shadcn)

If you are initializing this project structure from scratch, follow these commands:

### A. Scaffold the Vite + TypeScript Project
Create the project structure using Vite:
```bash
npx create-vite project-name --template react-ts
cd project-name
npm install
```

### B. Configure Tailwind CSS v4
Tailwind v4 features a CSS-first configuration and integrates as a Vite plugin:
1. Install Tailwind v4 and the Vite plugin:
   ```bash
   npm install tailwindcss @tailwindcss/vite
   ```
2. Open `vite.config.ts` and add the plugin:
   ```typescript
   import { defineConfig } from "vite"
   import react from "@vitejs/plugin-react"
   import tailwindcss from "@tailwindcss/vite"

   export default defineConfig({
     plugins: [
       react(),
       tailwindcss()
     ]
   })
   ```
3. Open `src/index.css` and import Tailwind:
   ```css
   @import "tailwindcss";
   ```

### C. Configure TypeScript Path Aliases (Required for shadcn)
Shadcn CLI relies on path aliases (like `@/*`) to reference components.
1. Install Node path types:
   ```bash
   npm install -D @types/node
   ```
2. Update `tsconfig.app.json` (inside the `compilerOptions` block) to map `@/*` to the `src/*` folder:
   ```json
   "baseUrl": ".",
   "paths": {
     "@/*": ["./src/*"]
   }
   ```
3. Update `vite.config.ts` to resolve the path alias in Vite:
   ```typescript
   import path from "path"
   import { defineConfig } from "vite"
   import react from "@vitejs/plugin-react"
   import tailwindcss from "@tailwindcss/vite"

   export default defineConfig({
     plugins: [react(), tailwindcss()],
     resolve: {
       alias: {
         "@": path.resolve(__dirname, "./src"),
       },
     },
   })
   ```

### D. Initialize shadcn UI
With aliases and Tailwind ready, initialize shadcn:
```bash
npx shadcn@latest init
```
*   Select **Radix** as the component library.
*   Select **Nova** as the preset.
*   The CLI will generate `components.json` and configure files.

---

## 2. Default Paths for Components & Styles

*   **Default Path for Base Components**: `@/components` (maps to `./src/components`)
*   **Default Path for UI Primitives (shadcn components)**: `@/components/ui` (maps to `./src/components/ui`)
*   **Default Path for Styles**: `src/index.css`

---

## 3. Importance of the `/components/ui` Folder Structure

In shadcn projects, UI components are created inside a dedicated subfolder (typically `src/components/ui` under the `@/components/ui` path alias). Maintaining this exact directory convention is important because:

1.  **CLI Scaffolding Location**:
    When you add standard shadcn components (e.g., `npx shadcn add button`), the CLI reads `components.json` and automatically downloads/writes the components directly into the designated `ui` alias folder. Modifying this structure without updating the config breaks the CLI automation.
2.  **Architectural Separation of Concerns**:
    It separates **low-level, primitive components** (generic, atomic elements like Buttons, Input inputs, Dialogs) from **high-level composite components** (like dashboard sidebars, profile cards, page layouts). This keeps the main `components/` directory clean.
3.  **Imports Consistency**:
    By using the alias `@/components/ui/button`, any file in the application can import the button without dealing with complex relative import paths (e.g., `../../../../components/button`). It keeps code cleaner and refactoring-safe.
