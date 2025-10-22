# ORFEAS Studio - Next.js Frontend

Modern React-based frontend for the ORFEAS AI-powered 3D model generation system. This Next.js application provides a sleek, responsive interface for converting 2D images into 3D STL files using advanced AI technology.

##  Features

- **Modern UI/UX**: Built with Next.js 15, React 18, and Tailwind CSS
- **Real-time Updates**: WebSocket integration for live generation progress
- **3D Model Preview**: Interactive Three.js viewer with controls
- **Advanced Controls**: Comprehensive generation settings including:

  - Multiple output formats (STL, OBJ, GBL)
  - Printer type optimization (FDM/SLA)
  - SLA printer-specific settings (Creality Halot-One X1)
  - Custom dimensions and quality settings

- **File Management**: Drag-and-drop upload with format validation
- **Download Manager**: Easy model download with format information
- **Responsive Design**: Works seamlessly across desktop and mobile devices

##  Quick Start

### Prerequisites

- Node.js 18+
- npm/yarn/pnpm
- ORFEAS Python backend running on `localhost:5000`

### Installation

1. **Install dependencies:**

   ```bash
   npm install

   ```text

2. **Set environment variables:**

   ```bash

   # Optional - defaults to localhost:5000

   echo "BACKEND_URL=http://localhost:5000" > .env.local

   ```text

3. **Start development server:**

   ```bash
   npm run dev

   ```text

4. **Open application:**

   Navigate to [http://localhost:3000](http://localhost:3000)

##  Development

### Available Scripts

```bash

## Development server with hot reload

npm run dev

## Production build

npm run build

## Start production server

npm start

## Lint code

npm run lint

## Type checking

npm run type-check

```text

### Project Structure

```text
src/
 app/                    # Next.js App Router
    api/               # API routes (proxy to Python backend)
       upload-image/  # Image upload endpoint
       generate-3d/   # 3D generation endpoint
    globals.css        # Global styles
    layout.tsx         # Root layout
    page.tsx          # Main application page
 components/            # React components
    ImageUploader.tsx  # Drag-and-drop image upload
    GenerationControls.tsx # 3D generation settings
    ModelViewer3D.tsx  # Three.js 3D model viewer
    ProgressTracker.tsx # Real-time progress display
    DownloadManager.tsx # File download interface
 hooks/                # Custom React hooks
     useSocket.ts      # WebSocket connection hook

```text

##  Configuration

### Environment Variables

| Variable      | Default                 | Description               |
| ------------- | ----------------------- | ------------------------- |
| `BACKEND_URL` | `http://localhost:5000` | ORFEAS Python backend URL |
| `NODE_ENV`    | `development`           | Environment mode          |

### Backend Integration

The frontend communicates with the ORFEAS Python backend via:

- **REST API**: Image upload and 3D generation requests
- **WebSocket**: Real-time progress updates and job notifications
- **File Serving**: Direct download of generated STL files

### API Endpoints

| Endpoint            | Method | Purpose                        |
| ------------------- | ------ | ------------------------------ |
| `/api/upload-image` | POST   | Upload image for 3D conversion |
| `/api/generate-3d`  | POST   | Start 3D model generation      |
| `/backend/*`        | ANY    | Proxy to Python backend        |

##  Customization

### Styling

The application uses Tailwind CSS with custom configurations:

```css
/* globals.css - Custom gradients and animations */
@layer utilities {
  .bg-gradient-orfeas {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
}

```text

### Components

All components are fully customizable and use TypeScript for type safety:

```typescript
interface GenerationParams {
  format: "stl" | "obj" | "gbl";
  dimensions: { width: number; height: number; depth: number };
  quality: number;
  printerType: "fdm" | "sla";
  slaModel?: string;
}

```text

##  Testing Integration

### Complex Shape Testing

The frontend supports testing with various complex shapes:

1. **Geometric Patterns**: Fractal trees, mathematical surfaces

2. **Organic Shapes**: Cellular structures, flowing curves

3. **Mechanical Parts**: Gears, technical components

4. **Text-to-3D**: AI-generated shapes from descriptions

### Quality Validation

- **Real-time Progress**: Live updates during generation
- **Error Handling**: Comprehensive error reporting
- **File Validation**: STL integrity checking
- **Download Verification**: File size and format validation

##  Mobile Support

- Responsive design for tablets and smartphones
- Touch-optimized 3D viewer controls
- Mobile-friendly file upload interface
- Adaptive layout for different screen sizes

##  Integration with ORFEAS Backend

### Workflow

1. **Image Upload** → Frontend uploads to Next.js API → Proxied to Python backend

2. **Job Creation** → Backend returns job ID → Frontend subscribes to updates

3. **Generation** → Backend processes → Real-time progress via WebSocket

4. **Completion** → Download URL provided → Frontend manages file download

### Real-time Features

- Live progress bars with step-by-step updates
- Status notifications (connecting, generating, completed, failed)
- WebSocket reconnection with automatic retry
- Background job management

##  Deployment

### Production Build

```bash
npm run build
npm start

```text

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

```text

### Environment Setup

```bash

## Production environment

BACKEND_URL=https://your-backend-url.com
NODE_ENV=production

```text

##  Contributing

1. Fork the repository

2. Create a feature branch: `git checkout -b feature/new-feature`

3. Commit changes: `git commit -am 'Add new feature'`

4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

##  License

This project is part of the ORFEAS system and follows the same licensing terms.

##  Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See `/docs` for detailed guides
- **Discord**: Join our development community
- **Email**: support@orfeas-studio.com

---

**ORFEAS Studio Next.js Frontend** - Transforming 2D images into 3D models with cutting-edge AI technology.
