import { generateAvatar } from '@/lib/utils';

export const enrolledPersons = [
  {
    id: 'EMP001',
    name: 'Shubham Kumar',
    email: 'shubham@company.com',
    phone: '+91 98765 43210',
    department: 'Engineering',
    position: 'Senior Developer',
    status: 'active',
    enrolledDate: '2023-01-15',
    lastSeen: '2 minutes ago',
    totalDetections: 1247,
    locationsVisited: 8,
    averageConfidence: '96.8%',
    riskLevel: 'low',
    images: [
      generateAvatar('Shubham'),
      generateAvatar('Shubham2'),
      generateAvatar('Shubham3')
    ],
    recentDetections: [
      { location: 'Main Entrance', time: '2 min ago', confidence: '97.2%', camera: 'CAM-001' },
      { location: 'Office Floor 2', time: '45 min ago', confidence: '96.5%', camera: 'CAM-008' },
      { location: 'Cafeteria', time: '2 hours ago', confidence: '95.8%', camera: 'CAM-012' }
    ],
    locationHistory: [
      { location: 'Main Entrance', visits: 89, lastVisit: '2 min ago' },
      { location: 'Office Floor 2', visits: 156, lastVisit: '45 min ago' },
      { location: 'Cafeteria', visits: 67, lastVisit: '2 hours ago' },
      { location: 'Meeting Room A', visits: 23, lastVisit: '1 day ago' }
    ]
  },
  {
    id: 'EMP002',
    name: 'Priya Singh',
    email: 'priya@company.com',
    phone: '+91 98765 43211',
    department: 'Marketing',
    position: 'Marketing Manager',
    status: 'active',
    enrolledDate: '2023-02-20',
    lastSeen: '15 minutes ago',
    totalDetections: 892,
    locationsVisited: 6,
    averageConfidence: '94.2%',
    riskLevel: 'low',
    images: [
      generateAvatar('Priya'),
      generateAvatar('Priya2')
    ],
    recentDetections: [
      { location: 'Reception', time: '15 min ago', confidence: '94.8%', camera: 'CAM-002' },
      { location: 'Meeting Room B', time: '1 hour ago', confidence: '93.2%', camera: 'CAM-015' }
    ],
    locationHistory: [
      { location: 'Reception', visits: 45, lastVisit: '15 min ago' },
      { location: 'Meeting Room B', visits: 78, lastVisit: '1 hour ago' },
      { location: 'Office Floor 3', visits: 134, lastVisit: '3 hours ago' }
    ]
  },
  {
    id: 'EMP003',
    name: 'Rajesh Patel',
    email: 'rajesh@company.com',
    phone: '+91 98765 43212',
    department: 'Security',
    position: 'Security Manager',
    status: 'active',
    enrolledDate: '2022-11-10',
    lastSeen: '1 hour ago',
    totalDetections: 2156,
    locationsVisited: 12,
    averageConfidence: '98.1%',
    riskLevel: 'high',
    images: [
      generateAvatar('Rajesh'),
      generateAvatar('Rajesh2'),
      generateAvatar('Rajesh3'),
      generateAvatar('Rajesh4')
    ],
    recentDetections: [
      { location: 'Security Office', time: '1 hour ago', confidence: '98.9%', camera: 'CAM-020' },
      { location: 'Main Entrance', time: '2 hours ago', confidence: '97.8%', camera: 'CAM-001' }
    ],
    locationHistory: [
      { location: 'Security Office', visits: 234, lastVisit: '1 hour ago' },
      { location: 'Main Entrance', visits: 189, lastVisit: '2 hours ago' },
      { location: 'Parking Area', visits: 145, lastVisit: '4 hours ago' }
    ]
  },
  {
    id: 'EMP004',
    name: 'Sarah Johnson',
    email: 'sarah@company.com',
    phone: '+91 98765 43213',
    department: 'HR',
    position: 'HR Director',
    status: 'active',
    enrolledDate: '2023-03-05',
    lastSeen: '30 minutes ago',
    totalDetections: 654,
    locationsVisited: 5,
    averageConfidence: '92.4%',
    riskLevel: 'medium',
    images: [
      generateAvatar('Sarah'),
      generateAvatar('Sarah2')
    ],
    recentDetections: [
      { location: 'HR Office', time: '30 min ago', confidence: '93.1%', camera: 'CAM-018' },
      { location: 'Conference Room', time: '2 hours ago', confidence: '91.7%', camera: 'CAM-025' }
    ],
    locationHistory: [
      { location: 'HR Office', visits: 123, lastVisit: '30 min ago' },
      { location: 'Conference Room', visits: 67, lastVisit: '2 hours ago' }
    ]
  }
];

