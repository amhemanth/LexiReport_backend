# Plan for AI-Powered Mobile Reporting Application

## 1. Introduction

This document outlines a comprehensive plan and high-level architecture for developing an innovative mobile application. Its core purpose is to transform traditional reports into dynamic, audio-guided narratives by extracting key insights, providing AI-generated voice-overs primarily using **on-device capabilities**, and allowing users to interact with this content in both audio-only and visual-audio modes, including robust offline functionality. The application will seamlessly integrate with leading Business Intelligence (BI) platforms such as PowerBI, Tableau, and Google Data Studio. Critical to its efficiency and cost-effectiveness, the backend will leverage **open-source models for key insight extraction**. Furthermore, the plan explores the strategic use of ONNX for optimizing on-device AI processing, particularly for advanced voice features.

**Target Tech Stack:**
* **Backend:** Python (with frameworks like FastAPI/Flask/Django REST Framework)
* **Frontend:** Expo React Native

---

## 2. High-Level Architecture

The application is structured around three primary components, designed for modularity, scalability, and performance:

* **Mobile Frontend (Expo React Native):** The user-facing client application responsible for delivering an intuitive UI/UX. Its critical functions include **on-device Text-to-Speech (TTS) generation**, local data management for offline access, and secure communication with the backend.
* **Backend (Python):** The server-side powerhouse that orchestrates core business logic, handles data processing, executes **key insight extraction using open-source AI models**, and manages integrations with external services.
* **Data Storage:** A hybrid approach combining cloud-based solutions for persistent, synchronized data and local storage on the mobile device for offline accessibility.

### 2.1. System Architecture Diagram (Conceptual)
+----------------------+         +-----------------------+         +---------------------+
| Mobile Frontend      | ------> | API Gateway           | ------> | Backend Services    |
| (Expo React Native)  |         | (Python: FastAPI)     |         | (Python Modules)    |
| - On-Device TTS      |         +-----------------------+         +---------------------+
| - ONNX (Voice?)      |                   ^ |                             ^ | ^
+----------------------+                   | |                             | | |
          ^ |                              | |                             | | | (Task Queue)
          | | <----------------------------+-----------------------------+ | |
          | | (API Responses: Insights)    (Internal Service Calls)       | | |
          | |                                                              | v |
          | +-----> Local Storage <----------------------------------------+---+
          |         (SQLite, Files)        (Async Tasks: Celery/Redis)      |
          |                                                                 |
          +-----------------------------------------------------------------+
                                       (External Services)
                                              |
                                              v
                          +---------------------------------------+
                          | Cloud DB (PostgreSQL/MongoDB)         |
                          | File Storage (S3/GCS for reports,     |
                          |   backend-generated audio             |
                          |   if fallback is used)                |
                          | BI Platforms (PowerBI, Tableau, GDS)  |
                          | TTS Services (Cloud - for fallback    |
                          |   or premium voices only)             |
                          +---------------------------------------+

**Explanation of Diagram:**

* **Mobile Frontend:** The primary interface for users. It communicates with the API Gateway for data. Crucially, it takes the lead in **Text-to-Speech (TTS) generation directly on the device** for most voice-overs. It also manages local data for offline capabilities. The integration of ONNX is envisioned for potential future optimization of on-device AI tasks, especially for highly customized voice synthesis.
* **API Gateway:** Serves as the unified entry point for all mobile application requests, routing them efficiently to the appropriate backend services. This layer handles authentication, rate limiting, and request validation.
* **Backend Services:** A modular suite of Python applications responsible for processing, AI-driven insight extraction, and external system integrations. These services are the core intelligence of the application.
* **Task Queue:** An asynchronous processing mechanism that offloads computationally intensive and long-running operations (such as report parsing and **AI insight extraction using open-source models**) from the main request-response cycle, ensuring API responsiveness and scalability.
* **Data Storage (Cloud):** Centralized, persistent storage for all application data, including user profiles, report metadata, **extracted text insights**, and potentially backend-generated audio files (if a cloud TTS fallback is utilized).
* **External Services:** Encompasses third-party integrations, primarily the BI platforms (PowerBI, Tableau, Google Data Studio) for data fetching and, secondarily, cloud-based TTS services, which serve as a fallback or for premium voice options.

### 2.2. Detailed Backend Services (Python)

The backend will be architected as a collection of modular services, orchestrated by the API Gateway, enabling a microservices-like approach or a well-structured monolithic application.

* **API Gateway / Service Layer:**
    * **Technology:** FastAPI (recommended for its performance and modern Python features), Flask with extensions, or Django REST Framework.
    * **Responsibilities:** Single entry point for all frontend requests, request validation, authentication token verification (delegated to Auth Service), rate limiting, and routing to internal services.
