export type CapacityStatus = "SEATS_AVAILABLE" | "STANDING_ONLY" | "FULL";

export interface TransitStop {
  id: string;
  name: string;
  landmark: string;
  scheduledTime: string;
  estimatedArrival: string;
  delayMinutes: number; // 0 for on-time, positive for delayed, negative for early
  status: "PASSED" | "APPROACHING" | "SCHEDULED";
  lat?: number;
  lng?: number;
}

export interface TransitVehicle {
  busNumber: string;
  model: string;
  licensePlate: string;
  driverName: string;
  driverPhone: string;
  totalSeats: number;
  occupiedSeats: number;
  capacityStatus: CapacityStatus;
  hasAC: boolean;
  hasWifi: boolean;
  speedKmh: number;
  lastPingSecondsAgo: number;
}

export type RouteCategory = "CITY_ROUTE" | "CAMPUS_SHUTTLE";
export type RouteDirection = "INBOUND_MORNING" | "OUTBOUND_EVENING" | "CIRCULAR_LOOP";

export interface TransitRoute {
  id: string;
  category: RouteCategory;
  direction: RouteDirection;
  name: string;
  subtitle: string;
  bus: TransitVehicle;
  stops: TransitStop[];
  departureTime: string;
  expectedArrivalTime: string;
  currentLocationDesc: string;
  overallStatus: "ON_TIME" | "MINOR_DELAY" | "DISRUPTED";
  delaySummary: string;
  operatingDays: string;
}

export interface DisruptionAlert {
  id: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  category: "ROUTE_DEVIATION" | "MAINTENANCE" | "WEATHER_DELAY";
  title: string;
  affectedRoutes: string[];
  message: string;
  timestamp: string;
  actionRecommendation: string;
}

export const TRANSIT_ALERTS: DisruptionAlert[] = [
  {
    id: "alert-farid-town-1",
    severity: "WARNING",
    category: "ROUTE_DEVIATION",
    title: "Farid Town Main Boulevard Construction — Service Lane Reroute",
    affectedRoutes: ["Bus #04"],
    message:
      "Municipal water pipeline repairs near Farid Town Gol Chowk have temporarily blocked the central carriageway. Bus #04 is utilizing the South Service Lane.",
    timestamp: "Updated 12 mins ago",
    actionRecommendation:
      "Please wait at the South Service Lane curb opposite National Bank. Expect approximately +4 to +6 minutes delay."
  },
  {
    id: "alert-shuttle-s4",
    severity: "INFO",
    category: "MAINTENANCE",
    title: "Shuttle #S-04 Scheduled Preventive Service — Backup Deployed",
    affectedRoutes: ["Shuttle #S-01"],
    message:
      "Intra-day Coaster #S-04 is in the departmental workshop for oil and braking maintenance. Backup 30-seater Shuttle #S-06 is actively running the loop.",
    timestamp: "Updated 45 mins ago",
    actionRecommendation:
      "Look for Shuttle #S-06 with the blue 'Loop Alpha' digital dashboard sign. Headway frequency remains 15 minutes."
  },
  {
    id: "alert-highway-fog",
    severity: "INFO",
    category: "WEATHER_DELAY",
    title: "Chichawatni & Harappa Highway Morning Headway Buffer",
    affectedRoutes: ["Bus #12"],
    message:
      "Highway Patrol reports localized morning mist along the canal corridors. Speed has been capped at 50 km/h for student safety.",
    timestamp: "Updated 1 hour ago",
    actionRecommendation:
      "Buses from Chichawatni may arrive 5–8 minutes later than schedule. Check live ETA before heading to the stop."
  }
];

export interface SimpleBusStop {
  id: string;
  name: string;
  time: string;
}

export interface PlannedCityBus {
  id: string;
  busName: string;
  city: "Sahiwal" | "Chichawatni";
  routeTitle: string;
  stops: SimpleBusStop[];
}

export type ShuttleScheduleKey = "regular" | "exams" | "ramzan" | "sports";
export type ShuttleDirectionKey = "from_university" | "to_university";

export interface ShuttleScheduleRouteSet {
  key: ShuttleScheduleKey;
  label: string;
  subtitle: string;
  directions: Record<ShuttleDirectionKey, PlannedCityBus[]>;
}

