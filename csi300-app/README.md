# CSI300 Standalone Application

CSI300 Standalone Application is a separated frontend application for browsing and analyzing CSI300 index companies. This application was extracted from the main Django backend to become a standalone frontend that communicates with the Django API.

## Current layout (legacy + React scaffold)

- **Legacy static pages** (still in use): `browser.html`, `index.html`, `detail.html`, `landing.html`, etc. These load assets from `assets/` and config from `config/` (e.g. `config/column-manifest.js`).
- **React/Vite scaffold** (new, optional): lives in `src/`. Multi-page entries are under `src/pages/landing` and `src/pages/browser`; shared pieces are under `src/components` and `src/styles`. Build output goes to `dist/react/` to stay isolated from the legacy static files.
- **Shared configuration**: environment variables via `.env.*` (`VITE_API_BASE`, `VITE_APP_NAME`), TypeScript configs (`tsconfig*.json`), lint/format configs (`eslint.config.js`, `prettier.config.cjs`), and styling (`tailwind.config.cjs`, `postcss.config.cjs`).

When using the legacy pages, load them directly from the repository root (for example `browser.html`) so they can resolve `config/column-manifest.js` correctly. The React scaffold is isolated and does not replace the legacy flow until you choose to migrate.

## Features

- **Company Filtering**: Filter companies by IM sector and market capitalization
- **Company Browser**: Browse companies with pagination and mobile-responsive design
- **Company Details**: View detailed financial metrics, ratios, and business information
- **REST API Integration**: Communicates with Django backend via REST API
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- **Standalone Deployment**: Can be deployed independently from the main Django application

## File Structure

```
csi300-app/
├── index.html              # Main filter page
├── browser.html             # Company browser with search results
├── detail.html              # Company detail page
├── README.md               # This file
├── config/
│   └── csi300_api_config.js # API configuration
└── assets/
    └── js/
        └── utils/
            └── csi300_api_client.js # API client for backend communication
```

## API Dependencies

This frontend application depends on the following Django backend API endpoints:

- `GET /api/csi300/api/companies/` - List companies with filtering
- `GET /api/csi300/api/companies/{id}/` - Get company details
- `GET /api/csi300/api/companies/filter_options/` - Get filter options
- `GET /api/csi300/api/companies/search/` - Search companies

## Setup and Deployment

### Local Development

1. Ensure the Django backend is running with CSI300 API endpoints enabled
2. Serve the `csi300-app` directory using any web server
3. Access the application via `index.html`

### Using Python HTTP Server

```bash
cd csi300-app
python3 -m http.server 8080
```

Then navigate to `http://localhost:8080`

### Using Node.js HTTP Server

```bash
cd csi300-app
npx http-server -p 8080
```

### Production Deployment

This application can be deployed to any static hosting service:

- **AWS S3 + CloudFront**: Upload files to S3 bucket (recommended)
- **Netlify**: Deploy the `csi300-app` folder
- **GitHub Pages**: Deploy via GitHub Actions
- **GitHub Pages**: Host directly from repository
- **Apache/Nginx**: Serve as static files

### Environment Configuration

Update `config/csi300_api_config.js` to point to your Django backend:

```javascript
const CSI300Config = {
    BASE_URL: 'https://your-django-backend.com', // Change this
    // ... rest of configuration
};
```

## Usage

### Main Filter Page (index.html)

- Select filters for IM sector and market cap range
- Click "Apply Filter" to view filtered results
- Click "View All" to see all companies

### Company Browser (browser.html)

- View paginated list of companies
- Apply additional filters
- Click on any company to view details
- Mobile-responsive table/card view

### Company Detail Page (detail.html)

- View comprehensive company information
- Financial metrics and ratios
- Risk assessment indicators
- Business description and basic information

## Technical Details

### API Communication

The application uses a custom API client (`csi300_api_client.js`) that:

- Handles HTTP requests with error handling
- Implements caching for better performance
- Supports filtering and pagination
- Provides consistent error messaging

### Responsive Design

- Desktop: Full table view with all columns
- Tablet: Optimized table with hidden columns
- Mobile: Card-based layout for better readability

### Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript features
- CSS Grid and Flexbox layout
- Fetch API for HTTP requests

## Development

### Adding New Features

1. Update API endpoints in Django backend if needed
2. Modify `csi300_api_config.js` for new endpoints
3. Extend `csi300_api_client.js` for new API methods
4. Update HTML/CSS/JS for new UI features

### Testing

Test the application with:

1. Different screen sizes (desktop, tablet, mobile)
2. Various filter combinations
3. Network connectivity issues
4. API error scenarios

## Integration with Main Application

This standalone application integrates with the main MEM Dashboard project:

- **Backend**: Django API endpoints in `src/django_api/csi300/`
- **Database**: Shares the same PostgreSQL database
- **Authentication**: Currently no authentication required
- **CORS**: Ensure CORS is configured for cross-origin requests

## Migration Notes

This application was migrated from Django templates to standalone HTML:

- **Original Location**: `src/django_api/csi300/templates/`
- **Template Variables**: Replaced with JavaScript API calls
- **URL Routing**: Django URLs replaced with query parameters
- **Static Files**: Self-contained CSS and JavaScript
- **Form Handling**: Client-side form processing

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check Django backend is running
   - Verify API endpoints are accessible
   - Check CORS configuration

2. **No Data Loading**
   - Verify database has CSI300 data
   - Check Django API responses
   - Review browser developer console for errors

3. **Mobile Layout Issues**
   - Test responsive breakpoints
   - Verify CSS media queries
   - Check touch interaction on mobile devices

### Debug Mode

Enable debug mode by opening browser developer console and running:

```javascript
// View API cache status
console.log(csi300ApiClient.getCacheStatus());

// Clear API cache
csi300ApiClient.clearCache();
```

## Future Enhancements

- [ ] Add real-time data updates
- [ ] Implement user authentication
- [ ] Add data export functionality
- [ ] Include charting and visualization
- [ ] Add company comparison features
- [ ] Implement advanced search capabilities