* **Authentication & Authorization Service:**
    * **Purpose:** Manages the full user lifecycle and access control.
    * **Functions:** User registration, login (email/password, potentially OAuth for social logins), logout, password reset. Handles OAuth 2.0 flows for BI tool integrations (client-side initiation, server-side token exchange and secure storage). Securely stores and manages user credentials (hashed passwords) and encrypted API tokens for BI tools. Implements Role-Based Access Control (RBAC) if multi-tier user permissions are needed.
* **Report Processing Service:**
    * **Purpose:** Ingests and pre-processes report files.
    * **Functions:** Handles file uploads (PDF, Excel) from the frontend. Utilizes robust Python libraries like `PyPDF2`, `pdfplumber`, `Camelot` (for PDF tables), `Tesseract` (for OCR on image-based PDFs), `pandas`, and `openpyxl` (for Excel). Manages temporary storage for uploaded files during processing. Pre-processes files by performing content extraction, text cleaning, and table identification. Publishes tasks to the Task Queue for asynchronous parsing and **AI insight extraction**.
* **BI Integration Service:**
    * **Purpose:** Manages secure connections and data retrieval from BI platforms.
    * **Functions:** Establishes and manages secure connections to PowerBI, Tableau, and Google Data Studio APIs. Employs official Python client libraries or direct HTTP requests for data interaction. Fetches report data, metadata, and visualizations based on user permissions and API capabilities. Handles authentication token management (retrieval from secure storage, refresh tokens) for BI tools.
* **Insight Extraction Service (AI/ML) - Open Source Driven:**
    * **Purpose:** The core intelligence for generating insights.
    * **Functions:** Consumes processed data (from Report Processing Service or BI Integration Service) via the Task Queue. **Employs leading open-source NLP models and libraries** for textual data, such as:
        * **Summarization:** Hugging Face Transformers (e.g., BART, T5 models).
        * **Keyword Extraction:** `spaCy`, `NLTK`.
        * **Sentiment Analysis:** Hugging Face Transformers.
        * **Topic Modeling:** `scikit-learn` (e.g., Latent Dirichlet Allocation).
    * Applies analytical techniques for tabular data using libraries like `pandas`, `scikit-learn` (for clustering, anomaly detection), and `statsmodels` (for statistical summaries, trend detection).
    * Manages and serves these **open-source AI models** (potentially using tools like MLflow for versioning and deployment, and FastAPI/Flask for serving inference endpoints).
    * Stores extracted insights (primarily in text format) in the Cloud Database via the Data Management Service. The frontend will be primarily responsible for vocalizing these text insights.
* **Text-to-Speech (TTS) Service (Backend - Fallback/Support Role):**
    * **Purpose:** This service's role is deliberately secondary, primarily supporting the frontend's on-device TTS.
    * **Functions:** May provide a fallback TTS generation mechanism using cloud services (AWS Polly, Google TTS, Azure TTS) or robust open-source Python libraries (e.g., Coqui TTS, which offers high-quality models) if on-device TTS fails, if a user opts for higher-quality cloud voices (as a premium feature), or for initial proof-of-concept. Manages storage of any backend-generated audio files in Cloud File Storage and their metadata via the Data Management Service.
* **Data Management Service:**
    * **Purpose:** Provides a unified abstraction layer for data persistence.
    * **Functions:** Manages interactions with the chosen Cloud Database (e.g., PostgreSQL with SQLAlchemy ORM, or MongoDB with Pymongo/Motor ODM) and Cloud File Storage (S3/GCS). Handles CRUD (Create, Read, Update, Delete) operations for user accounts, report metadata, **extracted text insights**, BI connection details, and links to any backend-generated audio files. Ensures data consistency, integrity, and handles database migrations.
* **Task Queue Management Service:**
    * **Technology:** Implements and manages a task queue system (e.g., Celery with RabbitMQ/Redis, or RQ).
    * **Functions:** Workers pick up asynchronous tasks like report parsing and **AI insight extraction** from the queue. Allows for asynchronous processing, which significantly improves API responsiveness and scalability. Handles task retries, error logging, and status updates for long-running operations.
* **Notification Service (Optional but Recommended):**
    * **Purpose:** Informs users about important events.
    * **Functions:** Sends notifications to users (e.g., via Firebase Cloud Messaging (FCM) for push notifications to the mobile app) when report processing is complete and insights are ready for viewing/listening, or if BI tool re-authentication is needed.

### 2.3. Detailed Frontend Services/Modules (Expo React Native)

The mobile frontend will be architected into several distinct services or modules, promoting a clean, maintainable, and scalable codebase:

* **UI/UX Components & Screens:**
    * **Purpose:** The visual foundation and user interaction layer.
    * **Components:** Reusable UI elements (buttons, cards, lists, modals, audio players) built with React Native core components or popular UI libraries (e.g., React Native Elements, React Native Paper, NativeBase).
    * **Screens:** Dedicated screen components for various application views, including Authentication (Login, Register), Dashboard/Report List, Report Viewer, Insight Display, Audio Player, BI Integration Management, and Settings.
    * **Navigation:** Managed efficiently by `react-navigation` (supporting stack, tab, and drawer navigators).
    * **Styling:** Theming and styling using `StyleSheet`, `Styled Components`, or a utility-first CSS approach if applicable in React Native.
* **API Client Service:**
    * **Purpose:** Centralized module for all communication with the backend API Gateway.
    * **Functions:** Makes HTTP requests using `axios` or `fetch API`. Handles request/response formatting (JSON), automatically adds authentication headers (JWT tokens), and implements global error handling for API responses (e.g., network errors, 4xx/5xx status codes) including token refresh logic.
* **Local Data Management Service:**
    * **Purpose:** Manages offline storage and caching on the device.
    * **Functions:** Utilizes `AsyncStorage` for simple key-value data (user preferences, session tokens, basic metadata). Employs `SQLite` (via `expo-sqlite`) or `Realm` for structured relational data (downloaded report details, **extracted text insights**, local file paths for reports, or any user-generated/downloaded audio). Implements robust data synchronization logic (e.g., on app start, periodically) to update local data with the backend when online (primarily for insights and report metadata). Manages local file system access via `expo-file-system` for downloaded reports.
* **Report Rendering Service:**
    * **Purpose:** Displays various report formats on the device.
    * **Functions:** Renders PDF documents using libraries like `react-native-pdf` or `react-native-view-pdf`. For Excel data, this might involve backend conversion to JSON/HTML or displaying tabular data in custom list/table components, as direct Excel rendering in React Native is challenging. Displays data and visualizations fetched from BI tools, potentially rendering charts using libraries like `react-native-charts-wrapper`, `victory-native`, or displaying web views for embeddable BI content if supported. Handles interactive elements within reports, such as highlighting text corresponding to the current audio insight.
* **On-Device TTS & Audio Playback Service:**
    * **Purpose:** The primary engine for generating and playing voice-overs directly on the device.
    * **Functions:** **Primary responsibility for generating speech from text insights using integrated on-device capabilities.** Integrates with robust React Native TTS libraries (e.g., `react-native-tts`, which typically leverages native iOS/Android TTS engines, or explores community packages for other open-source TTS engines compatible with React Native for more control). Manages voice selection if the on-device engine supports multiple voices/languages. Handles audio playback using `expo-av`: loads audio generated by on-device TTS, provides controls (play, pause, seek, stop, volume control, playback speed adjustment). Supports seamless background audio playback and lock screen controls. **Synchronizes audio playback progress with the Report Rendering Service to dynamically highlight relevant report sections.** Manages caching of generated audio locally to avoid re-generation for the same insight text, optimizing performance and offline access.
* **Download Manager Service:**
    * **Purpose:** Manages content downloading for offline access.
    * **Functions:** Manages downloading of files (original reports, potentially pre-generated audio if a cloud fallback was used and user explicitly wants it offline) for offline access using `expo-file-system`. Provides intuitive UI feedback for download progress, completion, and errors. Manages local storage of downloaded files and updates the Local Data Management Service with their local paths.
* **Authentication Module:**
    * **Purpose:** Manages user authentication flows within the app.
    * **Functions:** Handles UI for login, registration, and password reset forms. Communicates with the backend Authentication Service via the API Client. Securely stores authentication tokens (e.g., JWT) using `expo-secure-store`. Manages user session state (e.g., using React Context or a robust state management library like Zustand/Redux). Initiates and handles OAuth flows for BI tool connections, potentially using `expo-web-browser` or `expo-auth-session` to open a web view for the BI provider's login page.
* **ONNX Runtime Integration Module (If applicable for advanced phase):**
    * **Purpose:** To enable high-performance AI inference directly on the mobile device.
    * **Functions:** Integrates an ONNX runtime library (e.g., `onnxruntime-react-native`). This could be explored for more advanced/custom on-device TTS models if suitable ONNX-compatible models exist and perform well on mobile. It could also be used for lightweight, specific on-device insight extraction tasks or pre-processing if deemed feasible and beneficial for enhanced offline use or reducing backend load for certain simple tasks. Manages loading ONNX models bundled with the app or downloaded. Provides an interface for running inference on-device and handling model inputs/outputs.