export const PLANNED_CITY_BUSES: PlannedCityBus[] = [
  {
    id: "planned-bus-1",
    busName: "Bus #01",
    city: "Sahiwal",
    routeTitle: "Jeewan City · Stadium Road",
    stops: [
      { id: "pb1-1", name: "Jeewan City", time: "10:00 AM" },
      { id: "pb1-2", name: "College Chowk", time: "10:15 AM" },
      { id: "pb1-3", name: "Faridia Park", time: "10:30 AM" },
      { id: "pb1-4", name: "Civil Hospital", time: "10:45 AM" },
      { id: "pb1-5", name: "GT Road", time: "11:00 AM" },
      { id: "pb1-6", name: "Stadium Road", time: "11:15 AM" }
    ]
  },
  {
    id: "planned-bus-2",
    busName: "Bus #02",
    city: "Sahiwal",
    routeTitle: "Pakka Anna · Farid Town Point",
    stops: [
      { id: "pb2-1", name: "Pakka Anna", time: "07:25 AM" },
      { id: "pb2-2", name: "Sahiwal Adda", time: "07:40 AM" },
      { id: "pb2-3", name: "Railway Station", time: "07:55 AM" },
      { id: "pb2-4", name: "Farid Town Point", time: "08:10 AM" },
      { id: "pb2-5", name: "Jinnah Hall Chowk", time: "08:20 AM" },
      { id: "pb2-6", name: "Campus Terminal", time: "08:30 AM" }
    ]
  },
  {
    id: "planned-bus-3",
    busName: "Bus #03",
    city: "Sahiwal",
    routeTitle: "Mall Road · Bypass Line",
    stops: [
      { id: "pb3-1", name: "Mall Road GPO", time: "07:30 AM" },
      { id: "pb3-2", name: "High Court Point", time: "07:45 AM" },
      { id: "pb3-3", name: "Canal Bridge", time: "08:00 AM" },
      { id: "pb3-4", name: "Girls Hostel Gate", time: "08:15 AM" },
      { id: "pb3-5", name: "Bypass Chowk", time: "08:25 AM" },
      { id: "pb3-6", name: "Campus Terminal", time: "08:35 AM" }
    ]
  },
  {
    id: "planned-bus-cw-1",
    busName: "Bus #04",
    city: "Chichawatni",
    routeTitle: "Chichawatni · Harappa Express",
    stops: [
      { id: "pbc-1", name: "Chichawatni Adda", time: "07:00 AM" },
      { id: "pbc-2", name: "Harappa Station", time: "07:25 AM" },
      { id: "pbc-3", name: "N-5 Bypass", time: "07:50 AM" },
      { id: "pbc-4", name: "Campus Terminal", time: "08:20 AM" }
    ]
  }
];

