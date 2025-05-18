# Fragment Segmentation Application

## User Workflow

### 1. Access & Authentication
- Users connect through web browsers with domain resolution via DuckDNS
- Authentication options:
    - New users: Registration with username/password
    - Returning users: JWT-based login system
- Security implemented via FastAPI with bcrypt password hashing

### 2. Image Processing
- **Upload Options**:
    - Standard upload (storage only)
    - Upload with immediate processing
- **Analysis Process**:
    - YOLOv11 segmentation model identifies individual rock fragments
    - Precise masks are generated for each fragment
    - Volume calculations apply geometric algorithms to each mask
    - Results display includes color-coded overlays for visual identification

### 3. Result Management
- Historical processing records accessible through user dashboard
- Previous analyses available for retrieval and comparison
- Option to reprocess images with adjusted parameters

## Technical Architecture

### 1. Request Handling & Load Balancing
- Nginx serves as the entry point and load balancer
- Incoming requests are distributed to FastAPI backend instances

### 2. Processing Pipeline
- FastAPI processes image uploads and manages temporary storage
- YOLOv11 model (from Hugging Face Hub) performs segmentation
- OpenCV handles image processing and volume calculations
- Results flow: Upload → Processing → Database Storage → User Display

### 3. Data Infrastructure
- **PostgreSQL Database**:
    - Stores user profiles, authentication data
    - Maintains image metadata and analysis results
    - Interaction via SQLAlchemy ORM with Alembic migrations
- **Storage System (MinIO)**:
    - S3-compatible object storage for binary data
    - Original images preserved for reference
    - Processed overlays stored for rapid retrieval
    - Scalable design for high-performance image access

### 4. Frontend Architecture
- React-based user interface with Material-UI components
- Axios handles RESTful API communication
- Client-side features:
    - User authentication management
    - Image upload interface
    - Interactive result visualization

### 5. Deployment Infrastructure
- Docker containers for consistent environment
- Development: Docker Compose for local testing
- Production: Kubernetes orchestration for scaling
- Nginx reverse proxy for traffic management

### 6. Monitoring & Observability
- **Performance Monitoring**: Prometheus metrics with Grafana dashboards
- **Logging**: ELK stack (Elasticsearch, Logstash, Kibana)
- **Alerting**: Automated notifications for system issues

### 7. Security Framework
- JWT authentication for all API interactions
- Role-based access control system
- Secure credential storage and transmission

### 8. API Structure
- Key endpoints:
    - **Authentication**: `/api/auth/*`
    - **Basic Upload**: `/api/upload`
    - **Process & Analyze**: `/api/upload_predict`
    - **Result Retrieval**: `/api/fetch_prediction`