* **Background Task Manager:**
    * **Purpose:** Manages background operations for a seamless user experience.
    * **Functions:** Utilizes Expo's background task capabilities (`expo-task-manager`) for tasks such as: periodic data synchronization when the app is in the background, completing downloads if the app is backgrounded, and ensuring robust background audio playback.

---

## 3. Feature Breakdown and Implementation Approach

### 3.1. Report Ingestion and Key Insight Extraction

* **Supported Formats:** PDF, Excel, and direct integration with major BI Dashboards (PowerBI, Tableau, Google Data Studio).
* **Process:**
    * **Upload/Link (Frontend):** Users initiate by uploading files via `expo-document-picker` or connecting their BI tools through an OAuth flow.
    * **Backend Parsing & Pre-processing (Python - Report Processing Service):** For uploaded files, the backend handles robust parsing of PDF and Excel documents (extracting text, tables, images for OCR). For BI tools, the `BI Integration Service` fetches relevant data and metadata directly from the BI platform APIs.
    * **Key Insight Extraction (Python Backend - Insight Extraction Service):** This is where the core AI magic happens. The service consumes the processed data (textual content, tabular data) via the Task Queue. It then **utilizes sophisticated open-source NLP and ML models** (e.g., from Hugging Face for summarization, spaCy/NLTK for keyword extraction, scikit-learn for anomaly detection in tabular data) to identify and extract key insights. This process is inherently asynchronous to maintain responsiveness.
    * **Storage (Backend - Data Management Service):** The extracted **text insights** (not audio, as audio is primarily generated on-device) are meticulously stored in the cloud database, linked to the original report.

### 3.2. AI-Generated Voice Over - On-Device First

* **Process:**
    * **Insight Retrieval (Frontend):** Once the backend has completed extracting text insights, the frontend fetches these insights.
    * **On-Device TTS Generation (Frontend - On-Device TTS & Audio Playback Service):** This is the **primary method**. The frontend leverages integrated mobile TTS capabilities (`react-native-tts` or similar libraries that interface with native iOS/Android TTS engines) to convert the fetched text insights into speech directly on the user's device. This prioritizes speed, privacy, and offline functionality.
    * **Multi-voice Support:** The availability of multiple voice options and languages is directly dependent on the capabilities of the chosen on-device TTS engine. Native iOS/Android engines typically offer a rich selection.
    * **Audio Caching (Frontend):** To enhance performance and enable offline listening, generated audio segments (from on-device TTS) are cached locally on the device, preventing repeated generation for the same insight text.
    * **Fallback to External TTS (Optional):** In scenarios where on-device TTS might be unavailable, requires specific high-quality voices not locally present, or if a user opts-in for premium voice options, the application can intelligently request audio from the `Backend TTS Service`. This backend service would then utilize cloud TTS APIs (an **external service**) or powerful open-source backend TTS models.

### 3.3. View Reports While Listening (Frontend - Expo React Native)

* **UI Design:** A highly synchronized and interactive view is presented, where the relevant section of the report content dynamically highlights as the **on-device generated audio** plays. This provides a rich, multimodal consumption experience.
* **Synchronization:** This is achieved by either precise timestamping of insights (if the backend provides this) or by associating insights with specific text blocks/pages within the report. The audio player (`expo-av`) continuously triggers UI updates based on the playback progress of the **on-device generated audio**, ensuring a seamless highlight experience.

### 3.4. Modes of Interaction (Frontend - Expo React Native)

The application offers flexible content consumption modes:

* **Audio-Only Mode:** A minimalist UI focused purely on audio playback controls for the **on-device generated audio**. This mode prioritizes listening convenience, especially useful during commutes or when visual attention is not possible. Robust background audio support is a key feature here.
* **Visual-Audio Mode:** The full, immersive experience combining the display of the report with synchronized **on-device generated audio** narration. This is the default and most comprehensive interaction mode.

### 3.5. Offline Mode (Frontend & Backend)

The application is designed to provide robust offline access to downloaded content.

* **Process:**
    * **Download Selection (Frontend):** Users explicitly select reports or insights they wish to make available offline from the report list or within a report viewer.
    * **Data Packaging (Backend/Frontend):** The backend prepares and delivers the necessary components: the original report file and the extracted **text insights**. The frontend takes primary responsibility for storing these locally. **Audio for offline playback is primarily generated on-demand by the frontend from these locally stored text insights.** If any backend-generated audio (from a fallback scenario) was explicitly downloaded, it too is stored locally.
    * **Frontend Download & Storage (Expo React Native):** Utilizes `expo-file-system` for efficient downloading and storage of report files. `SQLite` (via `expo-sqlite`) or `Realm` is used for persistent storage of text insights and their associated metadata.
    * **Offline Access (Frontend):** When the device lacks network connectivity, the application seamlessly switches to offline mode. It loads reports and their **text insights** directly from local storage. When the user initiates playback, the **On-Device TTS Service generates speech directly from these local text insights**, ensuring full voice-over functionality even without an internet connection.

