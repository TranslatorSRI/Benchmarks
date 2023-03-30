import { useState, useEffect } from 'react';
import produce from 'immer';

export default function useStore() {
  const [graphData, setGraphData] = useState({});
  const [sidebarLinks, setSidebarLinks] = useState(null);

  useEffect(() => {
    const requestOptions = {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    };
    fetch('http://localhost:8346/api/available_benchmarks', requestOptions)
      .then(response => response.json())
      .then(data => {
        setSidebarLinks(data);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  const fetchBenchmark = (link) => {
    fetch(`http://localhost:8346/api/${link.benchmark}/${link.ara}/${link.timestamp}`,{method: 'GET', headers: { 'Content-Type': 'application/json' }})
      .then(response => response.json())
      .then(data => {
        setGraphData(
          produce((draft) => {
            // this is hopefully just temporary until the CLI adds this field to benchmarks
            Object.values(data).forEach((graph) => {
              graph.benchmark.timestamp = link.timestamp;
            });
            draft[`${link.benchmark}_${link.ara}_${link.timestamp}`] = data;
          })
        );
      })
      .catch((error) => {
        console.log(error);
      });
  };

  function removeBenchmark(benchmark) {
    setGraphData(
      produce((draft) => {
        delete draft[`${benchmark.benchmark}_${benchmark.ara}_${benchmark.timestamp}`];
      })
    )
  }

  return {
    sidebarLinks,

    fetchBenchmark,
    removeBenchmark,

    graphData,

  };
}