export const SHUTTLE_SCHEDULE_SETS: ShuttleScheduleRouteSet[] = [
  {
    key: "regular",
    label: "Regular Days",
    subtitle: "Regular Days schedule",
    directions: {
      from_university: [
        {
          id: "reg-out-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Afternoon Departure — City Line",
          stops: [
            { id: "ro1-1", name: "University Gate 1", time: "01:30 PM" },
            { id: "ro1-2", name: "Farid Town Point", time: "01:45 PM" },
            { id: "ro1-3", name: "Jeewan City", time: "02:00 PM" },
            { id: "ro1-4", name: "College Chowk", time: "02:10 PM" },
            { id: "ro1-5", name: "Faridia Park", time: "02:20 PM" },
            { id: "ro1-6", name: "Stadium Road", time: "02:30 PM" }
          ]
        },
        {
          id: "reg-out-2",
          busName: "Bus #02",
          city: "Sahiwal",
          routeTitle: "Evening Departure — Mall Line",
          stops: [
            { id: "ro2-1", name: "University Gate 1", time: "04:00 PM" },
            { id: "ro2-2", name: "Girls Hostel Gate", time: "04:10 PM" },
            { id: "ro2-3", name: "High Court Point", time: "04:22 PM" },
            { id: "ro2-4", name: "Civil Hospital", time: "04:32 PM" },
            { id: "ro2-5", name: "Railway Station", time: "04:42 PM" },
            { id: "ro2-6", name: "Sahiwal Adda", time: "04:55 PM" }
          ]
        }
      ],
      to_university: [
        {
          id: "reg-in-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Morning Arrival — City Line",
          stops: [
            { id: "ri1-1", name: "Jeewan City", time: "07:30 AM" },
            { id: "ri1-2", name: "College Chowk", time: "07:42 AM" },
            { id: "ri1-3", name: "Faridia Park", time: "07:52 AM" },
            { id: "ri1-4", name: "Farid Town Point", time: "08:05 AM" },
            { id: "ri1-5", name: "GT Road", time: "08:15 AM" },
            { id: "ri1-6", name: "University Gate 1", time: "08:25 AM" }
          ]
        },
        {
          id: "reg-in-2",
          busName: "Bus #02",
          city: "Sahiwal",
          routeTitle: "Morning Arrival — Bypass Line",
          stops: [
            { id: "ri2-1", name: "Pakka Anna", time: "07:20 AM" },
            { id: "ri2-2", name: "Sahiwal Adda", time: "07:35 AM" },
            { id: "ri2-3", name: "Railway Station", time: "07:50 AM" },
            { id: "ri2-4", name: "Civil Hospital", time: "08:02 AM" },
            { id: "ri2-5", name: "Stadium Road", time: "08:15 AM" },
            { id: "ri2-6", name: "University Gate 1", time: "08:25 AM" }
          ]
        }
      ]
    }
  },
  {
    key: "exams",
    label: "During Exams",
    subtitle: "During Exams schedule",
    directions: {
      from_university: [
        {
          id: "ex-out-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Paper Dispersal — Shift 1",
          stops: [
            { id: "eo1-1", name: "University Gate 1", time: "12:15 PM" },
            { id: "eo1-2", name: "Farid Town Point", time: "12:30 PM" },
            { id: "eo1-3", name: "Jeewan City", time: "12:45 PM" },
            { id: "eo1-4", name: "College Chowk", time: "12:55 PM" }
          ]
        },
        {
          id: "ex-out-2",
          busName: "Bus #02",
          city: "Sahiwal",
          routeTitle: "Paper Dispersal — Shift 2",
          stops: [
            { id: "eo2-1", name: "University Gate 1", time: "03:45 PM" },
            { id: "eo2-2", name: "Girls Hostel Gate", time: "03:55 PM" },
            { id: "eo2-3", name: "Civil Hospital", time: "04:10 PM" },
            { id: "eo2-4", name: "Sahiwal Adda", time: "04:25 PM" }
          ]
        }
      ],
      to_university: [
        {
          id: "ex-in-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Morning Exam Arrival",
          stops: [
            { id: "ei1-1", name: "Jeewan City", time: "08:00 AM" },
            { id: "ei1-2", name: "Farid Town Point", time: "08:15 AM" },
            { id: "ei1-3", name: "College Chowk", time: "08:25 AM" },
            { id: "ei1-4", name: "University Gate 1", time: "08:40 AM" }
          ]
        }
      ]
    }
  },
  {
    key: "ramzan",
    label: "During Ramzan",
    subtitle: "During Ramzan schedule",
    directions: {
      from_university: [
        {
          id: "rm-out-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Early Ramzan Return",
          stops: [
            { id: "rmo-1", name: "University Gate 1", time: "01:00 PM" },
            { id: "rmo-2", name: "Farid Town Point", time: "01:15 PM" },
            { id: "rmo-3", name: "Jeewan City", time: "01:30 PM" },
            { id: "rmo-4", name: "Sahiwal Adda", time: "01:45 PM" }
          ]
        }
      ],
      to_university: [
        {
          id: "rm-in-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Morning Ramzan Pickup",
          stops: [
            { id: "rmi-1", name: "Jeewan City", time: "07:45 AM" },
            { id: "rmi-2", name: "Faridia Park", time: "08:00 AM" },
            { id: "rmi-3", name: "Farid Town Point", time: "08:12 AM" },
            { id: "rmi-4", name: "University Gate 1", time: "08:25 AM" }
          ]
        }
      ]
    }
  },
  {
    key: "sports",
    label: "During Sports Week",
    subtitle: "During Sports Week schedule",
    directions: {
      from_university: [
        {
          id: "sp-out-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Post-Match Departure",
          stops: [
            { id: "spo-1", name: "Sports Complex Gate", time: "04:30 PM" },
            { id: "spo-2", name: "University Gate 1", time: "04:40 PM" },
            { id: "spo-3", name: "Farid Town Point", time: "04:55 PM" },
            { id: "spo-4", name: "Stadium Road", time: "05:10 PM" }
          ]
        }
      ],
      to_university: [
        {
          id: "sp-in-1",
          busName: "Bus #01",
          city: "Sahiwal",
          routeTitle: "Morning Sports Ground Drop",
          stops: [
            { id: "spi-1", name: "Jeewan City", time: "07:00 AM" },
            { id: "spi-2", name: "College Chowk", time: "07:12 AM" },
            { id: "spi-3", name: "Sports Complex Gate", time: "07:25 AM" },
            { id: "spi-4", name: "University Gate 1", time: "07:30 AM" }
          ]
        }
      ]
    }
  }
];

