export type JourneyOption = {
  mode: "walk" | "metro" | "auto";
  distance_m?: number;
  time_min: number;
  estimated?: boolean;
  metro_route?: string[];
  departure_distance_m?: number;
  arrival_distance_m?: number;
  metro_hops?: number;
  total_walk_distance_m?: number;
};

export type RouteTransition = {
  from: string;
  to: string;
  recommended: "walk" | "metro" | "auto";
  options: JourneyOption[];
};

export type MetroSegment = {
  line: string;
  stations: string[];
};

export type RouteStop = {
  pandal: string;
  metro_station: string;

  metro_route: string[];

  metro_segments: MetroSegment[];

  last_mile_transport: string;
  last_mile_distance_m: number;
  last_mile_time_min: number;

  google_maps_link: string;

  next_transition: RouteTransition | null;
};