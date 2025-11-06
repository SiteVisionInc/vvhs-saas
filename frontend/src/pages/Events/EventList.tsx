import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Event } from '../../types';

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'Date TBD';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return 'Invalid date';
  }
};

export const EventList: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await api.getEvents();
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Events</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {events.map((event) => (
          <div key={event.id} className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold mb-2">{event.title}</h3>
            <p className="text-gray-600 mb-2">{event.description}</p>
            <p className="text-sm text-gray-500">Date: {formatDate(event.event_date)}</p>
            <p className="text-sm text-gray-500">Location: {event.location}</p>
            <p className="text-sm text-gray-500 mt-2">
              Volunteers: {event.registered_volunteers} / {event.max_volunteers}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