export const TRANSIT_ROUTES: TransitRoute[] = [
  // ================= 1. CITY ROUTE NETWORKS =================
  {
    id: "city-bus-04",
    category: "CITY_ROUTE",
    direction: "INBOUND_MORNING",
    name: "Farid Town & Girls Hostel Express",
    subtitle: "High-density morning commuter service from Farid Town residential sectors",
    bus: {
      busNumber: "Bus #04",
      model: "Hino Blue Ribbon 52-Seater Coach",
      licensePlate: "SWL-7842",
      driverName: "Tariq Mehmood",
      driverPhone: "+92 300 7981245",
      totalSeats: 52,
      occupiedSeats: 36,
      capacityStatus: "SEATS_AVAILABLE",
      hasAC: true,
      hasWifi: true,
      speedKmh: 34,
      lastPingSecondsAgo: 6
    },
    departureTime: "07:30 AM",
    expectedArrivalTime: "08:28 AM",
    currentLocationDesc: "Approaching Farid Town Point (1.1 km away)",
    overallStatus: "MINOR_DELAY",
    delaySummary: "Running +4m behind schedule due to service road diversion near Gol Chowk",
    operatingDays: "Monday – Friday",
    stops: [
      {
        id: "stop-ft-1",
        name: "Farid Town Gol Chowk",
        landmark: "Main Market Commercial Area",
        scheduledTime: "07:35 AM",
        estimatedArrival: "07:35 AM",
        delayMinutes: 0,
        status: "PASSED"
      },
      {
        id: "stop-ft-2",
        name: "Farid Town Point (Main Pickup)",
        landmark: "Opposite National Bank & Park Gate",
        scheduledTime: "07:45 AM",
        estimatedArrival: "07:49 AM",
        delayMinutes: 4,
        status: "APPROACHING"
      },
      {
        id: "stop-ft-3",
        name: "Jinnah Hall Chowk",
        landmark: "Under the Jinnah Flyover Intersection",
        scheduledTime: "07:55 AM",
        estimatedArrival: "08:00 AM",
        delayMinutes: 5,
        status: "SCHEDULED"
      },
      {
        id: "stop-ft-4",
        name: "Fatima Jinnah Girls Hostel",
        landmark: "Hostel Security Gate 2",
        scheduledTime: "08:10 AM",
        estimatedArrival: "08:14 AM",
        delayMinutes: 4,
        status: "SCHEDULED"
      },
      {
        id: "stop-ft-5",
        name: "Campus Main Terminal (Gate 1)",
        landmark: "University Transportation Bay 1",
        scheduledTime: "08:25 AM",
        estimatedArrival: "08:28 AM",
        delayMinutes: 3,
        status: "SCHEDULED"
      }
    ]
  },
  {
    id: "city-bus-08",
    category: "CITY_ROUTE",
    direction: "INBOUND_MORNING",
    name: "Mall Road & Civil Lines Express",
    subtitle: "Downtown commercial corridor via High Court and College Road",
    bus: {
      busNumber: "Bus #08",
      model: "Isuzu Forward 52-Seater Coach",
      licensePlate: "SWL-5519",
      driverName: "Muhammad Ashraf",
      driverPhone: "+92 321 6854120",
      totalSeats: 52,
      occupiedSeats: 48,
      capacityStatus: "STANDING_ONLY",
      hasAC: true,
      hasWifi: false,
      speedKmh: 42,
      lastPingSecondsAgo: 11
    },
    departureTime: "07:20 AM",
    expectedArrivalTime: "08:26 AM",
    currentLocationDesc: "Passing High Court Chowk heading towards College Road",
    overallStatus: "ON_TIME",
    delaySummary: "Operating on exact timetable schedule with nominal traffic flow",
    operatingDays: "Monday – Friday",
    stops: [
      {
        id: "stop-mr-1",
        name: "General Bus Stand Terminal",
        landmark: "South Depot Gate 3",
        scheduledTime: "07:20 AM",
        estimatedArrival: "07:20 AM",
        delayMinutes: 0,
        status: "PASSED"
      },
      {
        id: "stop-mr-2",
        name: "Mall Road GPO Chowk",
        landmark: "Opposite General Post Office",
        scheduledTime: "07:35 AM",
        estimatedArrival: "07:36 AM",
        delayMinutes: 1,
        status: "PASSED"
      },
      {
        id: "stop-mr-3",
        name: "High Court & Bar Council Point",
        landmark: "Judicial Complex Main Gate",
        scheduledTime: "07:50 AM",
        estimatedArrival: "07:51 AM",
        delayMinutes: 1,
        status: "APPROACHING"
      },
      {
        id: "stop-mr-4",
        name: "College Road Point",
        landmark: "Near Govt. Post Graduate College",
        scheduledTime: "08:05 AM",
        estimatedArrival: "08:06 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      },
      {
        id: "stop-mr-5",
        name: "Campus North Terminal (Gate 2)",
        landmark: "Engineering & Science Bay",
        scheduledTime: "08:25 AM",
        estimatedArrival: "08:26 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      }
    ]
  },
  {
    id: "city-bus-15",
    category: "CITY_ROUTE",
    direction: "INBOUND_MORNING",
    name: "Canal Line & Harappa Feeder",
    subtitle: "Regional intercity commuter line along Lower Bari Doab Canal",
    bus: {
      busNumber: "Bus #15",
      model: "Daewoo Express 52-Seater Coach",
      licensePlate: "SWL-9923",
      driverName: "Rashid Minhas",
      driverPhone: "+92 333 4567891",
      totalSeats: 52,
      occupiedSeats: 52,
      capacityStatus: "FULL",
      hasAC: true,
      hasWifi: true,
      speedKmh: 48,
      lastPingSecondsAgo: 4
    },
    departureTime: "07:15 AM",
    expectedArrivalTime: "08:31 AM",
    currentLocationDesc: "Crossing Lower Bari Doab Canal Bridge",
    overallStatus: "MINOR_DELAY",
    delaySummary: "Full passenger capacity with +6m fog safety headway speed",
    operatingDays: "Monday – Friday",
    stops: [
      {
        id: "stop-cl-1",
        name: "Harappa Station Point",
        landmark: "Heritage Railway Crossing",
        scheduledTime: "07:15 AM",
        estimatedArrival: "07:15 AM",
        delayMinutes: 0,
        status: "PASSED"
      },
      {
        id: "stop-cl-2",
        name: "Lower Bari Doab Canal Bridge",
        landmark: "Canal Bank Irrigation Rest House",
        scheduledTime: "07:40 AM",
        estimatedArrival: "07:46 AM",
        delayMinutes: 6,
        status: "APPROACHING"
      },
      {
        id: "stop-cl-3",
        name: "Sahiwal Bypass Interchange",
        landmark: "National Highway N-5 Junction",
        scheduledTime: "08:05 AM",
        estimatedArrival: "08:12 AM",
        delayMinutes: 7,
        status: "SCHEDULED"
      },
      {
        id: "stop-cl-4",
        name: "Campus Main Terminal (Gate 1)",
        landmark: "Central University Concourse",
        scheduledTime: "08:25 AM",
        estimatedArrival: "08:31 AM",
        delayMinutes: 6,
        status: "SCHEDULED"
      }
    ]
  },
  {
    id: "city-bus-04-outbound",
    category: "CITY_ROUTE",
    direction: "OUTBOUND_EVENING",
    name: "Farid Town Evening Outbound",
    subtitle: "Afternoon student dispersal back to Farid Town residential sectors",
    bus: {
      busNumber: "Bus #04 (Outbound)",
      model: "Hino Blue Ribbon 52-Seater Coach",
      licensePlate: "SWL-7842",
      driverName: "Tariq Mehmood",
      driverPhone: "+92 300 7981245",
      totalSeats: 52,
      occupiedSeats: 12,
      capacityStatus: "SEATS_AVAILABLE",
      hasAC: true,
      hasWifi: true,
      speedKmh: 0,
      lastPingSecondsAgo: 15
    },
    departureTime: "03:45 PM",
    expectedArrivalTime: "04:35 PM",
    currentLocationDesc: "Parked at Campus Terminal Bay 1 boarding students",
    overallStatus: "ON_TIME",
    delaySummary: "Scheduled departure at 03:45 PM following Slot 5 completion",
    operatingDays: "Monday – Friday",
    stops: [
      {
        id: "stop-out-1",
        name: "Campus Main Terminal (Gate 1)",
        landmark: "Bay 1 Boarding Platform",
        scheduledTime: "03:45 PM",
        estimatedArrival: "03:45 PM",
        delayMinutes: 0,
        status: "APPROACHING"
      },
      {
        id: "stop-out-2",
        name: "Fatima Jinnah Girls Hostel",
        landmark: "Hostel Security Gate 2 Drop-off",
        scheduledTime: "04:00 PM",
        estimatedArrival: "04:00 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-out-3",
        name: "Jinnah Hall Chowk",
        landmark: "Civil Lines Service Road",
        scheduledTime: "04:15 PM",
        estimatedArrival: "04:15 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-out-4",
        name: "Farid Town Point",
        landmark: "Opposite National Bank & Park Gate",
        scheduledTime: "04:25 PM",
        estimatedArrival: "04:25 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-out-5",
        name: "Farid Town Gol Chowk Terminal",
        landmark: "Commercial Market Roundabout",
        scheduledTime: "04:35 PM",
        estimatedArrival: "04:35 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      }
    ]
  },

  // ================= 2. INTER-CAMPUS / INTRA-DAY SHUTTLES =================
  {
    id: "shuttle-alpha",
    category: "CAMPUS_SHUTTLE",
    direction: "CIRCULAR_LOOP",
    name: "Loop Alpha: Hostels ↔ Library ↔ CS Block",
    subtitle: "High-frequency 15-minute inter-departmental shuttle connecting living & study centers",
    bus: {
      busNumber: "Shuttle #S-01",
      model: "Toyota Coaster AC 30-Seater",
      licensePlate: "SWL-2041",
      driverName: "Ghulam Rasool",
      driverPhone: "+92 345 8899123",
      totalSeats: 30,
      occupiedSeats: 16,
      capacityStatus: "SEATS_AVAILABLE",
      hasAC: true,
      hasWifi: true,
      speedKmh: 24,
      lastPingSecondsAgo: 3
    },
    departureTime: "Every 15 min",
    expectedArrivalTime: "Continuous Loop",
    currentLocationDesc: "Departing Boys Hostel Complex towards Central Library",
    overallStatus: "ON_TIME",
    delaySummary: "Operating on 15-minute interval clock with zero reported delays",
    operatingDays: "Monday – Saturday (08:00 AM – 06:00 PM)",
    stops: [
      {
        id: "stop-sa-1",
        name: "Boys Hostels Complex (Allama Iqbal Hall)",
        landmark: "Hostel Dining Hall Entrance",
        scheduledTime: "10:00 AM",
        estimatedArrival: "10:00 AM",
        delayMinutes: 0,
        status: "PASSED"
      },
      {
        id: "stop-sa-2",
        name: "Faculty & Staff Residential Enclave",
        landmark: "Staff Club Roundabout",
        scheduledTime: "10:05 AM",
        estimatedArrival: "10:05 AM",
        delayMinutes: 0,
        status: "APPROACHING"
      },
      {
        id: "stop-sa-3",
        name: "Central Library & Block D",
        landmark: "Silent Study Wing Portico",
        scheduledTime: "10:10 AM",
        estimatedArrival: "10:11 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      },
      {
        id: "stop-sa-4",
        name: "CS & Software Block C Plaza",
        landmark: "Main Quadrangle Cafeteria",
        scheduledTime: "10:15 AM",
        estimatedArrival: "10:16 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      }
    ]
  },
  {
    id: "shuttle-beta",
    category: "CAMPUS_SHUTTLE",
    direction: "CIRCULAR_LOOP",
    name: "Loop Beta: Sports Complex & Oval Athletic Shuttle",
    subtitle: "20-minute loop connecting Student Activity Center with athletic grounds & gym",
    bus: {
      busNumber: "Shuttle #S-02",
      model: "Toyota Coaster AC 28-Seater",
      licensePlate: "SWL-3390",
      driverName: "Sajid Ali",
      driverPhone: "+92 312 9900441",
      totalSeats: 28,
      occupiedSeats: 11,
      capacityStatus: "SEATS_AVAILABLE",
      hasAC: true,
      hasWifi: true,
      speedKmh: 28,
      lastPingSecondsAgo: 8
    },
    departureTime: "Every 20 min",
    expectedArrivalTime: "Continuous Loop",
    currentLocationDesc: "Arriving at Student Activity Center (SAC)",
    overallStatus: "ON_TIME",
    delaySummary: "Operating normally; frequent sports week team transit",
    operatingDays: "Monday – Saturday (09:00 AM – 05:30 PM)",
    stops: [
      {
        id: "stop-sb-1",
        name: "Main Campus Administration Plaza",
        landmark: "Flagpole & Central Fountain",
        scheduledTime: "10:15 AM",
        estimatedArrival: "10:15 AM",
        delayMinutes: 0,
        status: "PASSED"
      },
      {
        id: "stop-sb-2",
        name: "Student Activity Center (SAC)",
        landmark: "Cafeteria Terrace & Indoor Sports",
        scheduledTime: "10:22 AM",
        estimatedArrival: "10:22 AM",
        delayMinutes: 0,
        status: "APPROACHING"
      },
      {
        id: "stop-sb-3",
        name: "Gymnasium & Swimming Complex",
        landmark: "Sports Pavilion Entrance",
        scheduledTime: "10:28 AM",
        estimatedArrival: "10:29 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      },
      {
        id: "stop-sb-4",
        name: "Main Oval Cricket & Football Arena",
        landmark: "Spectator Grandstand East Gate",
        scheduledTime: "10:35 AM",
        estimatedArrival: "10:36 AM",
        delayMinutes: 1,
        status: "SCHEDULED"
      }
    ]
  },
  {
    id: "shuttle-night-owl",
    category: "CAMPUS_SHUTTLE",
    direction: "CIRCULAR_LOOP",
    name: "Night Owl Research Shuttle (Evening Service)",
    subtitle: "Safe late-evening transit between Research Labs, Library, and Hostels",
    bus: {
      busNumber: "Shuttle #S-03",
      model: "Toyota HiAce 16-Seater AC Van",
      licensePlate: "SWL-1102",
      driverName: "Zahid Qureshi",
      driverPhone: "+92 301 5566778",
      totalSeats: 16,
      occupiedSeats: 4,
      capacityStatus: "SEATS_AVAILABLE",
      hasAC: true,
      hasWifi: true,
      speedKmh: 0,
      lastPingSecondsAgo: 25
    },
    departureTime: "Every 30 min (06:00 PM – 09:30 PM)",
    expectedArrivalTime: "Evening Loop",
    currentLocationDesc: "Staged at Central Library Portico for evening scholars",
    overallStatus: "ON_TIME",
    delaySummary: "Ready for evening service; security officer onboard each run",
    operatingDays: "Monday – Friday (06:00 PM – 09:30 PM)",
    stops: [
      {
        id: "stop-no-1",
        name: "Central Library Portico",
        landmark: "Main Entrance Porch",
        scheduledTime: "06:00 PM",
        estimatedArrival: "06:00 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-no-2",
        name: "Engineering & AI Labs Gate",
        landmark: "Robotics Research Wing",
        scheduledTime: "06:10 PM",
        estimatedArrival: "06:10 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-no-3",
        name: "Fatima Jinnah Girls Hostel",
        landmark: "Hostel Security Gate 1",
        scheduledTime: "06:20 PM",
        estimatedArrival: "06:20 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      },
      {
        id: "stop-no-4",
        name: "Allama Iqbal Boys Hostel",
        landmark: "Hostel Main Arch",
        scheduledTime: "06:30 PM",
        estimatedArrival: "06:30 PM",
        delayMinutes: 0,
        status: "SCHEDULED"
      }
    ]
  }
];
