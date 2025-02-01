```markdown:README.md
# Legal Automation System

A secure, microservices-based legal document automation system with AI capabilities, document version control, and multi-jurisdiction support.

## System Architecture

The system is built using a microservices architecture with the following components:

### Backend Services

1. **Document Service** (`/backend/document-service`)
   - Handles document creation, updates, and version control
   - Supports document metadata and jurisdiction-specific content
   - Implements secure document storage and retrieval

2. **Template Service** (`/backend/template-service`)
   - Manages legal document templates
   - Supports template versioning and jurisdictional variants
   - Handles template variables and placeholders

3. **AI Orchestrator** (`/backend/ai-orchestrator`)
   - Coordinates AI-powered document analysis
   - Manages document review and compliance checking
   - Provides template suggestions and risk assessment

4. **Audit Service** (`/backend/audit-service`)
   - Logs all system actions for compliance and tracking
   - Provides detailed audit trails
   - Stores logs in MongoDB for efficient querying

### Frontend Application

Built with React and TypeScript, providing:
- Real-time document editing
- Template management interface
- Collaboration features
- Audit log viewing

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Docker and Docker Compose

## Setup and Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/legal-automation-system.git
cd legal-automation-system
```

2. **Backend Setup**

Install Python dependencies for each service:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Required Python packages:
- fastapi
- uvicorn
- pydantic
- motor
- python-jose[cryptography]
- passlib[bcrypt]

3. **Frontend Setup**

```bash
cd frontend
npm install
```

Required npm packages:
- react
- @monaco-editor/react
- antd
- axios
- @types/react
- typescript

4. **Environment Configuration**

Create `.env` files for each service:

```env
# Backend services .env
MONGODB_URI=mongodb://localhost:27017
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000

# Frontend .env
REACT_APP_API_URL=http://localhost:8000
```

## Development

1. **Running Backend Services**

Start each service individually:
```bash
cd backend/document-service
uvicorn app:app --reload --port 8001

cd backend/template-service
uvicorn app:app --reload --port 8002

cd backend/ai-orchestrator
uvicorn app:app --reload --port 8003

cd backend/audit-service
uvicorn app:app --reload --port 8004
```

2. **Running Frontend**

```bash
cd frontend
npm start
```

## API Documentation

Each service provides Swagger documentation at `/docs` endpoint when running:
- Document Service: http://localhost:8001/docs
- Template Service: http://localhost:8002/docs
- AI Orchestrator: http://localhost:8003/docs
- Audit Service: http://localhost:8004/docs

## Security Features

- OAuth2 authentication for all services
- Role-based access control
- Audit logging for all actions
- Secure document storage
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Testing

Run backend tests:
```bash
pytest backend/*/tests
```

Run frontend tests:
```bash
cd frontend
npm test
```

## Docker Deployment

Build and run services using Docker Compose:
```bash
docker-compose up --build
```

## Project Structure

```
legal-automation-system/
├── backend/
│   ├── document-service/
│   ├── template-service/
│   ├── compliance-service/
│   ├── audit-service/
│   ├── integration-service/
│   ├── ai-orchestrator/
│   └── api-gateway/
├── frontend/
│   ├── src/
│   └── public/
└── docker/
```

## Future Enhancements

- Implement real-time collaboration using WebSocket
- Add support for digital signatures
- Enhance AI capabilities for document analysis
- Add document comparison features
- Implement workflow automation

## License

MIT License - see LICENSE file for details

## Support

For support, please open an issue in the GitHub repository or contact the development team.
```
