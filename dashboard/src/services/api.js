// API Service Layer for FaceGuard Dashboard
// Handles all backend API communications

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Generic request handler with error handling
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config = {
      headers: { ...defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // GET request
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(fullEndpoint, {
      method: 'GET',
    });
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // Health Check
  async getHealthStatus() {
    return this.get('/health');
  }

  // Person APIs
  async getPersons(page = 1, limit = 20, search = '') {
    return this.get('/persons', { page, limit, search });
  }

  async getPerson(personId) {
    return this.get(`/persons/${personId}`);
  }

  async createPerson(personData) {
    return this.post('/persons', personData);
  }

  async updatePerson(personId, personData) {
    return this.put(`/persons/${personId}`, personData);
  }

  async deletePerson(personId) {
    return this.delete(`/persons/${personId}`);
  }

  // Batch Enrollment API
  async batchEnrollPersons(metadataFile, imagesZip, processImmediately = true) {
    const formData = new FormData();
    formData.append('metadata_file', metadataFile);
    formData.append('images_zip', imagesZip);
    formData.append('process_immediately', processImmediately);

    return this.request('/batch-enrollment/persons', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  // Person with Images Enrollment
  async createPersonWithImages(personData, imageFiles) {
    const formData = new FormData();
    
    // Add person data as JSON
    formData.append('person_data', JSON.stringify({
      person_id: personData.employeeId,
      first_name: personData.firstName,
      last_name: personData.lastName,
      email: personData.email,
      phone: personData.phone,
      department: personData.department,
      position: personData.position,
      access_level: personData.accessLevel,
      is_vip: personData.riskLevel === 'critical',
      is_watchlist: personData.riskLevel === 'high' || personData.riskLevel === 'critical'
    }));

    // Add image files
    imageFiles.forEach((imageFile, index) => {
      formData.append(`images`, imageFile.file);
    });

    return this.request('/persons/with-images', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  // Sightings APIs
  async getSightings(page = 1, limit = 20, personId = null, cameraId = null, startDate = null, endDate = null) {
    const params = { page, limit };
    if (personId) params.person_id = personId;
    if (cameraId) params.camera_id = cameraId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    return this.get('/sightings', params);
  }

  async createSighting(sightingData) {
    return this.post('/sightings', sightingData);
  }

  // Analytics APIs (to be implemented on backend)
  async getAnalyticsOverview(timeRange = '7d') {
    return this.get('/analytics/overview', { time_range: timeRange });
  }

  async getDetectionTrends(timeRange = '7d') {
    return this.get('/analytics/detection-trends', { time_range: timeRange });
  }

  async getLocationAnalytics(timeRange = '7d') {
    return this.get('/analytics/location-stats', { time_range: timeRange });
  }

  async getConfidenceDistribution(timeRange = '7d') {
    return this.get('/analytics/confidence-distribution', { time_range: timeRange });
  }

  async getPersonActivityStats(timeRange = '7d', limit = 10) {
    return this.get('/analytics/person-activity', { time_range: timeRange, limit });
  }

  async getSystemMetrics() {
    return this.get('/analytics/system-metrics');
  }

  async getPeakHours(timeRange = '7d') {
    return this.get('/analytics/peak-hours', { time_range: timeRange });
  }

  async getAlertAnalytics(timeRange = '7d') {
    return this.get('/analytics/alerts', { time_range: timeRange });
  }

  // Monitoring APIs
  async getDashboardAnalytics() {
    return this.get('/api/dashboard/analytics');
  }

  async getSystemHealth() {
    return this.get('/dashboard/system/health');
  }

  async getServiceStatus() {
    return this.get('/api/status');
  }

  async getPerformanceMetrics(timeRange = '1h') {
    return this.get('/api/metrics/performance', { time_range: timeRange });
  }

  async getResourceUtilization() {
    return this.get('/api/metrics/resources');
  }

  async getCircuitBreakerStatus() {
    return this.get('/api/circuit-breaker/status');
  }

  // High Priority Person APIs
  async getHighPriorityPersons(page = 1, limit = 20) {
    return this.get('/high-priority-persons', { page, limit });
  }

  async addHighPriorityPerson(personData) {
    return this.post('/high-priority-persons', personData);
  }

  async removeHighPriorityPerson(personId) {
    return this.delete(`/high-priority-persons/${personId}`);
  }

  // Notification Contact APIs
  async getNotificationContacts(page = 1, limit = 20) {
    return this.get('/notification-contacts', { page, limit });
  }

  async createNotificationContact(contactData) {
    return this.post('/notification-contacts', contactData);
  }

  async updateNotificationContact(contactId, contactData) {
    return this.put(`/notification-contacts/${contactId}`, contactData);
  }

  async deleteNotificationContact(contactId) {
    return this.delete(`/notification-contacts/${contactId}`);
  }

  // WebSocket connection for real-time updates
  connectWebSocket() {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws/dashboard';
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected to dashboard');
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected from dashboard');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

// Export specific API categories for convenience
export const personAPI = {
  getAll: (params) => apiService.getPersons(params?.page, params?.limit, params?.search),
  getById: (id) => apiService.getPerson(id),
  create: (data) => apiService.createPerson(data),
  createWithImages: (personData, imageFiles) => apiService.createPersonWithImages(personData, imageFiles),
  batchEnroll: (metadataFile, imagesZip, processImmediately) => apiService.batchEnrollPersons(metadataFile, imagesZip, processImmediately),
  update: (id, data) => apiService.updatePerson(id, data),
  delete: (id) => apiService.deletePerson(id),
};

export const sightingsAPI = {
  getAll: (params) => apiService.getSightings(
    params?.page, params?.limit, params?.personId, 
    params?.cameraId, params?.startDate, params?.endDate
  ),
  create: (data) => apiService.createSighting(data),
};

export const analyticsAPI = {
  getOverview: (timeRange) => apiService.getAnalyticsOverview(timeRange),
  getDetectionTrends: (timeRange) => apiService.getDetectionTrends(timeRange),
  getLocationStats: (timeRange) => apiService.getLocationAnalytics(timeRange),
  getConfidenceDistribution: (timeRange) => apiService.getConfidenceDistribution(timeRange),
  getPersonActivity: (timeRange, limit) => apiService.getPersonActivityStats(timeRange, limit),
  getSystemMetrics: () => apiService.getSystemMetrics(),
  getPeakHours: (timeRange) => apiService.getPeakHours(timeRange),
  getAlertStats: (timeRange) => apiService.getAlertAnalytics(timeRange),
};

export const healthAPI = {
  getStatus: () => apiService.getHealthStatus(),
};

export const monitoringAPI = {
  getDashboardAnalytics: () => apiService.getDashboardAnalytics(),
  getSystemHealth: () => apiService.getSystemHealth(),
  getServiceStatus: () => apiService.getServiceStatus(),
  getPerformanceMetrics: (timeRange) => apiService.getPerformanceMetrics(timeRange),
  getResourceUtilization: () => apiService.getResourceUtilization(),
  getCircuitBreakerStatus: () => apiService.getCircuitBreakerStatus(),
};

// WebSocket utilities
export const connectDashboardWebSocket = () => apiService.connectWebSocket();