### 3.6. Multimodal Interaction

The application excels in multimodal engagement by seamlessly combining:
* Visual display of detailed report content.
* Dynamic highlighting of relevant sections.
* Synchronized **on-device generated audio** narration.
This approach caters to diverse learning styles and consumption preferences.

### 3.7. Seamless Integrations (Backend - Python)

Integration with leading BI platforms is a cornerstone feature:

* **PowerBI, Tableau, Google Data Studio:**
    * **Authentication:** Robust OAuth 2.0 flows are managed cooperatively by the `Backend Authentication Service` (for token exchange and secure storage) and the `Frontend Authentication Module` (for initiating the browser-based OAuth process).
    * **API Interaction:** The `Backend BI Integration Service` handles all API interactions and data fetching, ensuring secure and efficient retrieval of reports and data from these **external services**.

### 3.8. ONNX in Mobile Computing (Advanced - Frontend)

* **Objective:** To execute highly optimized AI models directly on the mobile device, pushing the boundaries of on-device intelligence.
* **Primary Focus for ONNX:** This technology will be explored in advanced phases for two key areas:
    * **Enhancing On-Device TTS:** Potentially enabling more custom, high-quality, or specialized voices that might not be available through native TTS engines, by running specific TTS models (e.g., Tacotron, FastSpeech models converted to ONNX) directly on the device.
    * **Lightweight On-Device Insight Tasks:** For very specific, computationally inexpensive insight-related tasks (e.g., simple sentiment detection, keyword spotting) that could run offline or significantly reduce backend load for certain operations.
* **Implementation:** Involves integrating `onnxruntime-react-native`. This requires careful model conversion and optimization for mobile hardware, along with managing the loading and inference pipeline for ONNX models bundled with the app or downloaded post-install.

---

## 4. User Flows

This section details typical user journeys through the application, highlighting the interaction between frontend, backend, and the core functionalities.

### 4.1. New User Registration & Login

1.  **User (U):** Opens the application, lands on the Welcome/Login screen.
2.  **U (Registration):** Taps "Register."
3.  **Frontend (FE):** Displays the Registration form (email, password, confirm password).
4.  **U:** Fills in the form and taps "Register."
5.  **FE (Auth Module):** Validates input client-side. Sends registration request to the Backend (BE) API Gateway.
6.  **BE (API Gateway -> Auth Service):** Receives, validates data, creates a new user account, securely hashes the password, and stores it in the Cloud DB (via Data Management Service).
7.  **BE:** Sends a success response (possibly with an authentication token) to the FE.
8.  **FE (Auth Module):** Stores the token securely (`expo-secure-store`), navigates to the main app screen (e.g., Dashboard).
9.  **U (Login Flow):** Taps "Login," enters credentials.
10. **FE (Auth Module):** Sends login request to BE.
11. **BE (API Gateway -> Auth Service):** Verifies credentials against the stored hashed password.
12. **BE:** Sends a success response (with token) or an error message.
13. **FE:** Stores the token, navigates to the Dashboard or displays an error.

### 4.2. Uploading a Report (PDF/Excel) & Getting Insights

1.  **U:** On the Dashboard, taps "Upload Report."
2.  **FE:** Prompts the user to select the file type (PDF/Excel) and pick a file using `expo-document-picker`.
3.  **U:** Selects a file from their device.
4.  **FE (API Client):** Uploads the file to the BE (API Gateway -> Report Processing Service). Displays a loading indicator.
5.  **BE (Report Processing Service):** Stores the file temporarily. Initiates an asynchronous task for parsing and **AI insight extraction** by putting it on the Task Queue. Returns an "Processing" status to the FE.
6.  **FE:** Displays a "Report is processing" message. The FE can poll for status updates, or the BE can use the Notification Service to push an update.
7.  **BE (Task Queue Worker -> Report Proc. -> Insight Ext. (using open-source models) -> Data Mgmt):**
    * Parses the file (e.g., extracts text, tables).
    * **Extracts text insights using open-source NLP/ML models.**
    * Stores the original report data and the extracted text insights in the Cloud DB/File Storage.
8.  **BE (Notification Service - Optional):** Sends a push notification to the user's device: "Your report insights are ready!"
9.  **FE:** Updates the report list (upon receiving notification or next refresh). Fetches the newly available text insights for the report.
10. **U:** Taps on the newly processed report in the list.
11. **FE (Report Rendering, On-Device TTS & Audio Playback):** Displays the report content and the fetched text insights. When the user taps the play button, the **On-Device TTS Service generates speech from the fetched text insights**, and playback begins. Provides full audio playback controls.

