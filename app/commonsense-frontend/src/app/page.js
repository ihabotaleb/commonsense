'use client';

import { useEffect, useState } from "react";

export default function Home() {
  const API_URL = 'https://z9k57bg2be.execute-api.us-east-1.amazonaws.com/charlie/occupancy';

  const [data, setData] = useState({});
  const [processedData, setProcessedData] = useState([]);
  const [numZones, setNumZones] = useState(0);
  const [numCameras, setNumCameras] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        const jsonData = await response.json();
        setData(jsonData["items"]);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    setProcessedData([]);
    const processData = () => {
      setNumCameras(data.length);
      for (let i = 0; i < data.length; i++) {
        let cid = data[i]['camera_id'];
        let processedDataEntry = { camera_id: cid };
        let occupancy = [];
        let segmentation = [];
        const keys = Object.keys(data[i]['occupancy']);
        setNumZones(keys.length);
        for (let j = 0; j < keys.length; j++) {
          occupancy.push(data[i]['occupancy'][keys[j]]['score']);
          segmentation.push(Object.entries(data[i]['occupancy'][keys[j]]['cnn']));
        }
        processedDataEntry['occupancy'] = occupancy;
        processedDataEntry['segmentation'] = segmentation;
        setProcessedData(processedData => [...processedData, processedDataEntry]);
      }
    };

    processData();
  }, [data]);

  const calculateCompleteScore = (zone) => {
    let score = 0;
    processedData.forEach(camera => {
      score += camera['occupancy'][zone];
    })
    return Math.round(score / numCameras * 105, 2);
  };


  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
       <pre>
      <h2>CommonSense</h2>

          <div className="mb-5">
            <p>Number of Cameras: {numCameras}</p>
            <p>Number of Zones: {numZones}</p>
          </div>
          <div className="mb-8">
            {[...Array(numZones).keys()].map(zone => {
              var considered = calculateCompleteScore(zone) > 50;
              return(
                <>
                {
                  considered ?  
                    <p className="bg-[#ec0000]">Zone {zone}: Occupied</p>
                    :
                    <p className="bg-[#ecec00]">Zone {zone}: Free</p>
                }
                </>
              )
            })}
    
          </div>
         {
            ([...Array(numZones).keys()].map(zone => {
              return (
                <>
                <p>{"Zone " + zone + " : " + calculateCompleteScore(zone)}%</p>
                <div className="ml-6">
                  {([...Array(numCameras).keys()]).map(camera => {
                    var score = processedData[camera]['occupancy'][zone];
                    score = Math.round(score * 100, 3);
                return(
                  <p>Camera {camera} : {score}%</p>
                )
                })}
                </div>
                </>
              )
            }))
          }</pre>
    </main>
  );
}