export const systemHealth = [
  { name: "Camera Network", status: "Active", uptime: "99.8%" },
  { name: "Recognition Engine", status: "Active", uptime: "99.2%" },
  { name: "Database Connection", status: "Active", uptime: "100%" },
  { name: "Alert System", status: "Warning", uptime: "85.7%" }
];

export const topCameras = [
  { location: "Main Entrance", detections: 142, alerts: 3 },
  { location: "Parking Area", detections: 89, alerts: 1 },
  { location: "Reception", detections: 76, alerts: 0 },
  { location: "Side Gate", detections: 54, alerts: 2 },
  { location: "Cafeteria", detections: 42, alerts: 0 }
];

export const recentDetections = [
  {
    id: "#DET001",
    personName: "Shubham Kumar", 
    email: "shubham@company.com",
    location: "Main Entrance",
    timestamp: "01 Jan, 2024",
    confidence: "96.5%"
  },
  {
    id: "#DET002",
    personName: "Priya Singh",
    email: "priya@company.com", 
    location: "Parking Area",
    timestamp: "01 Jan, 2024",
    confidence: "94.2%"
  },
  {
    id: "#DET003",
    personName: "Rajesh Patel",
    email: "rajesh@company.com",
    location: "Side Gate",
    timestamp: "09 Dec, 2023", 
    confidence: "98.1%"
  },
  {
    id: "#DET004",
    personName: "Sarah Johnson",
    email: "sarah@company.com",
    location: "Reception",
    timestamp: "01 Jan, 2024",
    confidence: "87.3%"
  },
  {
    id: "#DET005",
    personName: "Mike Chen",
    email: "mike@company.com",
    location: "Lobby",
    timestamp: "06 Nov, 2023",
    confidence: "95.8%"
  },
  {
    id: "#DET006",
    personName: "Lisa Anderson",
    email: "lisa@company.com",
    location: "Cafeteria",
    timestamp: "01 Jan, 2024",
    confidence: "92.4%"
  },
  {
    id: "#DET007",
    personName: "David Kim",
    email: "david@company.com",
    location: "Office Floor 2",
    timestamp: "02 Oct, 2023",
    confidence: "89.7%"
  }
];

export const statsCards = [
  {
    title: "Active Cameras",
    value: "24",
    change: "+2",
    changeType: "positive",
    color: "from-blue-500 to-blue-600"
  },
  {
    title: "Enrolled Persons",
    value: "1,247",
    change: "+12",
    changeType: "positive",
    color: "from-emerald-500 to-emerald-600"
  },
  {
    title: "Today's Detections",
    value: "342",
    change: "+89",
    changeType: "positive",
    color: "from-purple-500 to-purple-600"
  },
  {
    title: "Active Alerts",
    value: "3",
    change: "-1",
    changeType: "negative",
    color: "from-red-500 to-red-600"
  }
];