### 4.3. Connecting a BI Tool & Getting Insights

1.  **U:** Navigates to the "Integrations" or "Connect BI Tool" section.
2.  **U:** Selects a BI tool (e.g., PowerBI).
3.  **FE (Auth Module):** Initiates the OAuth flow (opens a web browser via `expo-web-browser` to the PowerBI login page, leveraging an **external service**).
4.  **U:** Logs into PowerBI and authorizes the application.
5.  **PowerBI (External Service):** Redirects back to the FE redirect URI with an authorization code.
6.  **FE:** Captures the authorization code and sends it to the BE (API Gateway -> Auth Service / BI Integration Service).
7.  **BE:** Exchanges the code for access/refresh tokens with the PowerBI API (an **external service**). Securely stores the encrypted tokens (via Data Management Service).
8.  **BE:** Sends a success response to the FE.
9.  **FE:** Shows "Connected" status for the BI tool.
10. **U:** Navigates to a section to browse/select reports from the newly connected BI tool.
11. **FE:** Requests a list of available reports from the BE (API Gateway -> BI Integration Service).
12. **BE (BI Integration Service):** Uses the stored token to fetch the report list from the BI tool API (**external service**). Sends the list to the FE.
13. **U:** Selects a specific BI report.
14. **FE:** Requests **insight extraction** for this BI report from the BE.
15. **BE (BI Integration Service -> Insight Ext. (using open-source models) -> Data Mgmt):** Fetches the detailed report data from the BI tool, **extracts text insights using open-source NLP/ML models** (similar to the file upload flow, via the Task Queue), and stores them.
16. **FE:** Fetches the text insights. When the user plays audio, the **On-Device TTS Service generates speech**. Displays insights and audio once ready.

### 4.4. Listening to Insights (Visual-Audio & Audio-Only)

1.  **U:** Opens a processed report with fetched text insights.
2.  **FE (Report Rendering, On-Device TTS & Audio Playback):** Displays the report content and insights. An audio player with controls is visible.
3.  **Visual-Audio Mode (Default):**
    * **U:** Taps "Play" on the audio player.
    * **FE (On-Device TTS & Audio Playback Service):** **Generates audio from the insight text** (if not already cached locally) and begins playback.
    * **FE (Report Rendering Service):** **Synchronizes the report view**, dynamically highlighting text or sections corresponding to the currently playing audio segment.
4.  **Audio-Only Mode:**
    * **U:** Taps a "Switch to Audio-Only" button or minimizes the visual report.
    * **FE:** The UI transforms into a simplified audio player interface. The report view might be hidden or minimized.
    * **FE (On-Device TTS & Audio Playback Service):** Continues audio playback (using **on-device generated/cached audio**). Robust background playback is enabled, allowing users to listen while using other apps or with the screen off.
5.  **Controls:** Standard audio controls are available: Play, Pause, Skip to next/previous insight, and Voice selection (if supported by the **on-device TTS engine**).

### 4.5. Taking a Report Offline

1.  **U:** While viewing a report list or a specific report, the user sees an option to download.
2.  **U:** Taps "Download for Offline" icon/button for a desired report.
3.  **FE (Download Manager Service):**
    * Requests necessary data from the BE (original report file, **text insights**).
    * Shows download progress for the report file.
    * Downloads the report file using `expo-file-system`.
4.  **FE (Local Data Management Service):** Stores the report file locally on the device. Stores the associated **text insights** in the local SQLite database.
5.  **FE:** Updates the UI to clearly indicate that the report is now available offline. (Crucially, **audio will be generated on-device from these local text insights** when the report is accessed offline, rather than pre-downloading audio).

### 4.6. Accessing Offline Content

1.  **U:** Opens the app while in offline mode (no network connectivity) or navigates to an "Offline Reports" section.
2.  **FE (Local Data Management Service):** Detects no network. Loads the list of downloaded reports and their associated **text insights** directly from the local database.
3.  **U:** Selects an offline report.
4.  **FE (Report Rendering, On-Device TTS & Audio Playback):**
    * Loads the report content from the local file system.
    * Loads the **text insights** from the local database.
    * When the user plays audio, the **On-Device TTS Service generates speech directly from these local text insights**, ensuring full voice-over functionality even without an internet connection.
    * Enables full viewing and playback experience using only local resources.

---

## 5. Requirements

### 5.1. Functional Requirements

**User Management:**
* FR1: Users shall be able to register using email and password.
* FR2: Users shall be able to log in using their registered credentials.
* FR3: Users shall be able to log out.
* FR4: (Optional) Users shall be able to reset their password.

