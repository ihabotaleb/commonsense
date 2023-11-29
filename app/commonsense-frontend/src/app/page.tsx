'use client';
import { useEffect, useState } from 'react';

import axios from 'axios';

export default function Home() {
  const API_URL = 'https://z9k57bg2be.execute-api.us-east-1.amazonaws.com/charlie/occupancy';

  const [jsonData, setJsonData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(API_URL, {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
        });
        setJsonData(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h2>CommonSense</h2>
      {/* Render the JSON data */}
      {jsonData && (
        <pre>{JSON.stringify(jsonData, null, 2)}</pre>
      )}
    </main>
  );
}
