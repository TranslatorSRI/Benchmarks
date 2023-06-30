import React from 'react';
import './App.scss';
import styles from './App.module.scss';
import Graph from './Components/BenchmarkGraph/BenchmarkGraph';
import Header from './Components/Header/Header';
import Page from './Components/Page/Page';
import StoreContext from './Utilities/StoreContext';
import useStore from './Utilities/useStore';

function App() {
  const store = useStore();

  return (
    <div className={`app`}>
      <Header/>
      <StoreContext.Provider value={store}>
        <Page 
          title="Translator Benchmarks UI" 
        >
          {
            !store.graphData &&
            <h4>Use the sidebar menu on the left to select benchmarks to display.</h4>
          }
          <div className={styles.graphsContainer}>
            {
              Object.values(store.graphData).map((benchmark) => {
                return Object.entries(benchmark).map(([target, graph]) => {
                  return(
                    <Graph
                      key={target}
                      title={target}
                      subtitle={graph.benchmark.timestamp}
                      data={graph}
                    />
                  );
                });
              })
            }
          </div>
        </Page>
      </StoreContext.Provider>
    </div>
  );
}

export default App;