**Report Handling:**
* FR5: Users shall be able to upload PDF files.
* FR6: Users shall be able to upload Excel files.
* FR7: The system (backend) shall parse uploaded PDF and Excel files to extract content (text, tables).
* FR8: Users shall be able to view a list of their uploaded and processed reports.
* FR9: Users shall be able to select a report to view its content.

**BI Tool Integration (External Services):**
* FR10: Users shall be able to connect their PowerBI accounts using OAuth2.
* F R11: Users shall be able to connect their Tableau accounts using OAuth2.
* FR12: Users shall be able to connect their Google Data Studio accounts using OAuth2.
* FR13: The system (backend) shall fetch accessible reports/data/metadata from connected BI tools.

**Key Insight Generation & Display (Open Source Driven):**
* FR14: The system (backend) shall generate key **text insights** from processed report content using **open-source NLP/ML models**.
    * FR14.1: The generated insights shall be relevant and accurate to the report's content.
* FR15: Users shall be able to view the extracted key **text insights** alongside the report on the frontend.

**Voice Over (Primarily On-Device):**
* FR16: The system (frontend) shall generate AI voice-overs for the extracted key **text insights using on-device TTS capabilities**.
* FR17: Users shall be able to play, pause, and stop the voice-over.
* FR18: Users shall be able to select from multiple voice options for the **on-device TTS**, if supported by the native mobile TTS engine.
* FR19: (Fallback/Premium) The system shall support optional generation of voice-overs using **external cloud TTS services** if on-device fails or for premium voice options.

**Interaction Modes:**
* FR20: The system shall support a visual-audio mode where the report is displayed and synchronized with the **on-device generated voice-over**.
* FR21: The system shall support an audio-only mode with controls for playback of **on-device generated audio**.
* FR22: Audio playback shall continue in the background if the app is not in the foreground.

**Offline Mode:**
* FR23: Users shall be able to select specific reports (with their **text insights**) for download to the device.
* FR24: Users shall be able to access and interact with downloaded content (view report, read insights, play **on-device generated audio from local text insights**) while offline.
* FR25: The system shall indicate which content is available offline.

**ONNX (Advanced):**
* FR26: (If implemented) The system shall explore using ONNX models on-device for enhancing TTS (e.g., custom voices) or for specific, lightweight insight-related tasks that can run offline.

### 5.2. Non-Functional Requirements

**Performance:**
* NFR1: Backend report parsing and **open-source insight extraction** for an average-sized PDF/Excel (e.g., 50 pages, 5MB) should complete within 30-90 seconds, depending on complexity and chosen models.
* NFR2: **On-device TTS generation** for an average set of insights (e.g., 100 words) should start playing within 1-3 seconds on a modern device.
* NFR3: App UI transitions and screen loading should be smooth, ideally under 200ms.
* NFR4: Offline content should load almost instantaneously.

**Scalability:**
* NFR5: The backend system should support at least 100 concurrent users without significant degradation in performance (for MVP, scaling up thereafter).
* NFR6: The backend should be able to process 1000 reports per hour.

**Security:**
* NFR7: All communication between frontend and backend must use HTTPS.
* NFR8: User passwords must be hashed and salted using industry-standard algorithms (e.g., bcrypt).
* NFR9: BI tool OAuth tokens must be encrypted at rest and transmitted securely.
* NFR10: The application must be protected against common vulnerabilities (e.g., OWASP Mobile Top 10, OWASP API Security Top 10).

**Usability:**
* NFR11: The mobile application must have an intuitive and user-friendly interface, requiring minimal learning curve.
* NFR12: The system must provide clear feedback for user actions (e.g., loading indicators, success/error messages).
* NFR13: The application should adhere to platform-specific (iOS/Android) design guidelines.
* NFR14: Accessibility features (e.g., font scaling, screen reader compatibility for key elements, sufficient color contrast) should be considered.

**Reliability/Availability:**
* NFR15: The backend services should aim for an uptime of 99.9%.
* NFR16: The application should handle errors gracefully and provide informative messages to the user (including **on-device TTS** and network errors).
* NFR17: Offline mode must function reliably without network connectivity once data is downloaded.

**Maintainability:**
* NFR18: Backend and frontend code should be modular, well-commented, and follow consistent coding standards.
* NFR19: APIs should be well-documented (e.g., using OpenAPI/Swagger).
* NFR20: Automated tests (unit, integration, end-to-end) should be implemented for critical components.

**Data Integrity:**
* NFR21: **Extracted insights** and **on-device generated audio** must accurately reflect the source report content and text insights.
* NFR22: Data synchronized for offline mode must be consistent with the online version at the time of download.