// Analytics specific data
export const analyticsData = {
  overview: {
    totalDetections: 15847,
    uniquePersons: 1247,
    averageConfidence: 94.2,
    alertsTriggered: 127,
    trends: {
      detections: { value: 15.4, type: 'increase' },
      persons: { value: 8.2, type: 'increase' },
      confidence: { value: 2.1, type: 'increase' },
      alerts: { value: 12.8, type: 'decrease' }
    }
  },
  timeAnalytics: {
    peakHours: [
      { hour: '09:00', detections: 145, percentage: 58 },
      { hour: '12:00', detections: 189, percentage: 76 },
      { hour: '17:00', detections: 234, percentage: 94 },
      { hour: '18:00', detections: 198, percentage: 79 }
    ],
    weeklyPattern: [
      { day: 'Mon', detections: 892, confidence: 95.1 },
      { day: 'Tue', detections: 1043, confidence: 94.7 },
      { day: 'Wed', detections: 978, confidence: 93.8 },
      { day: 'Thu', detections: 1134, confidence: 95.3 },
      { day: 'Fri', detections: 1267, confidence: 94.9 },
      { day: 'Sat', detections: 456, confidence: 92.4 },
      { day: 'Sun', detections: 321, confidence: 91.8 }
    ],
    monthlyTrend: [
      { month: 'Jan', detections: 12456, alerts: 45 },
      { month: 'Feb', detections: 13892, alerts: 38 },
      { month: 'Mar', detections: 15234, alerts: 52 },
      { month: 'Apr', detections: 14567, alerts: 43 },
      { month: 'May', detections: 16789, alerts: 61 },
      { month: 'Jun', detections: 15847, alerts: 48 }
    ]
  },
  locationAnalytics: [
    { 
      location: 'Main Entrance', 
      detections: 2847, 
      uniquePersons: 456, 
      avgConfidence: 96.2, 
      alerts: 12,
      cameraId: 'CAM-001',
      status: 'active'
    },
    { 
      location: 'Parking Area', 
      detections: 1923, 
      uniquePersons: 334, 
      avgConfidence: 94.8, 
      alerts: 8,
      cameraId: 'CAM-002',
      status: 'active'
    },
    { 
      location: 'Reception', 
      detections: 1675, 
      uniquePersons: 289, 
      avgConfidence: 93.4, 
      alerts: 3,
      cameraId: 'CAM-003',
      status: 'active'
    },
    { 
      location: 'Office Floor 2', 
      detections: 1234, 
      uniquePersons: 198, 
      avgConfidence: 95.7, 
      alerts: 2,
      cameraId: 'CAM-008',
      status: 'active'
    },
    { 
      location: 'Cafeteria', 
      detections: 987, 
      uniquePersons: 167, 
      avgConfidence: 92.1, 
      alerts: 1,
      cameraId: 'CAM-012',
      status: 'active'
    }
  ],
  confidenceDistribution: [
    { range: '90-95%', count: 4567, percentage: 38.2, color: 'yellow' },
    { range: '95-98%', count: 5234, percentage: 43.8, color: 'emerald' },
    { range: '98-100%', count: 2156, percentage: 18.0, color: 'blue' }
  ],
  personActivity: [
    { 
      name: 'Shubham Kumar', 
      detections: 234, 
      locations: 8, 
      avgConfidence: 96.8, 
      lastSeen: '2 min ago',
      department: 'Engineering',
      riskLevel: 'low'
    },
    { 
      name: 'Rajesh Patel', 
      detections: 189, 
      locations: 12, 
      avgConfidence: 98.1, 
      lastSeen: '1 hour ago',
      department: 'Security',
      riskLevel: 'high'
    },
    { 
      name: 'Priya Singh', 
      detections: 156, 
      locations: 6, 
      avgConfidence: 94.2, 
      lastSeen: '15 min ago',
      department: 'Marketing',
      riskLevel: 'low'
    },
    { 
      name: 'Sarah Johnson', 
      detections: 134, 
      locations: 5, 
      avgConfidence: 92.4, 
      lastSeen: '30 min ago',
      department: 'HR',
      riskLevel: 'medium'
    }
  ],
  alertAnalytics: [
    { type: 'High Priority Person', count: 45, percentage: 35.4, trend: 'stable' },
    { type: 'Unauthorized Access', count: 32, percentage: 25.2, trend: 'decrease' },
    { type: 'Low Confidence Detection', count: 28, percentage: 22.0, trend: 'increase' },
    { type: 'Multiple Person Alert', count: 22, percentage: 17.3, trend: 'stable' }
  ],
  systemMetrics: {
    processingTime: { average: 245, min: 120, max: 450, unit: 'ms' },
    accuracy: { current: 94.2, target: 95.0, trend: 'improving' },
    uptime: { percentage: 99.7, downtime: '2.5 hours', lastIncident: '3 days ago' },
    storage: { used: 2.4, total: 10.0, unit: 'TB', growthRate: '12GB/day' }
  }
};