import React, {useState, useEffect} from 'react';
import './App.scss';
import styles from './App.module.scss';
import Graph from './Components/BenchmarkGraph/BenchmarkGraph';
import Header from './Components/Header/Header';
import Page from './Components/Page/Page';
import exampleBenchmarkList from './Utilities/available_benchmarks_example.json';
import exampleGraphData from './Utilities/benchmark_json_example.json';

function App() {

  const [graphData, setGraphData] = useState(null);
  const [sidebarLinks, setSidebarLinks] = useState(exampleBenchmarkList);
  const [selectedBenchmarks, setSelectedBenchmarks] = useState(null);

  const handleSidebarLinkClick = (link) => {
    console.log(link);
    // fetch(`/${link.benchmark}/${link.target}/${link.timestamp}`,{method: 'GET', headers: { 'Content-Type': 'application/json' }})
    //   .then(response => response.json())
    //   .then(data => {
    //     console.log(data)
    //   })
    //   .catch((error) => {
    //     console.log(error)
    //   });
    setGraphData([exampleGraphData, exampleGraphData, exampleGraphData, exampleGraphData]);
  }
  
  const handleShowBenchmarks = () => {
    
  }


  useEffect(() => {

    const requestOptions = {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    };
    fetch('/available_benchmarks', requestOptions)
      .then(response => response.json())
      .then(data => {
        console.log(data)
      })
      .catch((error) => {
        console.log(error)
      });

  }, [])

  return (
    <div className={`app`}>
      <Header/>
      <Page 
        title="Translator Benchmarks UI" 
        sidebarLinks={sidebarLinks}
        handleSidebarLinkClick={handleSidebarLinkClick}
        handleShowBenchmarks={handleShowBenchmarks}
        >
        {
          !graphData &&
          <h4>Use the sidebar menu on the left to select benchmarks to display.</h4>
        }
        <div className={styles.graphsContainer}>
          {
            graphData &&
            graphData.map((graph, i) => {

              return(
                <Graph 
                  title="Example Graph" 
                  subtitle="Graph Subtitle"
                  data={graph}
                />
              );
            })
          }
        </div>
      </Page>
    </div>
  );
}

export default App;