**Offline Capability:**
* NFR23: The transition between online and offline modes should be seamless.
* NFR24: The app should clearly manage on-device storage and inform users if space is low.

**Integration Robustness:**
* NFR25: The system must gracefully handle API errors, rate limits, and schema changes from integrated BI platforms (**external services**).
* NFR26: Authentication with BI tools (**external services**) should be robust and handle token expiry/refresh mechanisms.

---

## 6. Suggested Phased Development Approach

A phased approach is crucial for managing complexity, delivering early value, and incorporating feedback iteratively.

**Phase 1: Core MVP (Focus: On-Device TTS & Basic Open-Source Insights)**
* **Frontend:**
    * Basic UI for User Authentication (Login/Register).
    * PDF file upload interface.
    * Basic Report Viewer for PDFs.
    * **Primary implementation of on-device TTS using native capabilities (`react-native-tts`)**.
    * Basic audio player controls (play/pause).
    * Display of raw extracted text insights.
* **Backend:**
    * Basic User Authentication Service.
    * PDF Parsing in Report Processing Service.
    * **Simple text summarization/keyword extraction using a readily available open-source NLP model** (e.g., a pre-trained Hugging Face summarization model).
    * Data Management for users and report insights.
    * Task Queue setup (Celery/Redis) for asynchronous processing.
* **Outcome:** Users can upload PDFs, get basic text insights, and listen to them with **on-device generated voice-overs**. No offline or BI integrations yet.

**Phase 2: Enhanced Features & Offline Capabilities**
* **Frontend:**
    * Add Excel file upload and display (potentially simple table rendering).
    * Implement multi-voice/language selection for **on-device TTS** if supported by the chosen library/native engines.
    * **Implement basic offline mode:** Allow users to download PDF/Excel reports, with their text insights stored locally. **Audio for offline playback will be generated on-device from these local text insights.**
    * Visual-Audio synchronization (basic highlighting).
* **Backend:**
    * Add Excel parsing capabilities.
    * **Improve backend insight extraction models:** Explore more sophisticated open-source options for deeper analysis (e.g., trend detection, anomaly detection for tabular data).
    * Refine data management for offline synchronization.
* **Outcome:** Expanded report format support, richer insights, initial offline functionality, and improved voice experience.

**Phase 3: BI Integrations (Leveraging External Services)**
* **Frontend:**
    * UI for connecting BI tools.
    * Display of BI reports/dashboards (e.g., using web views for embeds or basic chart rendering).
    * **On-device TTS** for insights extracted from BI data.
* **Backend:**
    * Implement OAuth 2.0 and API integration for the first BI tool (e.g., Google Data Studio, given its web-centric nature might be simpler to start).
    * `BI Integration Service` for data fetching from the chosen **external BI service**.
    * **Insight extraction using open-source models** applied to BI data.
    * Notification service for BI report processing completion.
* **Outcome:** Users can connect to one BI platform, fetch reports, and get AI-generated insights with voice-overs.

**Phase 4: Advanced Features & Polish (Including ONNX & Fallback TTS)**
* **Frontend:**
    * Integrate remaining BI tools (PowerBI, Tableau) fully.
    * Implement full-fledged offline mode with robust data synchronization mechanisms.
    * UI/UX refinements across the application, advanced audio playback controls.
    * **Explore and potentially integrate ONNX runtime for optimizing on-device TTS** (e.g., for custom voices or higher performance models if available and feasible) or other lightweight on-device AI tasks.
    * Implement the **fallback mechanism to backend (cloud/open-source) TTS services** for premium voices or in case of on-device TTS issues.
* **Backend:**
    * Integrate remaining BI tools.
    * Refine scalability and performance of AI models.
    * Implement and optimize the **backend TTS fallback service**.
* **Outcome:** A complete, highly polished, and performant application with comprehensive integrations, robust offline capabilities, and advanced on-device AI.

---

## 7. Conclusion

Building this AI-powered mobile reporting application is a significant, yet highly valuable, undertaking. The core strategic decision to prioritize **on-device Text-to-Speech (TTS)** for immediate, private, and offline voice-overs, complemented by the leveraging of **open-source models for robust backend insight extraction**, forms a strong foundation. The combination of Python for the backend and Expo React Native for the frontend is well-suited for rapid development and cross-platform deployment.

A phased development approach, commencing with a Minimum Viable Product (MVP) centered on core **on-device TTS** and **open-source backend insight capabilities**, is strongly recommended. Careful planning around data flow, API design, the choice of **on-device TTS solutions**, **external service integrations (BI platforms and optional cloud TTS)**, and **open-source model integration and deployment** will be absolutely crucial for the project's success. This detailed plan provides a clear roadmap to bring this innovative vision to fruition.